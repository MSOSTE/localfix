import json
import time

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

from .forms import ModeratorReportForm, ReportForm, ReportImageForm
from .geocoding import geocode_address, reverse_geocode_coordinates
from .models import Category, Report, ReportImage


def get_report_stats():
    reports = Report.objects.all()
    return {
        "total": reports.count(),
        Report.Status.NEW: reports.filter(status=Report.Status.NEW).count(),
        Report.Status.IN_PROGRESS: reports.filter(status=Report.Status.IN_PROGRESS).count(),
        Report.Status.RESOLVED: reports.filter(status=Report.Status.RESOLVED).count(),
        Report.Status.REJECTED: reports.filter(status=Report.Status.REJECTED).count(),
    }


def serialize_report_for_map(report):
    # Keep map data JSON-safe for Leaflet.
    return {
        "title": report.title,
        "address": report.address,
        "lat": float(report.latitude),
        "lng": float(report.longitude),
        "url": report.get_absolute_url(),
        "status": report.get_status_display(),
        "statusValue": report.status,
        "category": str(report.category.translated_name),
        "categoryId": report.category_id,
        "categoryColor": report.category.color,
    }


def home(request):
    reports = Report.objects.all()
    total_reports = reports.count()
    home_status_labels = {
        Report.Status.NEW: _("New reports"),
        Report.Status.IN_PROGRESS: _("In progress"),
        Report.Status.RESOLVED: _("Resolved reports"),
        Report.Status.REJECTED: _("Rejected reports"),
    }
    status_summary = [
        {"value": value, "label": home_status_labels[value], "count": reports.filter(status=value).count()}
        for value, _label in Report.Status.choices
    ]
    return render(
        request,
        "core/home.html",
        {"status_summary": status_summary, "total_reports": total_reports},
    )


def is_moderator(user):
    return user.is_authenticated and getattr(user.profile, "role", "") == "moderator"


def can_edit_report(user, report):
    return user.is_authenticated and (report.created_by == user or is_moderator(user))


def report_list(request):
    reports = Report.objects.select_related("category", "created_by").prefetch_related("images")
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    mine = request.GET.get("mine") == "1" and request.user.is_authenticated

    if query:
        reports = reports.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query)
        )
    if category_id:
        reports = reports.filter(category_id=category_id)
    if status:
        reports = reports.filter(status=status)
    if mine:
        reports = reports.filter(created_by=request.user)

    paginator = Paginator(reports, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "reports": page_obj,
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "status_choices": Report.Status.choices,
        "selected_category": category_id,
        "selected_status": status,
        "query": query,
        "mine": mine,
        "pagination_query": query_params.urlencode(),
        "live_stats": get_report_stats(),
    }
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # AJAX filters replace only the report cards.
        html = render_to_string("core/_report_results.html", context, request=request)
        return JsonResponse({"html": html})

    return render(request, "core/report_list.html", context)


def report_live_stats(request):
    def event_stream():
        while True:
            # SSE keeps the browser updated without a page refresh.
            yield f"data: {json.dumps(get_report_stats())}\n\n"
            time.sleep(5)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def report_map(request):
    reports = Report.objects.select_related("category").exclude(latitude=None).exclude(longitude=None)
    map_reports = [serialize_report_for_map(report) for report in reports]
    categories = Category.objects.all()
    return render(
        request,
        "core/report_map.html",
        {"map_reports": map_reports, "categories": categories, "status_choices": Report.Status.choices},
    )


def reverse_geocode(request):
    latitude = request.GET.get("lat")
    longitude = request.GET.get("lng")
    address = reverse_geocode_coordinates(latitude, longitude)
    return JsonResponse({"address": address})


def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related("category", "created_by").prefetch_related("images"),
        pk=pk,
    )
    map_reports = []
    if report.latitude is not None and report.longitude is not None:
        map_reports.append(
            {
                **serialize_report_for_map(report),
            }
        )
    return render(
        request,
        "core/report_detail.html",
        {"report": report, "can_edit": can_edit_report(request.user, report), "map_reports": map_reports},
    )


@login_required
def report_create(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        image_form = ReportImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            coordinates = None
            if (report.latitude is None or report.longitude is None) and report.address:
                # Use the address as a fallback when the user did not click the map.
                coordinates = geocode_address(report.address)
            if coordinates:
                report.latitude, report.longitude = coordinates
            report.save()
            for image in image_form.cleaned_data.get("images", []):
                ReportImage.objects.create(report=report, image=image)
            return redirect(report)
    else:
        form = ReportForm()
        image_form = ReportImageForm()

    return render(request, "core/report_form.html", {"form": form, "image_form": image_form, "title": _("Create report")})


@login_required
def report_update(request, pk):
    report = get_object_or_404(Report.objects.prefetch_related("images"), pk=pk)
    if not can_edit_report(request.user, report):
        raise PermissionDenied

    form_class = ModeratorReportForm if is_moderator(request.user) else ReportForm
    if request.method == "POST":
        form = form_class(request.POST, instance=report)
        image_form = ReportImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            report = form.save(commit=False)
            coordinates = None
            if (report.latitude is None or report.longitude is None) and report.address:
                # Keep old reports usable even if coordinates were left empty.
                coordinates = geocode_address(report.address)
            if coordinates:
                report.latitude, report.longitude = coordinates
            report.save()
            image_ids = request.POST.getlist("delete_images")
            if image_ids:
                report.images.filter(id__in=image_ids).delete()
            for image in image_form.cleaned_data.get("images", []):
                ReportImage.objects.create(report=report, image=image)
            return redirect(report)
    else:
        form = form_class(instance=report)
        image_form = ReportImageForm()

    return render(
        request,
        "core/report_form.html",
        {"form": form, "image_form": image_form, "title": _("Edit report"), "report": report},
    )


@login_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if not can_edit_report(request.user, report):
        raise PermissionDenied

    if request.method == "POST":
        report.delete()
        return redirect("report_list")

    return render(request, "core/report_confirm_delete.html", {"report": report})
