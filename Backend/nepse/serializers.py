"""NEPSE Serializers — Transforms NEPSE model data for API responses."""

from rest_framework import serializers
from .models import NepseIndex


class NepseIndexSerializer(serializers.ModelSerializer):
    """Serializer for NEPSE OHLCV index data."""
    class Meta:
        model = NepseIndex
        fields = ('id', 'symbol', 'date', 'open_price', 'high_price',
                  'low_price', 'close_price', 'percent_change', 'volume')

