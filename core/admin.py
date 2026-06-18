from django.contrib import admin

from .models import Category, Report, ReportImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    list_editable = ("description",)
    search_fields = ("name",)


class ReportImageInline(admin.TabularInline):
    model = ReportImage
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "created_by", "created_at")
    list_editable = ("category", "status")
    list_filter = ("status", "category")
    search_fields = ("title", "description", "address")
    inlines = [ReportImageInline]
