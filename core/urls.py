from django.urls import path

from .views import home, report_create, report_delete, report_detail, report_list, report_update

urlpatterns = [
    path("", home, name="home"),
    path("reports/", report_list, name="report_list"),
    path("reports/new/", report_create, name="report_create"),
    path("reports/<int:pk>/", report_detail, name="report_detail"),
    path("reports/<int:pk>/edit/", report_update, name="report_update"),
    path("reports/<int:pk>/delete/", report_delete, name="report_delete"),
]
