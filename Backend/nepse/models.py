"""
NEPSE Data Models
-----------------
Stores historical NEPSE index data imported from CSV files.
Provides data for analytics, charting, and AI-driven insights.
"""

from django.db import models


class NepseIndex(models.Model):
    """
    Historical NEPSE index price data (OHLCV format).
    Each row represents one trading day from the NEPSE CSV export.
    """
    symbol = models.CharField(max_length=20, default='NEPSE', db_index=True,
                              help_text="Index or stock symbol (e.g. NEPSE)")
    date = models.DateField(unique=True, db_index=True,
                            help_text="Trading date")
    open_price = models.DecimalField(max_digits=12, decimal_places=2,
                                     help_text="Opening price")
    high_price = models.DecimalField(max_digits=12, decimal_places=2,
                                     help_text="Highest price of the day")
    low_price = models.DecimalField(max_digits=12, decimal_places=2,
                                    help_text="Lowest price of the day")
    close_price = models.DecimalField(max_digits=12, decimal_places=2,
                                      help_text="Closing price")
    percent_change = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                         help_text="Daily percent change")
    volume = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                  help_text="Trading volume (turnover in NPR)")
    imported_at = models.DateTimeField(auto_now_add=True,
                                       help_text="When this record was imported")

    class Meta:
        ordering = ['-date']
        verbose_name = 'NEPSE Index Data'
        verbose_name_plural = 'NEPSE Index Data'
        indexes = [
            models.Index(fields=['symbol', 'date']),
            models.Index(fields=['date', 'close_price']),
        ]

    def __str__(self):
        return f"{self.symbol} {self.date}: {self.close_price}"
