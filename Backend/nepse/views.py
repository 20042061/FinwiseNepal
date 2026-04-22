"""
NEPSE Views
-----------
API endpoints for NEPSE index data, analytics, and market summaries.
Provides historical price data, technical indicators, and chart data.
"""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.db.models import Max, Min, Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import NepseIndex
from .serializers import NepseIndexSerializer


# ========== NEPSE Market Summary ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nepse_summary(request):
    """
    Get NEPSE market summary with latest price, changes, and 52-week stats.
    Returns key market indicators for the dashboard overview.
    """
    latest = NepseIndex.objects.first()  # ordered by -date
    if not latest:
        return Response({'error': 'No NEPSE data available. Please import CSV data.'},
                        status=status.HTTP_404_NOT_FOUND)

    today = latest.date
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    week_52_ago = today - timedelta(days=365)

    # Helper to get closest price to a date
    def get_price_near(target_date):
        record = NepseIndex.objects.filter(date__lte=target_date).first()
        return record.close_price if record else latest.close_price

    prev_close = NepseIndex.objects.filter(date__lt=today).first()
    daily_change = Decimal('0')
    if prev_close:
        daily_change = ((latest.close_price - prev_close.close_price) / prev_close.close_price * 100)

    week_price = get_price_near(week_ago)
    weekly_change = ((latest.close_price - week_price) / week_price * 100) if week_price else Decimal('0')

    month_price = get_price_near(month_ago)
    monthly_change = ((latest.close_price - month_price) / month_price * 100) if month_price else Decimal('0')

    year_price = get_price_near(year_ago)
    yearly_change = ((latest.close_price - year_price) / year_price * 100) if year_price else Decimal('0')

    # 52-week high/low
    stats_52w = NepseIndex.objects.filter(
        date__gte=week_52_ago
    ).aggregate(
        high_52w=Max('high_price'),
        low_52w=Min('low_price'),
        avg_volume=Avg('volume')
    )

    return Response({
        'latest_close': latest.close_price,
        'latest_date': latest.date,
        'open_price': latest.open_price,
        'high_price': latest.high_price,
        'low_price': latest.low_price,
        'daily_change': round(daily_change, 4),
        'weekly_change': round(weekly_change, 4),
        'monthly_change': round(monthly_change, 4),
        'yearly_change': round(yearly_change, 4),
        'high_52w': stats_52w['high_52w'],
        'low_52w': stats_52w['low_52w'],
        'avg_volume': stats_52w['avg_volume'],
        'total_records': NepseIndex.objects.count(),
    })


# ========== Historical Price Data ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nepse_historical(request):
    """
    Get historical NEPSE price data with optional date range filtering.
    
    Query params:
        - period: '1m', '3m', '6m', '1y', '2y', 'all' (default: '1y')
        - start_date: YYYY-MM-DD (overrides period)
        - end_date: YYYY-MM-DD (overrides period)
    """
    period = request.query_params.get('period', '1y')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    queryset = NepseIndex.objects.all()

    if start_date and end_date:
        queryset = queryset.filter(date__gte=start_date, date__lte=end_date)
    else:
        latest = NepseIndex.objects.first()
        if latest:
            end = latest.date
            period_map = {
                '1m': timedelta(days=30),
                '3m': timedelta(days=90),
                '6m': timedelta(days=180),
                '1y': timedelta(days=365),
                '2y': timedelta(days=730),
            }
            if period in period_map:
                start = end - period_map[period]
                queryset = queryset.filter(date__gte=start)

    # Return ordered by date ascending for charting
    data = queryset.order_by('date')
    serializer = NepseIndexSerializer(data, many=True)
    return Response(serializer.data)


# ========== Technical Analytics ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nepse_analytics(request):
    """
    Compute and return technical analysis indicators for the NEPSE index.
    Returns SMA (20, 50, 200), RSI(14), daily returns, and volatility.
    """
    period = request.query_params.get('period', '1y')

    # Fetch data
    latest = NepseIndex.objects.first()
    if not latest:
        return Response({'error': 'No NEPSE data available.'}, status=status.HTTP_404_NOT_FOUND)

    end = latest.date
    period_map = {
        '1m': 30, '3m': 90, '6m': 180, '1y': 365, '2y': 730, 'all': 9999,
    }
    days = period_map.get(period, 365)
    start = end - timedelta(days=days)

    # Get enough extra data for computing moving averages
    prices = list(
        NepseIndex.objects.filter(date__gte=start - timedelta(days=250))
        .order_by('date')
        .values_list('date', 'close_price')
    )

    if len(prices) < 2:
        return Response({'error': 'Insufficient data for analytics.'}, status=status.HTTP_400_BAD_REQUEST)

    dates = [p[0] for p in prices]
    closes = [float(p[1]) for p in prices]

    # --- Compute Simple Moving Averages ---
    def compute_sma(values, window):
        sma = []
        for i in range(len(values)):
            if i < window - 1:
                sma.append(None)
            else:
                sma.append(round(sum(values[i - window + 1:i + 1]) / window, 2))
        return sma

    sma_20 = compute_sma(closes, 20)
    sma_50 = compute_sma(closes, 50)
    sma_200 = compute_sma(closes, 200)

    # --- Compute RSI(14) ---
    def compute_rsi(values, window=14):
        rsi = [None] * window
        deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]

        avg_gain = sum(gains[:window]) / window
        avg_loss = sum(losses[:window]) / window

        for i in range(window, len(deltas)):
            avg_gain = (avg_gain * (window - 1) + gains[i]) / window
            avg_loss = (avg_loss * (window - 1) + losses[i]) / window
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(round(100 - (100 / (1 + rs)), 2))
        return rsi

    rsi_14 = compute_rsi(closes)

    # --- Compute Daily Returns ---
    daily_returns = [None]
    for i in range(1, len(closes)):
        ret = ((closes[i] - closes[i - 1]) / closes[i - 1]) * 100
        daily_returns.append(round(ret, 4))

    # --- Compute 30-day Rolling Volatility ---
    volatility = [None] * 30
    for i in range(30, len(daily_returns)):
        window_returns = [r for r in daily_returns[i - 29:i + 1] if r is not None]
        if window_returns:
            mean = sum(window_returns) / len(window_returns)
            variance = sum((r - mean) ** 2 for r in window_returns) / len(window_returns)
            volatility.append(round(variance ** 0.5, 4))
        else:
            volatility.append(None)

    # Filter to requested period
    result = []
    for i, d in enumerate(dates):
        if d >= start:
            result.append({
                'date': d,
                'close': closes[i],
                'sma_20': sma_20[i],
                'sma_50': sma_50[i],
                'sma_200': sma_200[i],
                'rsi_14': rsi_14[i] if i < len(rsi_14) else None,
                'daily_return': daily_returns[i] if i < len(daily_returns) else None,
                'volatility': volatility[i] if i < len(volatility) else None,
            })

    return Response({
        'period': period,
        'data_points': len(result),
        'data': result,
    })


# ========== Volume Analysis ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nepse_volume(request):
    """
    Get volume/turnover data for the NEPSE index.
    Returns date, volume, and close price for correlation analysis.
    """
    period = request.query_params.get('period', '6m')
    latest = NepseIndex.objects.first()
    if not latest:
        return Response({'error': 'No NEPSE data available.'}, status=status.HTTP_404_NOT_FOUND)

    period_map = {'1m': 30, '3m': 90, '6m': 180, '1y': 365, '2y': 730}
    days = period_map.get(period, 180)
    start = latest.date - timedelta(days=days)

    data = NepseIndex.objects.filter(date__gte=start).order_by('date').values(
        'date', 'close_price', 'volume', 'percent_change'
    )

    return Response(list(data))
