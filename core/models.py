from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=80, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Report(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("New")
        IN_PROGRESS = "in_progress", _("In progress")
        RESOLVED = "resolved", _("Resolved")
        REJECTED = "rejected", _("Rejected")

    title = models.CharField(_("Title"), max_length=120)
    description = models.TextField(_("Description"))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="reports", verbose_name=_("Category"))
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.NEW)
    address = models.CharField(_("Address"), max_length=180)
    latitude = models.DecimalField(_("Latitude"), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=9, decimal_places=6, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports", verbose_name=_("Created by"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("report_detail", kwargs={"pk": self.pk})


class ReportImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="images", verbose_name=_("Report"))
    image = models.ImageField(_("Photo"), upload_to="reports/")
    uploaded_at = models.DateTimeField(_("Uploaded at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Report image")
        verbose_name_plural = _("Report images")

    def __str__(self):
        return f"Image for {self.report}"
