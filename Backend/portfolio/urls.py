"""Portfolio app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    # Portfolios
    path('', views.portfolios, name='portfolios'),
    path('<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    
    # Assets
    path('<int:portfolio_id>/assets/', views.add_asset, name='add_asset'),
    path('<int:portfolio_id>/assets/<int:asset_id>/', views.asset_detail, name='asset_detail'),
    
    # Rebalancing
    path('<int:portfolio_id>/rebalance/', views.rebalance_portfolio, name='rebalance_portfolio'),
    path('<int:portfolio_id>/rebalancing-history/', views.rebalancing_history, name='rebalancing_history'),
    
    # Health Scores
    path('health-score/', views.compute_health_score, name='health_score'),
    path('health-score/history/', views.health_score_history, name='health_score_history'),
]
