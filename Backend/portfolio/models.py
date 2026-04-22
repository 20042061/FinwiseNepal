"""
Portfolio Management Models
---------------------------
Manages user portfolios, asset allocations, rebalancing engine,
and financial health score computation.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Portfolio(models.Model):
    """
    A user's investment portfolio containing multiple asset allocations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=200, default='My Portfolio')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def total_value(self):
        """Total current value of all assets in the portfolio."""
        return sum(a.current_value for a in self.assets.all())

    @property
    def total_invested(self):
        """Total amount invested across all assets."""
        return sum(a.invested_amount for a in self.assets.all())

    @property
    def total_return_pct(self):
        """Overall portfolio return percentage."""
        invested = float(self.total_invested)
        if invested <= 0:
            return 0
        return round(((float(self.total_value) - invested) / invested) * 100, 2)


class PortfolioAsset(models.Model):
    """
    Individual asset within a portfolio (stocks, bonds, mutual funds, etc.).
    """
    ASSET_TYPE_CHOICES = [
        ('stocks', 'Stocks'),
        ('bonds', 'Government Bonds'),
        ('mutual_fund', 'Mutual Funds'),
        ('fixed_deposit', 'Fixed Deposits'),
        ('gold', 'Gold'),
        ('real_estate', 'Real Estate'),
        ('crypto', 'Cryptocurrency'),
        ('savings', 'Savings Account'),
        ('other', 'Other'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=200, help_text="Asset name (e.g. 'NABIL Bank Stocks')")
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          validators=[MinValueValidator(0)])
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                        validators=[MinValueValidator(0)])
    # Target allocation is the desired percentage of portfolio
    target_allocation = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                                            help_text="Target allocation percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-current_value']
        verbose_name = 'Portfolio Asset'
        verbose_name_plural = 'Portfolio Assets'

    def __str__(self):
        return f"{self.name} ({self.asset_type})"

    @property
    def return_pct(self):
        """Individual asset return percentage."""
        invested = float(self.invested_amount)
        if invested <= 0:
            return 0
        return round(((float(self.current_value) - invested) / invested) * 100, 2)

    @property
    def actual_allocation(self):
        """Actual allocation as percent of total portfolio value."""
        total = float(self.portfolio.total_value)
        if total <= 0:
            return 0
        return round((float(self.current_value) / total) * 100, 2)

    @property
    def drift(self):
        """Difference between actual and target allocation (rebalancing signal)."""
        return round(self.actual_allocation - float(self.target_allocation), 2)


class RebalancingLog(models.Model):
    """
    Records auto-rebalancing actions and recommendations.
    """
    ACTION_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('hold', 'Hold'),
    ]

    STATUS_CHOICES = [
        ('recommended', 'Recommended'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('executed', 'Executed'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='rebalancing_logs')
    asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE, related_name='rebalancing_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2,
                                 help_text="Suggested rebalance amount in NPR")
    current_allocation = models.DecimalField(max_digits=5, decimal_places=2)
    target_allocation = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField(help_text="AI-generated reasoning for this action")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recommended')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rebalancing Log'
        verbose_name_plural = 'Rebalancing Logs'

    def __str__(self):
        return f"{self.action.upper()} {self.asset.name}: NPR {self.amount}"


class HealthScore(models.Model):
    """
    Financial health score snapshot for a user.
    Computed periodically from portfolio, goals, and financial habits.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_scores')
    overall_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                        help_text="Overall financial health (0-100)")
    # Component scores (each 0-100)
    diversification_score = models.IntegerField(default=0,
                                                 validators=[MinValueValidator(0), MaxValueValidator(100)])
    goal_progress_score = models.IntegerField(default=0,
                                               validators=[MinValueValidator(0), MaxValueValidator(100)])
    savings_score = models.IntegerField(default=0,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    risk_score = models.IntegerField(default=0,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)])
    investment_score = models.IntegerField(default=0,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)])
    # AI-generated insights
    insights = models.JSONField(default=list, help_text="List of AI-generated insight strings")
    recommendations = models.JSONField(default=list, help_text="List of recommended actions")
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-computed_at']
        verbose_name = 'Health Score'
        verbose_name_plural = 'Health Scores'

    def __str__(self):
        return f"{self.user.username}: {self.overall_score}/100 on {self.computed_at.date()}"
