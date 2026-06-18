from django.urls import path

from .views import (
    home,
    report_create,
    report_delete,
    report_detail,
    report_list,
    report_live_stats,
    report_map,
    report_update,
    reverse_geocode,
)

urlpatterns = [
    # GET: home page
    path("", home, name="home"),
    # GET: report list, AJAX filter
    path("reports/", report_list, name="report_list"),
    # GET: live report statistics with SSE
    path("reports/live-stats/", report_live_stats, name="report_live_stats"),
    # GET: map page
    path("map/", report_map, name="report_map"),
    # GET: coordinates to address
    path("reverse-geocode/", reverse_geocode, name="reverse_geocode"),
    # GET: create form, POST: create report
    path("reports/new/", report_create, name="report_create"),
    # GET: report details
    path("reports/<int:pk>/", report_detail, name="report_detail"),
    # GET: edit form, POST: update report
    path("reports/<int:pk>/edit/", report_update, name="report_update"),
    # GET: delete confirmation, POST: delete report
    path("reports/<int:pk>/delete/", report_delete, name="report_delete"),
]
