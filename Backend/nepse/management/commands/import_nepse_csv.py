"""
Management command to import NEPSE CSV data into the database.

Usage:
    python manage.py import_nepse_csv
    python manage.py import_nepse_csv --file path/to/custom.csv
    python manage.py import_nepse_csv --clear  # Clear existing data first

CSV Expected Format:
    Symbol, Date, Open, High, Low, Close, Percent Change, Volume, Turn Over
    NEPSE, 17/04/2026, 2835.22, 2843.57, 2808.02, 2838.4, 0.18%, "7,460,698,098.48", -
"""

import csv
import os
from decimal import Decimal, InvalidOperation
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from nepse.models import NepseIndex


class Command(BaseCommand):
    help = 'Import NEPSE index data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Path to CSV file (default: auto-detect in NEPSE.CSV folder)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing NEPSE data before importing',
        )

    def handle(self, *args, **options):
        csv_file = options['file']

        # Auto-detect CSV file if not specified
        if not csv_file:
            nepse_dir = os.path.join(settings.BASE_DIR, '..', 'NEPSE.CSV')
            if os.path.isdir(nepse_dir):
                csv_files = [f for f in os.listdir(nepse_dir) if f.endswith('.csv')]
                if csv_files:
                    csv_file = os.path.join(nepse_dir, csv_files[0])
                    self.stdout.write(f"Auto-detected CSV: {csv_file}")
                else:
                    raise CommandError("No CSV files found in NEPSE.CSV directory")
            else:
                raise CommandError("NEPSE.CSV directory not found. Use --file to specify path.")

        if not os.path.exists(csv_file):
            raise CommandError(f"File not found: {csv_file}")

        # Clear existing data if requested
        if options['clear']:
            count = NepseIndex.objects.count()
            NepseIndex.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing records"))

        self.stdout.write(f"Importing from: {csv_file}")

        imported = 0
        skipped = 0
        errors = 0

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Parse date (DD/MM/YYYY format)
                    date_str = row.get('Date', '').strip()
                    if not date_str:
                        skipped += 1
                        continue
                    trade_date = datetime.strptime(date_str, '%d/%m/%Y').date()

                    # Skip if already exists
                    if NepseIndex.objects.filter(date=trade_date).exists():
                        skipped += 1
                        continue

                    # Parse symbol
                    symbol = row.get('Symbol', 'NEPSE').strip()

                    # Parse prices
                    open_price = self._parse_decimal(row.get('Open', '0'))
                    high_price = self._parse_decimal(row.get('High', '0'))
                    low_price = self._parse_decimal(row.get('Low', '0'))
                    close_price = self._parse_decimal(row.get('Close', '0'))

                    # Parse percent change (remove % sign)
                    pct_str = row.get('Percent Change', '0').strip().replace('%', '')
                    try:
                        percent_change = Decimal(pct_str) if pct_str and pct_str != '-' else None
                    except InvalidOperation:
                        percent_change = None

                    # Parse volume/turnover (remove commas and quotes)
                    volume_str = row.get('Volume', '') or row.get('Turn Over', '')
                    volume = self._parse_volume(volume_str)

                    # Create the record
                    NepseIndex.objects.create(
                        symbol=symbol,
                        date=trade_date,
                        open_price=open_price,
                        high_price=high_price,
                        low_price=low_price,
                        close_price=close_price,
                        percent_change=percent_change,
                        volume=volume,
                    )
                    imported += 1

                    # Progress indicator
                    if imported % 100 == 0:
                        self.stdout.write(f"  Imported {imported} records...")

                except Exception as e:
                    errors += 1
                    self.stderr.write(f"  Row {row_num}: Error - {str(e)}")

        self.stdout.write(self.style.SUCCESS(
            f"\nImport complete: {imported} imported, {skipped} skipped, {errors} errors"
        ))
        self.stdout.write(f"Total NEPSE records in database: {NepseIndex.objects.count()}")

    def _parse_decimal(self, value):
        """Parse a decimal value, handling commas and special chars."""
        if not value or value.strip() == '-':
            return Decimal('0')
        cleaned = value.strip().replace(',', '').replace('"', '')
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return Decimal('0')

    def _parse_volume(self, value):
        """Parse volume/turnover value with comma formatting."""
        if not value or value.strip() in ('-', ''):
            return None
        cleaned = value.strip().replace(',', '').replace('"', '')
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None
