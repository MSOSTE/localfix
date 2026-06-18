from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Report


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        # Django returns one file or a list depending on the upload count.
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleImageField, self).clean(file, initial) for file in files]


class ReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].label_from_instance = lambda category: category.translated_name

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        # Coordinates must be saved as a complete pair.
        if (latitude is None) != (longitude is None):
            raise forms.ValidationError(_("Enter both coordinates or leave both empty."))

        return cleaned_data

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


class ReportImageForm(forms.Form):
    images = MultipleImageField(required=False, label=_("Photos"))


class ModeratorReportForm(ReportForm):
    class Meta(ReportForm.Meta):
        fields = ReportForm.Meta.fields + ("status",)
        labels = {**ReportForm.Meta.labels, "status": _("Status")}
