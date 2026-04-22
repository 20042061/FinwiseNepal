"""
Investment Planner Models
-------------------------
Goal-based investment planner allowing users to set financial targets,
track progress, and receive AI-powered planning recommendations.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class InvestmentGoal(models.Model):
    """
    A user-defined investment goal with target amount, timeline, and strategy.
    """
    GOAL_CATEGORY_CHOICES = [
        ('retirement', 'Retirement'),
        ('education', 'Education Fund'),
        ('home', 'Home Purchase'),
        ('emergency', 'Emergency Fund'),
        ('wealth', 'Wealth Building'),
        ('business', 'Business Investment'),
        ('travel', 'Travel Fund'),
        ('other', 'Other'),
    ]

    RISK_LEVEL_CHOICES = [
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_goals')
    name = models.CharField(max_length=200, help_text="Goal name (e.g. 'Buy a house')")
    category = models.CharField(max_length=20, choices=GOAL_CATEGORY_CHOICES, default='wealth')
    target_amount = models.DecimalField(max_digits=15, decimal_places=2,
                                        validators=[MinValueValidator(1)],
                                        help_text="Target amount in NPR")
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)],
                                         help_text="Current amount saved towards goal")
    monthly_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                                validators=[MinValueValidator(0)],
                                                help_text="Planned monthly contribution in NPR")
    expected_return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0,
                                               validators=[MinValueValidator(0), MaxValueValidator(100)],
                                               help_text="Expected annual return rate (%)")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='moderate')
    target_date = models.DateField(help_text="Target date to achieve the goal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this goal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Investment Goal'
        verbose_name_plural = 'Investment Goals'

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def progress_percent(self):
        """Calculate goal completion percentage."""
        if self.target_amount <= 0:
            return 0
        return min(round(float(self.current_amount / self.target_amount) * 100, 1), 100)

    @property
    def remaining_amount(self):
        """Amount still needed to reach goal."""
        return max(self.target_amount - self.current_amount, 0)


class GoalContribution(models.Model):
    """
    Records individual contributions made towards an investment goal.
    """
    goal = models.ForeignKey(InvestmentGoal, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])
    note = models.CharField(max_length=200, blank=True)
    contributed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-contributed_at']
        verbose_name = 'Goal Contribution'
        verbose_name_plural = 'Goal Contributions'

    def __str__(self):
        return f"NPR {self.amount} → {self.goal.name}"
