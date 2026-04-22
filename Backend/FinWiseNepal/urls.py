"""
FinWiseNepal URL Configuration
-------------------------------
Central URL routing for all API endpoints.
All app URLs are namespaced under /api/ prefix.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('authentication.urls')),      # Auth, Profile, Chat, Education, Dashboard
    path('api/nepse/', include('nepse.urls')),          # NEPSE Analytics
    path('api/planner/', include('planner.urls')),      # Investment Planner
    path('api/portfolio/', include('portfolio.urls')),  # Portfolio & Health Scores
    path('api/reports/', include('reports.urls')),      # Auto-Generated Reports
]
