"""Reports app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_reports, name='list_reports'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('generate/', views.generate_report, name='generate_report'),
    path('<int:report_id>/delete/', views.delete_report, name='delete_report'),
]
