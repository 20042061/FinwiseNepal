"""Portfolio Serializers — Portfolio, asset, rebalancing, and health score serialization."""

from rest_framework import serializers
from .models import Portfolio, PortfolioAsset, RebalancingLog, HealthScore


class PortfolioAssetSerializer(serializers.ModelSerializer):
    """Serializer for portfolio assets with computed allocation/return data."""
    return_pct = serializers.ReadOnlyField()
    actual_allocation = serializers.ReadOnlyField()
    drift = serializers.ReadOnlyField()

    class Meta:
        model = PortfolioAsset
        fields = ('id', 'name', 'asset_type', 'invested_amount', 'current_value',
                  'target_allocation', 'return_pct', 'actual_allocation', 'drift',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for portfolios with nested assets and summary computations."""
    assets = PortfolioAssetSerializer(many=True, read_only=True)
    total_value = serializers.ReadOnlyField()
    total_invested = serializers.ReadOnlyField()
    total_return_pct = serializers.ReadOnlyField()

    class Meta:
        model = Portfolio
        fields = ('id', 'name', 'description', 'is_active', 'assets',
                  'total_value', 'total_invested', 'total_return_pct',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class PortfolioAssetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating portfolio assets."""
    class Meta:
        model = PortfolioAsset
        fields = ('name', 'asset_type', 'invested_amount', 'current_value',
                  'target_allocation')


class RebalancingLogSerializer(serializers.ModelSerializer):
    """Serializer for rebalancing log entries."""
    asset_name = serializers.CharField(source='asset.name', read_only=True)

    class Meta:
        model = RebalancingLog
        fields = ('id', 'asset', 'asset_name', 'action', 'amount',
                  'current_allocation', 'target_allocation', 'reason',
                  'status', 'created_at')
        read_only_fields = ('id', 'created_at')


class HealthScoreSerializer(serializers.ModelSerializer):
    """Serializer for financial health scores."""
    class Meta:
        model = HealthScore
        fields = ('id', 'overall_score', 'diversification_score',
                  'goal_progress_score', 'savings_score', 'risk_score',
                  'investment_score', 'insights', 'recommendations',
                  'computed_at')
        read_only_fields = ('id', 'computed_at')
