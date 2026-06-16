from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Report, ReportImage


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("title", "category", "description", "address", "latitude", "longitude")
        labels = {
            "title": _("Title"),
            "category": _("Category"),
            "description": _("Description"),
            "address": _("Address"),
            "latitude": _("Latitude"),
            "longitude": _("Longitude"),
        }


class ReportImageForm(forms.ModelForm):
    image = forms.ImageField(required=False, label=_("Photo"))

    class Meta:
        model = ReportImage
        fields = ("image",)


class ModeratorReportForm(ReportForm):
    class Meta(ReportForm.Meta):
        fields = ReportForm.Meta.fields + ("status",)
        labels = {**ReportForm.Meta.labels, "status": _("Status")}
