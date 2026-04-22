"""
Investment Planner Views
------------------------
API endpoints for goal-based investment planning including CRUD operations,
contribution tracking, and AI-powered projections.
"""

import math
from decimal import Decimal
from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import InvestmentGoal, GoalContribution
from .serializers import InvestmentGoalSerializer, InvestmentGoalCreateSerializer, GoalContributionSerializer


# ========== Investment Goals CRUD ==========

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def investment_goals(request):
    """List all goals for the user, or create a new goal."""
    if request.method == 'GET':
        goals = InvestmentGoal.objects.filter(user=request.user)

        # Optional status filter
        goal_status = request.query_params.get('status')
        if goal_status:
            goals = goals.filter(status=goal_status)

        serializer = InvestmentGoalSerializer(goals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InvestmentGoalCreateSerializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save(user=request.user)
            return Response(
                InvestmentGoalSerializer(goal).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def investment_goal_detail(request, goal_id):
    """Get, update, or delete a specific investment goal."""
    try:
        goal = InvestmentGoal.objects.get(id=goal_id, user=request.user)
    except InvestmentGoal.DoesNotExist:
        return Response({'error': 'Goal not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InvestmentGoalSerializer(goal)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InvestmentGoalCreateSerializer(goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(InvestmentGoalSerializer(goal).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========== Goal Contributions ==========

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_contribution(request, goal_id):
    """Add a contribution towards an investment goal."""
    try:
        goal = InvestmentGoal.objects.get(id=goal_id, user=request.user)
    except InvestmentGoal.DoesNotExist:
        return Response({'error': 'Goal not found'}, status=status.HTTP_404_NOT_FOUND)

    amount = request.data.get('amount')
    note = request.data.get('note', '')

    if not amount or float(amount) <= 0:
        return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

    amount = Decimal(str(amount))

    # Create contribution and update goal
    contribution = GoalContribution.objects.create(goal=goal, amount=amount, note=note)
    goal.current_amount += amount
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'
    goal.save()

    return Response({
        'contribution': GoalContributionSerializer(contribution).data,
        'goal': InvestmentGoalSerializer(goal).data,
    }, status=status.HTTP_201_CREATED)


# ========== Goal Projection ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goal_projection(request, goal_id):
    """
    Calculate future value projection for a goal using compound interest.
    Shows month-by-month projected growth to target date.
    """
    try:
        goal = InvestmentGoal.objects.get(id=goal_id, user=request.user)
    except InvestmentGoal.DoesNotExist:
        return Response({'error': 'Goal not found'}, status=status.HTTP_404_NOT_FOUND)

    today = date.today()
    months_remaining = max(
        (goal.target_date.year - today.year) * 12 + (goal.target_date.month - today.month),
        1
    )

    monthly_rate = float(goal.expected_return_rate) / 100 / 12
    monthly_contrib = float(goal.monthly_contribution)
    current = float(goal.current_amount)

    projections = []
    running_total = current

    for month in range(1, months_remaining + 1):
        # Compound existing + new contribution
        running_total = running_total * (1 + monthly_rate) + monthly_contrib
        proj_date = date(
            today.year + (today.month + month - 1) // 12,
            (today.month + month - 1) % 12 + 1,
            1
        )
        projections.append({
            'month': month,
            'date': proj_date.isoformat(),
            'projected_value': round(running_total, 2),
            'target': float(goal.target_amount),
        })

    # Calculate if goal is achievable
    final_value = running_total
    achievable = final_value >= float(goal.target_amount)

    # Required monthly contribution to reach goal
    if monthly_rate > 0:
        fv_current = current * ((1 + monthly_rate) ** months_remaining)
        shortfall = float(goal.target_amount) - fv_current
        if shortfall > 0:
            required_monthly = shortfall * monthly_rate / ((1 + monthly_rate) ** months_remaining - 1)
        else:
            required_monthly = 0
    else:
        required_monthly = max((float(goal.target_amount) - current) / months_remaining, 0)

    return Response({
        'goal_id': goal.id,
        'goal_name': goal.name,
        'current_amount': float(goal.current_amount),
        'target_amount': float(goal.target_amount),
        'months_remaining': months_remaining,
        'projected_final_value': round(final_value, 2),
        'achievable': achievable,
        'required_monthly': round(required_monthly, 2),
        'current_monthly': monthly_contrib,
        'projections': projections,
    })


# ========== Goals Summary ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goals_summary(request):
    """Get aggregate summary of all user's investment goals."""
    goals = InvestmentGoal.objects.filter(user=request.user)

    active_goals = goals.filter(status='active')
    completed_goals = goals.filter(status='completed')

    total_target = sum(float(g.target_amount) for g in active_goals)
    total_current = sum(float(g.current_amount) for g in active_goals)
    total_monthly = sum(float(g.monthly_contribution) for g in active_goals)

    return Response({
        'total_goals': goals.count(),
        'active_goals': active_goals.count(),
        'completed_goals': completed_goals.count(),
        'total_target_amount': round(total_target, 2),
        'total_current_amount': round(total_current, 2),
        'total_monthly_contribution': round(total_monthly, 2),
        'overall_progress': round((total_current / total_target * 100) if total_target > 0 else 0, 1),
    })
