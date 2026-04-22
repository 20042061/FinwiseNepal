from django.contrib import admin
from .models import UserProfile, ChatSession, ChatMessage, EducationalResource

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'risk_tolerance', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('risk_tolerance', 'created_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    list_filter = ('created_at',)
    ordering = ('-updated_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'timestamp')
    search_fields = ('content',)
    list_filter = ('role', 'timestamp')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(EducationalResource)
class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty_level', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('category', 'difficulty_level', 'created_at')
