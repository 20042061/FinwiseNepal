"""Reports Serializers — Report model serialization."""

from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for auto-generated reports."""
    class Meta:
        model = Report
        fields = ('id', 'title', 'report_type', 'content', 'summary',
                  'status', 'created_at')
        read_only_fields = ('id', 'created_at')


class ReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for report listings (without full content)."""
    class Meta:
        model = Report
        fields = ('id', 'title', 'report_type', 'summary', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')
