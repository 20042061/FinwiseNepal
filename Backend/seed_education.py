"""
Seed educational resources into the database
Run this with: python manage.py shell < seed_education.py
"""

from authentication.models import EducationalResource

# Clear existing resources (optional)
# EducationalResource.objects.all().delete()

resources = [
    {
        "title": "Getting Started with Investing",
        "category": "investing",
        "difficulty_level": "beginner",
        "content": """
Investing is the act of committing money or capital to an endeavor with the expectation of obtaining an additional income or profit.

Key Concepts:
- Start early to benefit from compound interest
- Diversify your portfolio to reduce risk
- Understand your risk tolerance
- Consider index funds for beginners
- Don't try to time the market

Steps to Start:
1. Build an emergency fund (3-6 months expenses)
2. Pay off high-interest debt
3. Open a brokerage account
4. Start with low-cost index funds
5. Invest regularly (dollar-cost averaging)
        """
    },
    {
        "title": "Understanding Stocks vs Bonds",
        "category": "investing",
        "difficulty_level": "beginner",
        "content": """
Stocks and bonds are two fundamental investment types with different risk-return profiles.

STOCKS:
- Represent ownership in a company
- Higher potential returns
- Higher risk
- Can provide dividends
- Value fluctuates with market

BONDS:
- Loans to companies or governments
- Lower but steadier returns
- Lower risk
- Provide regular interest payments
- More stable value

A balanced portfolio typically contains both stocks and bonds based on your age and risk tolerance.
        """
    },
    {
        "title": "Creating a Monthly Budget",
        "category": "budgeting",
        "difficulty_level": "beginner",
        "content": """
A budget helps you track income and expenses to achieve financial goals.

50/30/20 Rule:
- 50% Needs (rent, food, utilities)
- 30% Wants (entertainment, dining out)
- 20% Savings & Debt Repayment

Steps to Create a Budget:
1. Calculate your monthly income
2. List all fixed expenses
3. Track variable expenses
4. Set realistic spending limits
5. Monitor and adjust regularly

Tools:
- Spreadsheets (Excel, Google Sheets)
- Budgeting apps (Mint, YNAB)
- Bank apps with budgeting features
        """
    },
    {
        "title": "Emergency Fund Essentials",
        "category": "savings",
        "difficulty_level": "beginner",
        "content": """
An emergency fund is money set aside for unexpected expenses or financial emergencies.

Why You Need One:
- Job loss protection
- Medical emergencies
- Car or home repairs
- Reduces stress
- Prevents debt accumulation

How Much to Save:
- Minimum: $1,000 starter emergency fund
- Goal: 3-6 months of expenses
- Self-employed: 6-12 months recommended

Where to Keep It:
- High-yield savings account
- Money market account
- Short-term CD ladder
- NOT in stocks or risky investments
        """
    },
    {
        "title": "Retirement Planning 101",
        "category": "retirement",
        "difficulty_level": "intermediate",
        "content": """
Planning for retirement ensures financial security in your later years.

Retirement Accounts:
- 401(k): Employer-sponsored plan
- IRA: Individual Retirement Account
- Roth IRA: Tax-free withdrawals
- SEP IRA: For self-employed

How Much to Save:
- Rule of thumb: 10-15% of income
- Start early for compound growth
- Take advantage of employer match
- Increase contributions with raises

Retirement Age Considerations:
- Full retirement age: 66-67 for most
- Early withdrawal penalties before 59½
- Required Minimum Distributions at 72
- Social Security benefits strategy
        """
    },
    {
        "title": "Understanding Tax-Advantaged Accounts",
        "category": "taxes",
        "difficulty_level": "intermediate",
        "content": """
Tax-advantaged accounts help you save money on taxes while investing for the future.

Types:
1. Traditional 401(k)/IRA
   - Tax-deductible contributions
   - Tax-deferred growth
   - Taxed upon withdrawal

2. Roth 401(k)/IRA
   - After-tax contributions
   - Tax-free growth
   - Tax-free withdrawals in retirement

3. HSA (Health Savings Account)
   - Triple tax advantage
   - For high-deductible health plans
   - Can be used for retirement

4. 529 Plan
   - Education savings
   - Tax-free growth for education

Choosing the Right Account:
- Consider current vs. future tax bracket
- Maximize employer match first
- Diversify tax treatment
        """
    },
    {
        "title": "Types of Insurance You Need",
        "category": "insurance",
        "difficulty_level": "intermediate",
        "content": """
Insurance protects you and your family from financial disasters.

Essential Insurance Types:

1. Health Insurance
   - Protects against medical costs
   - Often provided by employer
   - Consider deductible vs. premium

2. Life Insurance
   - Term life: Temporary coverage
   - Whole life: Permanent with cash value
   - Needed if others depend on your income

3. Disability Insurance
   - Replaces income if you can't work
   - Often overlooked but crucial
   - Check employer coverage

4. Auto Insurance
   - Legally required in most places
   - Liability, collision, comprehensive

5. Homeowners/Renters Insurance
   - Protects property and belongings
   - Liability coverage included

6. Umbrella Insurance
   - Extra liability protection
   - Recommended for high net worth
        """
    },
    {
        "title": "Debt Management Strategies",
        "category": "debt",
        "difficulty_level": "intermediate",
        "content": """
Effective debt management is crucial for financial health.

Debt Payoff Strategies:

1. Debt Snowball
   - Pay smallest debt first
   - Psychological wins
   - Build momentum

2. Debt Avalanche
   - Pay highest interest first
   - Mathematically optimal
   - Saves most money

3. Debt Consolidation
   - Combine multiple debts
   - Single payment
   - Potentially lower interest

Good Debt vs. Bad Debt:
- Good: Mortgage, student loans (low interest)
- Bad: Credit cards, payday loans (high interest)

Tips:
- Pay more than minimum
- Negotiate lower rates
- Stop accumulating new debt
- Use windfalls for debt payoff
        """
    },
    {
        "title": "Advanced Portfolio Diversification",
        "category": "investing",
        "difficulty_level": "advanced",
        "content": """
Diversification reduces risk by spreading investments across different assets.

Asset Classes:
- Domestic stocks (large, mid, small cap)
- International stocks (developed, emerging)
- Bonds (government, corporate, municipal)
- Real estate (REITs)
- Commodities
- Alternative investments

Diversification Strategies:
1. Across asset classes
2. Within asset classes
3. Geographic diversification
4. Sector diversification
5. Time diversification (dollar-cost averaging)

Modern Portfolio Theory:
- Efficient frontier
- Risk-adjusted returns
- Correlation coefficients
- Rebalancing strategies

Common Mistakes:
- Over-diversification (diminishing returns)
- Home country bias
- Ignoring correlations
- Forgetting to rebalance
        """
    },
    {
        "title": "Understanding Asset Allocation",
        "category": "investing",
        "difficulty_level": "advanced",
        "content": """
Asset allocation is how you divide your portfolio among different asset categories.

Age-Based Rules:
- Rule of 110: 110 - age = % in stocks
- More conservative: 100 - age = % in stocks
- Aggressive: 120 - age = % in stocks

Risk Tolerance Factors:
- Time horizon
- Income stability
- Financial goals
- Risk capacity vs. risk willingness
- Market knowledge

Lifecycle Investing:
- Young: 90% stocks, 10% bonds
- Mid-career: 70% stocks, 30% bonds
- Near retirement: 50% stocks, 50% bonds
- Retired: 40% stocks, 60% bonds

Rebalancing:
- Review quarterly or annually
- Sell winners, buy losers
- Maintain target allocation
- Consider tax implications
        """
    }
]

print("Seeding educational resources...")

for resource_data in resources:
    resource, created = EducationalResource.objects.get_or_create(
        title=resource_data["title"],
        defaults=resource_data
    )
    if created:
        print(f"✓ Created: {resource.title}")
    else:
        print(f"- Already exists: {resource.title}")

print(f"\nTotal resources in database: {EducationalResource.objects.count()}")
print("Seeding complete!")
