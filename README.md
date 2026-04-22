# FinWise Nepal

**AI-Powered Investment Management & NEPSE Analytics Platform**

A full-stack financial advisory platform built for Nepal's investment ecosystem, providing AI-driven insights, NEPSE market analytics, goal-based planning, portfolio management, and comprehensive financial health assessment.

---

## Tech Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| Frontend       | React 19 + Vite                         |
| Backend        | Django 5.1 + Django REST Framework      |
| Database       | PostgreSQL                              |
| Authentication | JWT (SimpleJWT)                         |
| AI Engine      | OpenAI GPT-4o-mini (with mock fallback) |
| Data Source    | NEPSE Alpha CSV Export                  |

## Core Features

1. **User Authentication** — Register, login, JWT token management, profile settings
2. **AI Chat Advisor** — ChatGPT-powered financial advice with conversation history
3. **NEPSE Analytics** — Historical price data, SMA/RSI/volatility technical indicators
4. **Goal-Based Planner** — Investment goals with contribution tracking and projections
5. **Portfolio Management** — Multi-portfolio asset tracking with auto-rebalancing engine
6. **Financial Health Score** — 5-component weighted wellness assessment with insights
7. **Report Generator** — Auto-generated portfolio, NEPSE, goal, and health reports
8. **Financial Education** — Categorized educational resources with difficulty filtering
9. **Dashboard** — Unified overview of all financial metrics and quick actions

## Project Structure

```
FineWiseNepal/
├── Backend/
│   ├── FinWiseNepal/        # Django project settings & URLs
│   ├── authentication/      # Auth, profile, chat, education, dashboard
│   ├── nepse/               # NEPSE index data & analytics
│   ├── planner/             # Goal-based investment planner
│   ├── portfolio/           # Portfolio management & health scores
│   ├── reports/             # Auto-generated financial reports
│   ├── requirements.txt
│   └── manage.py
├── Frontend/FinWiseNepal/
│   └── src/
│       ├── api.js           # Centralized API service (Axios + JWT)
│       ├── App.jsx          # Application router
│       ├── components/      # Shared components (Sidebar)
│       ├── pages/           # All page components
│       └── styles/          # Component-specific CSS
├── NEPSE.CSV/               # NEPSE historical data (CSV)
└── README.md
```

## Quick Start

### Backend
```bash
cd Backend
pip install -r requirements.txt
# Configure PostgreSQL in FinWiseNepal/settings.py
python manage.py migrate
python manage.py import_nepse_csv    # Import NEPSE data
python manage.py shell < seed_education.py  # Seed education content
python manage.py runserver 8001
```

### Frontend
```bash
cd Frontend/FinWiseNepal
npm install
npm run dev
```

## API Endpoints

| Module         | Base URL           | Key Endpoints                          |
| -------------- | ------------------ | -------------------------------------- |
| Auth           | `/api/auth/`       | register, login, token/refresh, me     |
| Profile        | `/api/profile/`    | GET/PUT user profile                   |
| Chat           | `/api/chat/`       | sessions, send messages                |
| Education      | `/api/education/`  | resources (filterable)                 |
| Dashboard      | `/api/dashboard/`  | stats                                  |
| NEPSE          | `/api/nepse/`      | summary, historical, analytics, volume |
| Planner        | `/api/planner/`    | goals CRUD, contribute, projection     |
| Portfolio      | `/api/portfolio/`  | CRUD, assets, rebalance, health-score  |
| Reports        | `/api/reports/`    | list, detail, generate, delete         |
