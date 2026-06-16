from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import ModeratorReportForm, ReportForm, ReportImageForm
from .models import Category, Report


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
    reports = Report.objects.select_related("category", "created_by")
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
    }
    return render(request, "core/report_list.html", context)


def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related("category", "created_by").prefetch_related("images"),
        pk=pk,
    )
    return render(request, "core/report_detail.html", {"report": report, "can_edit": can_edit_report(request.user, report)})


@login_required
def report_create(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        image_form = ReportImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            if image_form.cleaned_data.get("image"):
                image = image_form.save(commit=False)
                image.report = report
                image.save()
            messages.success(request, _("Report created successfully."))
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
            report = form.save()
            image_ids = request.POST.getlist("delete_images")
            if image_ids:
                report.images.filter(id__in=image_ids).delete()
            if image_form.cleaned_data.get("image"):
                image = image_form.save(commit=False)
                image.report = report
                image.save()
            messages.success(request, _("Report updated successfully."))
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
        messages.success(request, _("Report deleted successfully."))
        return redirect("report_list")

    return render(request, "core/report_confirm_delete.html", {"report": report})
