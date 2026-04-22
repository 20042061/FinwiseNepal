"""
Auto-Generated Reports Models
------------------------------
Models for generating and storing financial reports including
portfolio summaries, NEPSE analytics, and goal progress reports.
"""

from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):
    """
    Auto-generated financial report for a user.
    """
    REPORT_TYPE_CHOICES = [
        ('portfolio_summary', 'Portfolio Summary'),
        ('nepse_analysis', 'NEPSE Market Analysis'),
        ('goal_progress', 'Goal Progress Report'),
        ('health_assessment', 'Financial Health Assessment'),
        ('monthly_review', 'Monthly Investment Review'),
    ]

    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=300)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    content = models.JSONField(default=dict,
                               help_text="Structured report content as JSON")
    summary = models.TextField(blank=True,
                               help_text="AI-generated executive summary")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        return f"{self.title} ({self.report_type})"
