from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extended user profile for finance advisor"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    finance_goal = models.TextField(blank=True, null=True)
    risk_tolerance = models.CharField(max_length=20, choices=[
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive')
    ], default='moderate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class ChatSession(models.Model):
    """Chat session for organizing conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
    """Individual chat messages"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant')
    ])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

class EducationalResource(models.Model):
    """Finance education resources"""
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=[
        ('investing', 'Investing'),
        ('budgeting', 'Budgeting'),
        ('savings', 'Savings'),
        ('retirement', 'Retirement'),
        ('taxes', 'Taxes'),
        ('insurance', 'Insurance'),
        ('debt', 'Debt Management')
    ])
    content = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
