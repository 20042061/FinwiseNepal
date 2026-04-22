"""
Reports Views
--------------
API endpoints for auto-generating and managing financial reports.
Reports integrate data from NEPSE analytics, portfolios, goals, and health scores.
"""

from datetime import timedelta, date
from decimal import Decimal

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Report
from .serializers import ReportSerializer, ReportListSerializer
from portfolio.models import Portfolio, PortfolioAsset, HealthScore
from planner.models import InvestmentGoal
from nepse.models import NepseIndex


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reports(request):
    """List all reports for the authenticated user."""
    reports = Report.objects.filter(user=request.user)
    report_type = request.query_params.get('type')
    if report_type:
        reports = reports.filter(report_type=report_type)
    serializer = ReportListSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_detail(request, report_id):
    """Get full report details."""
    try:
        report = Report.objects.get(id=report_id, user=request.user)
    except Report.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ReportSerializer(report).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    Generate a new report of the specified type.
    
    POST body:
        report_type: 'portfolio_summary' | 'nepse_analysis' | 'goal_progress' |
                     'health_assessment' | 'monthly_review'
    """
    report_type = request.data.get('report_type', 'portfolio_summary')
    user = request.user

    generators = {
        'portfolio_summary': _generate_portfolio_report,
        'nepse_analysis': _generate_nepse_report,
        'goal_progress': _generate_goal_report,
        'health_assessment': _generate_health_report,
        'monthly_review': _generate_monthly_review,
    }

    generator = generators.get(report_type)
    if not generator:
        return Response({'error': f'Unknown report type: {report_type}'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        report_data = generator(user)
        report = Report.objects.create(
            user=user,
            title=report_data['title'],
            report_type=report_type,
            content=report_data['content'],
            summary=report_data['summary'],
            status='completed',
        )
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Report generation failed: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report(request, report_id):
    """Delete a report."""
    try:
        report = Report.objects.get(id=report_id, user=request.user)
    except Report.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
    report.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ========== Report Generators ==========

def _generate_portfolio_report(user):
    """Generate a portfolio summary report."""
    portfolios = Portfolio.objects.filter(user=user, is_active=True)
    
    portfolio_data = []
    total_invested = 0
    total_value = 0
    
    for p in portfolios:
        assets_data = []
        for asset in p.assets.all():
            assets_data.append({
                'name': asset.name,
                'type': asset.get_asset_type_display(),
                'invested': float(asset.invested_amount),
                'current_value': float(asset.current_value),
                'return_pct': asset.return_pct,
                'allocation': asset.actual_allocation,
                'target_allocation': float(asset.target_allocation),
            })
        
        portfolio_data.append({
            'name': p.name,
            'total_invested': float(p.total_invested),
            'total_value': float(p.total_value),
            'return_pct': p.total_return_pct,
            'assets': assets_data,
        })
        total_invested += float(p.total_invested)
        total_value += float(p.total_value)

    overall_return = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0

    return {
        'title': f'Portfolio Summary — {date.today().strftime("%B %d, %Y")}',
        'summary': (
            f"Your total portfolio is valued at NPR {total_value:,.2f} with "
            f"NPR {total_invested:,.2f} invested, yielding a {overall_return:.1f}% return. "
            f"You have {len(portfolio_data)} active portfolio(s) with "
            f"{sum(len(p['assets']) for p in portfolio_data)} total assets."
        ),
        'content': {
            'total_invested': total_invested,
            'total_value': total_value,
            'overall_return_pct': round(overall_return, 2),
            'portfolios': portfolio_data,
            'generated_date': date.today().isoformat(),
        }
    }


def _generate_nepse_report(user):
    """Generate NEPSE market analysis report."""
    latest = NepseIndex.objects.first()
    if not latest:
        return {
            'title': 'NEPSE Market Analysis',
            'summary': 'No NEPSE data available for analysis.',
            'content': {'error': 'No data'}
        }

    today = latest.date
    # Get price data for different periods
    def get_change(days):
        past = NepseIndex.objects.filter(date__lte=today - timedelta(days=days)).first()
        if past:
            return round(float((latest.close_price - past.close_price) / past.close_price * 100), 2)
        return 0

    # Monthly price history
    monthly_data = list(
        NepseIndex.objects.filter(date__gte=today - timedelta(days=180))
        .order_by('date')
        .values('date', 'close_price', 'volume')
    )
    monthly_serializable = [
        {'date': str(d['date']), 'close_price': float(d['close_price']),
         'volume': float(d['volume']) if d['volume'] else 0}
        for d in monthly_data
    ]

    return {
        'title': f'NEPSE Market Analysis — {today.strftime("%B %d, %Y")}',
        'summary': (
            f"NEPSE closed at {latest.close_price} on {today}. "
            f"Weekly change: {get_change(7)}%, Monthly: {get_change(30)}%, "
            f"Yearly: {get_change(365)}%."
        ),
        'content': {
            'latest_close': float(latest.close_price),
            'latest_date': str(today),
            'changes': {
                'daily': get_change(1),
                'weekly': get_change(7),
                'monthly': get_change(30),
                'quarterly': get_change(90),
                'yearly': get_change(365),
            },
            'price_history': monthly_serializable[-60:],  # Last 60 data points
            'generated_date': date.today().isoformat(),
        }
    }


def _generate_goal_report(user):
    """Generate goal progress report."""
    goals = InvestmentGoal.objects.filter(user=user)
    goals_data = []
    
    for g in goals:
        goals_data.append({
            'name': g.name,
            'category': g.get_category_display(),
            'target': float(g.target_amount),
            'current': float(g.current_amount),
            'progress': g.progress_percent,
            'status': g.status,
            'target_date': str(g.target_date),
            'monthly_contribution': float(g.monthly_contribution),
        })

    active = [g for g in goals_data if g['status'] == 'active']
    avg_progress = sum(g['progress'] for g in active) / len(active) if active else 0

    return {
        'title': f'Goal Progress Report — {date.today().strftime("%B %d, %Y")}',
        'summary': (
            f"You have {len(active)} active goals with an average progress of {avg_progress:.1f}%. "
            f"Total goals: {len(goals_data)}, Completed: {len([g for g in goals_data if g['status'] == 'completed'])}."
        ),
        'content': {
            'total_goals': len(goals_data),
            'active_goals': len(active),
            'average_progress': round(avg_progress, 1),
            'goals': goals_data,
            'generated_date': date.today().isoformat(),
        }
    }


def _generate_health_report(user):
    """Generate financial health assessment report."""
    latest_score = HealthScore.objects.filter(user=user).first()
    
    if latest_score:
        score_data = {
            'overall': latest_score.overall_score,
            'diversification': latest_score.diversification_score,
            'goal_progress': latest_score.goal_progress_score,
            'savings': latest_score.savings_score,
            'risk': latest_score.risk_score,
            'investment': latest_score.investment_score,
            'insights': latest_score.insights,
            'recommendations': latest_score.recommendations,
        }
        summary = (
            f"Your financial health score is {latest_score.overall_score}/100. "
            f"Strongest area: {'Goal Progress' if latest_score.goal_progress_score >= max(latest_score.diversification_score, latest_score.savings_score) else 'Diversification'}."
        )
    else:
        score_data = {'overall': 0, 'message': 'No health score computed yet'}
        summary = "No financial health score available. Please compute your health score first."

    return {
        'title': f'Financial Health Assessment — {date.today().strftime("%B %d, %Y")}',
        'summary': summary,
        'content': {
            'health_score': score_data,
            'generated_date': date.today().isoformat(),
        }
    }


def _generate_monthly_review(user):
    """Generate comprehensive monthly investment review."""
    portfolio_report = _generate_portfolio_report(user)
    goal_report = _generate_goal_report(user)
    health_report = _generate_health_report(user)

    return {
        'title': f'Monthly Investment Review — {date.today().strftime("%B %Y")}',
        'summary': (
            f"Monthly review: {portfolio_report['summary']} {goal_report['summary']}"
        ),
        'content': {
            'portfolio': portfolio_report['content'],
            'goals': goal_report['content'],
            'health': health_report['content'],
            'generated_date': date.today().isoformat(),
        }
    }
