"""Planner Serializers — Investment goal and contribution serialization."""

from rest_framework import serializers
from .models import InvestmentGoal, GoalContribution


class GoalContributionSerializer(serializers.ModelSerializer):
    """Serializer for individual goal contributions."""
    class Meta:
        model = GoalContribution
        fields = ('id', 'amount', 'note', 'contributed_at')
        read_only_fields = ('id', 'contributed_at')


class InvestmentGoalSerializer(serializers.ModelSerializer):
    """Serializer for investment goals with computed fields."""
    progress_percent = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    contributions = GoalContributionSerializer(many=True, read_only=True)

    class Meta:
        model = InvestmentGoal
        fields = ('id', 'name', 'category', 'target_amount', 'current_amount',
                  'monthly_contribution', 'expected_return_rate', 'risk_level',
                  'target_date', 'status', 'notes', 'progress_percent',
                  'remaining_amount', 'contributions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class InvestmentGoalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating investment goals."""
    class Meta:
        model = InvestmentGoal
        fields = ('name', 'category', 'target_amount', 'current_amount',
                  'monthly_contribution', 'expected_return_rate', 'risk_level',
                  'target_date', 'status', 'notes')
