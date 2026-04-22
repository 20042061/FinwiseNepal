"""Planner Admin Configuration."""
from django.contrib import admin
from .models import InvestmentGoal, GoalContribution


@admin.register(InvestmentGoal)
class InvestmentGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'category', 'target_amount', 'current_amount', 'progress_percent', 'status')
    list_filter = ('category', 'status', 'risk_level')
    search_fields = ('user__username', 'name')
    ordering = ('-created_at',)


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ('goal', 'amount', 'note', 'contributed_at')
    list_filter = ('contributed_at',)
    ordering = ('-contributed_at',)
