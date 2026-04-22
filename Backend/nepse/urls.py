"""NEPSE app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.nepse_summary, name='nepse_summary'),
    path('historical/', views.nepse_historical, name='nepse_historical'),
    path('analytics/', views.nepse_analytics, name='nepse_analytics'),
    path('volume/', views.nepse_volume, name='nepse_volume'),
]
