"""Planner app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('goals/', views.investment_goals, name='investment_goals'),
    path('goals/<int:goal_id>/', views.investment_goal_detail, name='investment_goal_detail'),
    path('goals/<int:goal_id>/contribute/', views.add_contribution, name='add_contribution'),
    path('goals/<int:goal_id>/projection/', views.goal_projection, name='goal_projection'),
    path('goals/summary/', views.goals_summary, name='goals_summary'),
]
