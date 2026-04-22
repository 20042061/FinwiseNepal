import os
import random
from django.conf import settings

# Try to import OpenAI, but don't fail if it's not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class FinanceAdvisorAI:
    """
    ChatGPT integration for finance advisory with strict finance-focused prompts
    Includes fallback mock responses for development/testing
    """
    
    def __init__(self):
        # Initialize OpenAI client if API key is available
        api_key = getattr(settings, 'OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY'))
        
        # Check if API key is valid (not the placeholder)
        if api_key and api_key != 'your-openai-api-key-here' and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=api_key)
            self.use_mock = False
            print("✅ OpenAI API initialized successfully")
        else:
            self.client = None
            self.use_mock = True
            print("⚠️  No valid OpenAI API key found. Using mock responses for development.")
        
        # System prompt to ensure finance-focused responses
        self.system_prompt = """You are FinWise AI, a professional financial advisor and educator specializing in personal finance, investing, budgeting, savings, retirement planning, tax optimization, insurance, and debt management.

Your responsibilities:
1. Provide accurate, actionable financial advice tailored to the user's situation
2. Educate users about finance concepts in a clear, understandable way
3. Help users make informed financial decisions
4. STRICTLY stay within the finance and education domain
5. If users ask non-finance questions, politely redirect them to finance-related topics

Guidelines:
- Always ask clarifying questions when needed to provide personalized advice
- Consider risk tolerance and financial goals in your recommendations
- Provide disclaimers when appropriate (e.g., "This is general advice, consult a certified financial planner for personalized guidance")
- Use examples and analogies to explain complex financial concepts
- Be encouraging and supportive about the user's financial journey
- Never provide illegal or unethical financial advice

IMPORTANT: You must ONLY discuss finance, investing, economics, personal finance management, and financial education. If asked about other topics, respond with: "I'm specialized in finance and financial education. How can I help you with your financial goals today?"
"""
    
    def get_mock_response(self, messages):
        """
        Generate mock finance responses for development/testing
        """
        if not messages:
            return "Hello! I'm FinWise AI, your financial advisor. How can I help you today?"
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '').lower()
                break
        
        # Mock responses based on keywords
        if any(word in user_message for word in ['save', 'saving', 'savings']):
            responses = [
                "Great question about saving! Here are some effective strategies:\n\n1. **50/30/20 Rule**: Allocate 50% of income to needs, 30% to wants, and 20% to savings\n2. **Automate your savings**: Set up automatic transfers to a savings account\n3. **High-yield savings account**: Look for accounts offering 4-5% APY\n4. **Emergency fund**: Aim for 3-6 months of expenses\n\nWhat's your current monthly income? This will help me provide more personalized advice.",
                "Excellent focus on savings! Let me share some powerful tips:\n\n**Short-term savings (< 1 year):**\n- High-yield savings accounts\n- Money market accounts\n- Short-term CDs\n\n**Medium-term (1-5 years):**\n- Treasury bonds\n- Short-term bond funds\n\n**Long-term (5+ years):**\n- Index funds\n- Retirement accounts (401k, IRA)\n\nWhat are you saving for specifically?"
            ]
        
        elif any(word in user_message for word in ['invest', 'investing', 'stock', 'stocks', 'portfolio']):
            responses = [
                "Investing is a great way to build wealth! Here's a beginner-friendly approach:\n\n1. **Start with index funds**: Low-cost, diversified (e.g., S&P 500 index)\n2. **Dollar-cost averaging**: Invest consistently, regardless of market conditions\n3. **Diversification**: Don't put all eggs in one basket\n4. **Time horizon**: Longer investment periods reduce risk\n\n**Risk levels:**\n- Conservative: 70% bonds, 30% stocks\n- Moderate: 60% stocks, 40% bonds\n- Aggressive: 80% stocks, 20% bonds\n\nWhat's your risk tolerance and investment timeframe?",
                "Smart thinking about investing! Here are key principles:\n\n**For beginners:**\n- Start with target-date retirement funds\n- Consider robo-advisors (Betterment, Wealthfront)\n- Invest in low-cost index funds (Vanguard, Fidelity)\n\n**Asset allocation by age:**\n- 20s-30s: 80-90% stocks, 10-20% bonds\n- 40s-50s: 70-80% stocks, 20-30% bonds\n- 60s+: 50-60% stocks, 40-50% bonds\n\nRemember: This is general advice. Consider consulting a certified financial advisor for personalized guidance.\n\nHow much are you planning to invest monthly?"
            ]
        
        elif any(word in user_message for word in ['budget', 'budgeting', 'expense', 'expenses']):
            responses = [
                "Creating a budget is the foundation of financial success! Here's a simple approach:\n\n**Zero-Based Budgeting:**\n1. List all income sources\n2. List all expenses (fixed & variable)\n3. Income - Expenses = $0 (allocate every dollar)\n\n**Budget categories:**\n- Housing: 25-30%\n- Food: 10-15%\n- Transportation: 10-15%\n- Savings: 20%\n- Utilities: 5-10%\n- Entertainment: 5-10%\n- Other: 15-20%\n\n**Tools to use:**\n- Mint (free)\n- YNAB (You Need A Budget)\n- Personal Capital\n- Simple spreadsheet\n\nWhat's your biggest challenge with budgeting?",
                "Excellent question about budgeting! Let me help you create a solid plan:\n\n**The 50/30/20 Budget:**\n- 50% Needs (rent, utilities, groceries)\n- 30% Wants (entertainment, dining out)\n- 20% Savings & debt payoff\n\n**Track your spending:**\n- Use apps (Mint, Personal Capital)\n- Review bank statements weekly\n- Categorize all expenses\n\n**Cut unnecessary costs:**\n- Cancel unused subscriptions\n- Cook at home more\n- Use cashback credit cards wisely\n\nWhat's your current monthly income and major expenses?"
            ]
        
        elif any(word in user_message for word in ['retire', 'retirement', '401k', 'ira', 'pension']):
            responses = [
                "Retirement planning is crucial! Here's how to get started:\n\n**Retirement accounts:**\n- **401(k)**: Employer-sponsored, often with matching (free money!)\n- **Traditional IRA**: Tax-deductible contributions\n- **Roth IRA**: Tax-free withdrawals in retirement\n\n**How much to save:**\n- Age 30: Save 1x your annual salary\n- Age 40: Save 3x your annual salary\n- Age 50: Save 6x your annual salary\n- Age 60: Save 8x your annual salary\n- Age 67: Save 10x your annual salary\n\n**Rule of thumb:** Save 15-20% of income for retirement\n\n**Compound interest is your friend!**\nStarting at 25: $500/month = $1.4M by 65\nStarting at 35: $500/month = $700K by 65\n\nWhat's your current age and when do you plan to retire?",
                "Great focus on retirement! Let me break it down:\n\n**Priority order:**\n1. Get full employer 401(k) match\n2. Max out Roth IRA ($7,000/year in 2024)\n3. Max out 401(k) ($23,000/year in 2024)\n4. Taxable investment accounts\n\n**Retirement calculation:**\n- Multiply desired annual retirement income by 25\n- Example: Want $60k/year? Need $1.5M saved\n\n**Catch-up contributions (age 50+):**\n- 401(k): Additional $7,500/year\n- IRA: Additional $1,000/year\n\nRemember: Start early, even if it's small amounts!\n\nHow much are you currently saving for retirement?"
            ]
        
        elif any(word in user_message for word in ['debt', 'loan', 'credit card', 'mortgage']):
            responses = [
                "Tackling debt is smart! Here are proven strategies:\n\n**Debt payoff methods:**\n1. **Avalanche**: Pay highest interest rate first (saves most money)\n2. **Snowball**: Pay smallest balance first (builds momentum)\n\n**Credit card debt:**\n- Average APR: 16-24%\n- Pay more than minimum!\n- Consider balance transfer (0% APR for 12-18 months)\n\n**Priority order:**\n1. High-interest credit cards (>15%)\n2. Personal loans\n3. Student loans\n4. Mortgage (lowest priority)\n\n**Avoid new debt:**\n- Use cash/debit for purchases\n- Build emergency fund\n- Live below your means\n\nWhat type of debt are you dealing with and what's the interest rate?",
                "Let's create a debt elimination plan!\n\n**Good debt vs Bad debt:**\n- Good: Mortgage, student loans (< 6% interest)\n- Bad: Credit cards, payday loans (> 15% interest)\n\n**Debt consolidation options:**\n- Personal loan (8-12% APR)\n- Balance transfer credit card (0% intro)\n- Home equity loan (if you have equity)\n\n**Debt-to-Income ratio:**\n- Keep below 36% for financial health\n- Lenders prefer below 28% for mortgages\n\n**Extra payment impact:**\n$10,000 debt at 18% APR:\n- Minimum payment: 13 years, $7,100 interest\n- $50 extra/month: 5 years, $2,400 interest\n\nHow much total debt do you have?"
            ]
        
        else:
            # General finance response
            responses = [
                "I'm FinWise AI, your personal financial advisor! I can help you with:\n\n💰 **Saving & Budgeting**\n- Creating effective budgets\n- Building emergency funds\n- Maximizing savings\n\n📈 **Investing**\n- Stock market basics\n- Portfolio diversification\n- Retirement accounts (401k, IRA)\n\n🏦 **Debt Management**\n- Paying off credit cards\n- Student loans strategies\n- Mortgage optimization\n\n🏖️ **Retirement Planning**\n- How much to save\n- Retirement accounts\n- Compound interest\n\nWhat financial topic would you like to explore?",
                "Hello! I'm here to help with your financial goals. I specialize in:\n\n✅ Personal finance advice\n✅ Investment strategies\n✅ Budget optimization\n✅ Debt reduction\n✅ Retirement planning\n✅ Tax efficiency\n\nTo give you the best advice, could you tell me:\n1. What's your main financial goal right now?\n2. What's your current financial situation?\n3. What specific question can I help you with?\n\nI'm here to help you build a strong financial future!"
            ]
        
        return random.choice(responses)
    
    def get_completion(self, messages, user_profile=None):
        """
        Get AI completion with finance-focused context
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            user_profile: UserProfile object for personalized context
        
        Returns:
            AI response as string
        """
        # Use mock responses if no API key
        if self.use_mock:
            return self.get_mock_response(messages)
        
        # Add user context if available
        context_prompt = self.system_prompt
        if user_profile:
            context = f"\n\nUser Context:\n"
            if user_profile.finance_goal:
                context += f"- Financial Goal: {user_profile.finance_goal}\n"
            context += f"- Risk Tolerance: {user_profile.risk_tolerance}\n"
            context_prompt += context
        
        # Prepare messages for API
        api_messages = [{"role": "system", "content": context_prompt}]
        api_messages.extend(messages)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4 for better finance advice
                messages=api_messages,
                temperature=0.7,
                max_tokens=1500,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to mock if API fails
            return self.get_mock_response(messages)

    def generate_conversation_title(self, first_message):
        """
        Generate a concise title for the conversation based on first message.
        """
        # Use simple keyword-based titles in mock mode
        if self.use_mock:
            message_lower = first_message.lower()
            if any(word in message_lower for word in ['save', 'saving', 'savings']):
                return "Savings Strategies"
            elif any(word in message_lower for word in ['invest', 'investing', 'stock']):
                return "Investment Planning"
            elif any(word in message_lower for word in ['budget', 'budgeting']):
                return "Budget Creation"
            elif any(word in message_lower for word in ['retire', 'retirement']):
                return "Retirement Planning"
            elif any(word in message_lower for word in ['debt', 'loan']):
                return "Debt Management"
            else:
                return "Finance Discussion"

        # Use OpenAI for real titles
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate a short, concise title (max 5 words) for a financial conversation based on the user's first message. Only return the title, nothing else."},
                    {"role": "user", "content": first_message}
                ],
                temperature=0.5,
                max_tokens=20
            )
            return response.choices[0].message.content.strip()
        except:
            return "Finance Discussion"
