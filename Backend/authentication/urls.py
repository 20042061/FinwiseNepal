from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.get_current_user, name='current_user'),
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
    
    # Chat Sessions
    path('chat/sessions/', views.chat_sessions, name='chat_sessions'),
    path('chat/sessions/<int:session_id>/', views.chat_session_detail, name='chat_session_detail'),
    path('chat/sessions/<int:session_id>/send/', views.send_message, name='send_message'),
    
    # Educational Resources
    path('education/resources/', views.educational_resources, name='educational_resources'),
    path('education/resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
]
