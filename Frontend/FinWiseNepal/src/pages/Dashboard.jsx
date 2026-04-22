/**
 * Dashboard.jsx — Main analytics dashboard with real data visualization.
 * Shows NEPSE summary, portfolio overview, goals progress, health score,
 * and quick-action cards.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI, nepseAPI, plannerAPI, healthAPI, portfolioAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/Dashboard.css';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [nepse, setNepse] = useState(null);
    const [goalsSummary, setGoalsSummary] = useState(null);
    const [healthScore, setHealthScore] = useState(null);
    const [portfolios, setPortfolios] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        loadAllData();
    }, []);

    const loadAllData = async () => {
        setLoading(true);
        try {
            const results = await Promise.allSettled([
                dashboardAPI.getStats(),
                nepseAPI.getSummary(),
                plannerAPI.getSummary(),
                healthAPI.getHistory(),
                portfolioAPI.getPortfolios(),
            ]);
            if (results[0].status === 'fulfilled') setStats(results[0].value.data);
            if (results[1].status === 'fulfilled') setNepse(results[1].value.data);
            if (results[2].status === 'fulfilled') setGoalsSummary(results[2].value.data);
            if (results[3].status === 'fulfilled' && results[3].value.data.length > 0) {
                setHealthScore(results[3].value.data[0]);
            }
            if (results[4].status === 'fulfilled') setPortfolios(results[4].value.data);
        } catch (err) {
            console.error('Dashboard load error:', err);
        }
        setLoading(false);
    };

    const formatNumber = (num) => {
        if (!num && num !== 0) return '—';
        return Number(num).toLocaleString('en-NP', { maximumFractionDigits: 2 });
    };

    const totalPortfolioValue = portfolios.reduce((sum, p) => sum + (p.total_value || 0), 0);
    const totalReturn = portfolios.reduce((sum, p) => sum + (p.total_return_pct || 0), 0);

    if (loading) {
        return (
            <div className="page-layout">
                <Sidebar />
                <main className="page-content">
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Loading your dashboard...</p>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="dashboard-page">
                {/* Welcome header */}
                <div className="dash-welcome">
                    <div>
                        <h1 className="dash-greeting">
                            Welcome back, {user.first_name || user.username} 👋
                        </h1>
                        <p className="dash-subtitle">
                            Here's your financial overview for today
                        </p>
                    </div>
                    <button className="btn btn-primary" onClick={() => navigate('/chat')}>
                        🤖 Ask AI Advisor
                    </button>
                </div>

                {/* NEPSE Market Summary */}
                {nepse && (
                    <div className="dash-nepse-banner" onClick={() => navigate('/nepse')}>
                        <div className="nepse-main">
                            <span className="nepse-badge">NEPSE Index</span>
                            <span className="nepse-price">{formatNumber(nepse.latest_close)}</span>
                            <span className={`nepse-change ${Number(nepse.daily_change) >= 0 ? 'text-positive' : 'text-negative'}`}>
                                {Number(nepse.daily_change) >= 0 ? '▲' : '▼'} {Math.abs(Number(nepse.daily_change)).toFixed(2)}%
                            </span>
                        </div>
                        <div className="nepse-stats-row">
                            <div className="nepse-mini-stat">
                                <span className="mini-label">Weekly</span>
                                <span className={Number(nepse.weekly_change) >= 0 ? 'text-positive' : 'text-negative'}>
                                    {Number(nepse.weekly_change) > 0 ? '+' : ''}{Number(nepse.weekly_change).toFixed(2)}%
                                </span>
                            </div>
                            <div className="nepse-mini-stat">
                                <span className="mini-label">Monthly</span>
                                <span className={Number(nepse.monthly_change) >= 0 ? 'text-positive' : 'text-negative'}>
                                    {Number(nepse.monthly_change) > 0 ? '+' : ''}{Number(nepse.monthly_change).toFixed(2)}%
                                </span>
                            </div>
                            <div className="nepse-mini-stat">
                                <span className="mini-label">Yearly</span>
                                <span className={Number(nepse.yearly_change) >= 0 ? 'text-positive' : 'text-negative'}>
                                    {Number(nepse.yearly_change) > 0 ? '+' : ''}{Number(nepse.yearly_change).toFixed(2)}%
                                </span>
                            </div>
                            <div className="nepse-mini-stat">
                                <span className="mini-label">52W High</span>
                                <span>{formatNumber(nepse.high_52w)}</span>
                            </div>
                            <div className="nepse-mini-stat">
                                <span className="mini-label">52W Low</span>
                                <span>{formatNumber(nepse.low_52w)}</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Stats Grid */}
                <div className="grid-4 dash-stats-grid">
                    <div className="card dash-stat-card" onClick={() => navigate('/portfolio')}>
                        <div className="dash-stat-icon" style={{ background: 'rgba(99,102,241,0.15)' }}>💼</div>
                        <div className="dash-stat-info">
                            <span className="stat-label">Portfolio Value</span>
                            <span className="stat-value">NPR {formatNumber(totalPortfolioValue)}</span>
                            <span className={`stat-change ${totalReturn >= 0 ? 'text-positive' : 'text-negative'}`}>
                                {totalReturn >= 0 ? '↑' : '↓'} {Math.abs(totalReturn).toFixed(1)}% return
                            </span>
                        </div>
                    </div>

                    <div className="card dash-stat-card" onClick={() => navigate('/planner')}>
                        <div className="dash-stat-icon" style={{ background: 'rgba(16,185,129,0.15)' }}>🎯</div>
                        <div className="dash-stat-info">
                            <span className="stat-label">Active Goals</span>
                            <span className="stat-value">{goalsSummary?.active_goals || 0}</span>
                            <span className="stat-change text-positive">
                                {goalsSummary?.overall_progress?.toFixed(0) || 0}% avg progress
                            </span>
                        </div>
                    </div>

                    <div className="card dash-stat-card" onClick={() => navigate('/health')}>
                        <div className="dash-stat-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>💚</div>
                        <div className="dash-stat-info">
                            <span className="stat-label">Health Score</span>
                            <span className="stat-value">{healthScore?.overall_score || '—'}/100</span>
                            <span className="stat-change">
                                {healthScore?.overall_score >= 70 ? '✨ Great' :
                                 healthScore?.overall_score >= 40 ? '⚡ Good' : '📈 Needs work'}
                            </span>
                        </div>
                    </div>

                    <div className="card dash-stat-card" onClick={() => navigate('/chat')}>
                        <div className="dash-stat-icon" style={{ background: 'rgba(139,92,246,0.15)' }}>💬</div>
                        <div className="dash-stat-info">
                            <span className="stat-label">AI Conversations</span>
                            <span className="stat-value">{stats?.total_conversations || 0}</span>
                            <span className="stat-change">{stats?.total_messages || 0} messages</span>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="dash-actions-grid">
                    <div className="card dash-action-card" onClick={() => navigate('/nepse')}>
                        <span className="action-emoji">📈</span>
                        <h3>NEPSE Analytics</h3>
                        <p>Live market data, charts & technical indicators</p>
                    </div>
                    <div className="card dash-action-card" onClick={() => navigate('/planner')}>
                        <span className="action-emoji">🎯</span>
                        <h3>Goal Planner</h3>
                        <p>Set and track your investment goals</p>
                    </div>
                    <div className="card dash-action-card" onClick={() => navigate('/portfolio')}>
                        <span className="action-emoji">💼</span>
                        <h3>Portfolio</h3>
                        <p>Manage assets & auto-rebalance</p>
                    </div>
                    <div className="card dash-action-card" onClick={() => navigate('/reports')}>
                        <span className="action-emoji">📋</span>
                        <h3>Reports</h3>
                        <p>Auto-generated financial reports</p>
                    </div>
                    <div className="card dash-action-card" onClick={() => navigate('/health')}>
                        <span className="action-emoji">💚</span>
                        <h3>Health Score</h3>
                        <p>Check your financial wellness</p>
                    </div>
                    <div className="card dash-action-card" onClick={() => navigate('/chat')}>
                        <span className="action-emoji">🤖</span>
                        <h3>AI Advisor</h3>
                        <p>Get personalized financial advice</p>
                    </div>
                </div>

                {/* Recent Goals */}
                {goalsSummary && goalsSummary.active_goals > 0 && (
                    <div className="card dash-goals-card">
                        <div className="card-header">
                            <h3 className="card-title">📊 Goals Overview</h3>
                            <button className="btn btn-sm btn-secondary" onClick={() => navigate('/planner')}>
                                View All
                            </button>
                        </div>
                        <div className="dash-goals-stats">
                            <div className="goal-stat">
                                <span className="goal-stat-val">NPR {formatNumber(goalsSummary.total_current_amount)}</span>
                                <span className="goal-stat-label">Saved so far</span>
                            </div>
                            <div className="goal-stat">
                                <span className="goal-stat-val">NPR {formatNumber(goalsSummary.total_target_amount)}</span>
                                <span className="goal-stat-label">Target total</span>
                            </div>
                            <div className="goal-stat">
                                <span className="goal-stat-val">NPR {formatNumber(goalsSummary.total_monthly_contribution)}</span>
                                <span className="goal-stat-label">Monthly savings</span>
                            </div>
                        </div>
                        <div className="progress-bar" style={{ marginTop: 16 }}>
                            <div className="progress-fill" style={{ width: `${goalsSummary.overall_progress || 0}%` }}></div>
                        </div>
                        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
                            {goalsSummary.overall_progress?.toFixed(1)}% of overall goals completed
                        </p>
                    </div>
                )}
            </main>
        </div>
    );
}

export default Dashboard;
