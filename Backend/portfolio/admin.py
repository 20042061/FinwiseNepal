"""Portfolio Admin Configuration."""
from django.contrib import admin
from .models import Portfolio, PortfolioAsset, RebalancingLog, HealthScore


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'name')


@admin.register(PortfolioAsset)
class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'name', 'asset_type', 'invested_amount', 'current_value', 'target_allocation')
    list_filter = ('asset_type',)
    search_fields = ('name',)


@admin.register(RebalancingLog)
class RebalancingLogAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'asset', 'action', 'amount', 'status', 'created_at')
    list_filter = ('action', 'status')
    ordering = ('-created_at',)


@admin.register(HealthScore)
class HealthScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'overall_score', 'diversification_score', 'goal_progress_score', 
                    'savings_score', 'risk_score', 'investment_score', 'computed_at')
    list_filter = ('computed_at',)
    search_fields = ('user__username',)
    ordering = ('-computed_at',)
