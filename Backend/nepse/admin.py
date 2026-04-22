"""NEPSE Admin Configuration."""
from django.contrib import admin
from .models import NepseIndex


@admin.register(NepseIndex)
class NepseIndexAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'percent_change')
    list_filter = ('symbol',)
    search_fields = ('symbol',)
    ordering = ('-date',)
    date_hierarchy = 'date'
