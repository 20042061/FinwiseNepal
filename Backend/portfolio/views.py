"""
Portfolio & Health Score Views
-------------------------------
API endpoints for portfolio management, AI auto-rebalancing engine,
and financial health score computation.
"""

from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Portfolio, PortfolioAsset, RebalancingLog, HealthScore
from .serializers import (
    PortfolioSerializer, PortfolioAssetSerializer, PortfolioAssetCreateSerializer,
    RebalancingLogSerializer, HealthScoreSerializer
)
from planner.models import InvestmentGoal


# ========== Portfolio CRUD ==========

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def portfolios(request):
    """List user's portfolios or create a new one."""
    if request.method == 'GET':
        user_portfolios = Portfolio.objects.filter(user=request.user)
        serializer = PortfolioSerializer(user_portfolios, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        name = request.data.get('name', 'My Portfolio')
        description = request.data.get('description', '')
        portfolio = Portfolio.objects.create(
            user=request.user, name=name, description=description
        )
        return Response(PortfolioSerializer(portfolio).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def portfolio_detail(request, portfolio_id):
    """Get, update, or delete a specific portfolio."""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(PortfolioSerializer(portfolio).data)

    elif request.method == 'PUT':
        portfolio.name = request.data.get('name', portfolio.name)
        portfolio.description = request.data.get('description', portfolio.description)
        portfolio.save()
        return Response(PortfolioSerializer(portfolio).data)

    elif request.method == 'DELETE':
        portfolio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========== Portfolio Assets ==========

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_asset(request, portfolio_id):
    """Add an asset to a portfolio."""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PortfolioAssetCreateSerializer(data=request.data)
    if serializer.is_valid():
        asset = serializer.save(portfolio=portfolio)
        return Response(PortfolioAssetSerializer(asset).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def asset_detail(request, portfolio_id, asset_id):
    """Update or delete a portfolio asset."""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        asset = PortfolioAsset.objects.get(id=asset_id, portfolio=portfolio)
    except (Portfolio.DoesNotExist, PortfolioAsset.DoesNotExist):
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PortfolioAssetCreateSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(PortfolioAssetSerializer(asset).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========== AI Auto-Rebalancing Engine ==========

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rebalance_portfolio(request, portfolio_id):
    """
    AI-powered auto-rebalancing engine.
    Analyzes current allocation vs target allocation and generates
    buy/sell/hold recommendations to bring the portfolio back to target.
    
    Rebalancing logic:
    1. Calculates drift for each asset (actual_alloc - target_alloc)
    2. Assets with drift > threshold need selling
    3. Assets with drift < -threshold need buying
    4. Generates NPR amounts for rebalancing actions
    """
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=status.HTTP_404_NOT_FOUND)

    assets = portfolio.assets.all()
    if not assets:
        return Response({'error': 'Portfolio has no assets'}, status=status.HTTP_400_BAD_REQUEST)

    total_value = float(portfolio.total_value)
    if total_value <= 0:
        return Response({'error': 'Portfolio value must be positive'}, status=status.HTTP_400_BAD_REQUEST)

    # Rebalancing threshold (only rebalance if drift > 2%)
    DRIFT_THRESHOLD = 2.0

    recommendations = []
    for asset in assets:
        drift = asset.drift
        target_alloc = float(asset.target_allocation)
        actual_alloc = asset.actual_allocation

        if abs(drift) < DRIFT_THRESHOLD:
            action = 'hold'
            amount = Decimal('0')
            reason = (
                f"{asset.name} is within acceptable range. "
                f"Current: {actual_alloc}%, Target: {target_alloc}%. "
                f"No action needed."
            )
        elif drift > 0:
            # Overweight — need to sell
            action = 'sell'
            amount = Decimal(str(round(abs(drift) / 100 * total_value, 2)))
            reason = (
                f"{asset.name} is overweight by {abs(drift):.1f}%. "
                f"Current allocation: {actual_alloc}%, Target: {target_alloc}%. "
                f"Consider selling NPR {amount:,.2f} to rebalance. "
                f"This will help reduce risk concentration in {asset.get_asset_type_display()}."
            )
        else:
            # Underweight — need to buy
            action = 'buy'
            amount = Decimal(str(round(abs(drift) / 100 * total_value, 2)))
            reason = (
                f"{asset.name} is underweight by {abs(drift):.1f}%. "
                f"Current allocation: {actual_alloc}%, Target: {target_alloc}%. "
                f"Consider investing NPR {amount:,.2f} more. "
                f"Increasing {asset.get_asset_type_display()} exposure improves diversification."
            )

        # Log the rebalancing recommendation
        log = RebalancingLog.objects.create(
            portfolio=portfolio,
            asset=asset,
            action=action,
            amount=amount,
            current_allocation=Decimal(str(actual_alloc)),
            target_allocation=Decimal(str(target_alloc)),
            reason=reason,
        )

        recommendations.append(RebalancingLogSerializer(log).data)

    return Response({
        'portfolio_id': portfolio.id,
        'portfolio_name': portfolio.name,
        'total_value': total_value,
        'recommendations': recommendations,
        'summary': {
            'buys': len([r for r in recommendations if r['action'] == 'buy']),
            'sells': len([r for r in recommendations if r['action'] == 'sell']),
            'holds': len([r for r in recommendations if r['action'] == 'hold']),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rebalancing_history(request, portfolio_id):
    """Get rebalancing recommendation history for a portfolio."""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=status.HTTP_404_NOT_FOUND)

    logs = RebalancingLog.objects.filter(portfolio=portfolio)[:50]
    serializer = RebalancingLogSerializer(logs, many=True)
    return Response(serializer.data)


# ========== Financial Health Score ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compute_health_score(request):
    """
    Compute and return the user's financial health score.
    
    Scoring algorithm:
    1. Diversification Score (0-100): Based on portfolio asset type variety
    2. Goal Progress Score (0-100): Based on avg goal completion %
    3. Savings Score (0-100): Based on monthly contributions vs targets
    4. Risk Score (0-100): Based on portfolio risk alignment
    5. Investment Score (0-100): Based on portfolio returns
    
    Overall = weighted average of components
    """
    user = request.user

    # --- 1. Diversification Score ---
    portfolios_qs = Portfolio.objects.filter(user=user, is_active=True)
    all_assets = PortfolioAsset.objects.filter(portfolio__in=portfolios_qs)
    unique_types = all_assets.values_list('asset_type', flat=True).distinct().count()

    # More asset types = better diversification (max 8 types)
    diversification_score = min(int((unique_types / 5) * 100), 100) if unique_types > 0 else 20

    # --- 2. Goal Progress Score ---
    goals = InvestmentGoal.objects.filter(user=user, status='active')
    if goals.exists():
        avg_progress = sum(g.progress_percent for g in goals) / goals.count()
        goal_progress_score = min(int(avg_progress), 100)
    else:
        goal_progress_score = 30  # Baseline score for having no goals

    # --- 3. Savings Score ---
    total_monthly = sum(float(g.monthly_contribution) for g in goals)
    if total_monthly >= 10000:
        savings_score = 90
    elif total_monthly >= 5000:
        savings_score = 70
    elif total_monthly >= 1000:
        savings_score = 50
    else:
        savings_score = 25

    # --- 4. Risk Score ---
    # Check if portfolio risk matches user's risk tolerance
    try:
        profile = user.profile
        risk_preference = profile.risk_tolerance
    except Exception:
        risk_preference = 'moderate'

    total_value = sum(float(p.total_value) for p in portfolios_qs)
    stock_value = sum(
        float(a.current_value) for a in all_assets if a.asset_type in ('stocks', 'crypto')
    )
    stock_pct = (stock_value / total_value * 100) if total_value > 0 else 0

    # Score based on risk alignment
    risk_ranges = {
        'conservative': (0, 30),
        'moderate': (20, 60),
        'aggressive': (40, 90),
    }
    low, high = risk_ranges.get(risk_preference, (20, 60))
    if low <= stock_pct <= high:
        risk_score = 85
    elif abs(stock_pct - (low + high) / 2) < 20:
        risk_score = 60
    else:
        risk_score = 35

    # --- 5. Investment Score ---
    total_invested = sum(float(p.total_invested) for p in portfolios_qs)
    total_current = sum(float(p.total_value) for p in portfolios_qs)
    if total_invested > 0:
        overall_return = ((total_current - total_invested) / total_invested) * 100
        if overall_return > 15:
            investment_score = 95
        elif overall_return > 10:
            investment_score = 80
        elif overall_return > 5:
            investment_score = 65
        elif overall_return > 0:
            investment_score = 50
        else:
            investment_score = 30
    else:
        investment_score = 20

    # --- Overall Score (weighted average) ---
    weights = {
        'diversification': 0.20,
        'goal_progress': 0.25,
        'savings': 0.20,
        'risk': 0.15,
        'investment': 0.20,
    }
    overall = int(
        diversification_score * weights['diversification'] +
        goal_progress_score * weights['goal_progress'] +
        savings_score * weights['savings'] +
        risk_score * weights['risk'] +
        investment_score * weights['investment']
    )

    # --- Generate Insights ---
    insights = []
    if diversification_score < 50:
        insights.append("Your portfolio lacks diversification. Consider adding different asset types.")
    if goal_progress_score < 40:
        insights.append("You're behind on your investment goals. Consider increasing contributions.")
    if savings_score < 50:
        insights.append("Your monthly savings could be improved. Aim for at least NPR 5,000/month.")
    if risk_score < 50:
        insights.append("Your portfolio risk doesn't align with your risk tolerance. Consider rebalancing.")
    if investment_score > 70:
        insights.append("Great investment returns! Your portfolio is performing well.")
    if not insights:
        insights.append("Your finances are in good shape! Keep up the disciplined approach.")

    # --- Generate Recommendations ---
    recommendations = []
    if diversification_score < 60:
        recommendations.append("Add mutual funds or bonds to diversify your portfolio.")
    if goal_progress_score < 50:
        recommendations.append("Set up automatic monthly contributions to stay on track.")
    if savings_score < 50:
        recommendations.append("Create a budget to identify areas where you can save more.")
    if not portfolios_qs.exists():
        recommendations.append("Create your first portfolio to start tracking investments.")
    if not goals.exists():
        recommendations.append("Set financial goals to give your investments direction.")

    # Save the health score
    health = HealthScore.objects.create(
        user=user,
        overall_score=overall,
        diversification_score=diversification_score,
        goal_progress_score=goal_progress_score,
        savings_score=savings_score,
        risk_score=risk_score,
        investment_score=investment_score,
        insights=insights,
        recommendations=recommendations,
    )

    return Response(HealthScoreSerializer(health).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_score_history(request):
    """Get historical health scores for trend visualization."""
    scores = HealthScore.objects.filter(user=request.user)[:30]
    serializer = HealthScoreSerializer(scores, many=True)
    return Response(serializer.data)
