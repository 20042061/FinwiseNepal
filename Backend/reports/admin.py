"""Reports Admin Configuration."""
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'report_type', 'status', 'created_at')
    list_filter = ('report_type', 'status')
    search_fields = ('user__username', 'title')
    ordering = ('-created_at',)
