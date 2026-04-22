/**
 * InvestmentPlanner.jsx — Goal-based investment planner.
 * Create, track, and manage investment goals with contributions and projections.
 */

import { useState, useEffect } from 'react';
import { plannerAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/InvestmentPlanner.css';

function InvestmentPlanner() {
    const [goals, setGoals] = useState([]);
    const [summary, setSummary] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [showContrib, setShowContrib] = useState(null);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({
        name: '', category: 'wealth', target_amount: '', current_amount: '0',
        monthly_contribution: '', expected_return_rate: '10', risk_level: 'moderate',
        target_date: '', notes: '',
    });
    const [contribAmount, setContribAmount] = useState('');
    const [contribNote, setContribNote] = useState('');

    useEffect(() => { loadData(); }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [goalsRes, sumRes] = await Promise.all([
                plannerAPI.getGoals(),
                plannerAPI.getSummary(),
            ]);
            setGoals(goalsRes.data);
            setSummary(sumRes.data);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await plannerAPI.createGoal(form);
            setShowModal(false);
            setForm({ name: '', category: 'wealth', target_amount: '', current_amount: '0',
                monthly_contribution: '', expected_return_rate: '10', risk_level: 'moderate',
                target_date: '', notes: '' });
            loadData();
        } catch (e) { console.error(e); }
    };

    const handleContribute = async (goalId) => {
        if (!contribAmount || Number(contribAmount) <= 0) return;
        try {
            await plannerAPI.addContribution(goalId, { amount: contribAmount, note: contribNote });
            setShowContrib(null);
            setContribAmount('');
            setContribNote('');
            loadData();
        } catch (e) { console.error(e); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this goal?')) return;
        try { await plannerAPI.deleteGoal(id); loadData(); } catch (e) { console.error(e); }
    };

    const fmt = (n) => Number(n || 0).toLocaleString('en-NP', { maximumFractionDigits: 0 });

    const categories = [
        { value: 'retirement', label: '🏖️ Retirement', color: '#f59e0b' },
        { value: 'education', label: '🎓 Education', color: '#3b82f6' },
        { value: 'home', label: '🏠 Home', color: '#10b981' },
        { value: 'emergency', label: '🚨 Emergency', color: '#ef4444' },
        { value: 'wealth', label: '💎 Wealth', color: '#8b5cf6' },
        { value: 'business', label: '🏢 Business', color: '#6366f1' },
        { value: 'travel', label: '✈️ Travel', color: '#ec4899' },
        { value: 'other', label: '📌 Other', color: '#64748b' },
    ];

    const getCat = (val) => categories.find(c => c.value === val) || categories[7];

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="planner-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">🎯 Investment Planner</h1>
                        <p className="section-subtitle">Set goals, track progress, and stay on path</p>
                    </div>
                    <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                        + New Goal
                    </button>
                </div>

                {/* Summary Cards */}
                {summary && (
                    <div className="grid-4 planner-summary">
                        <div className="card">
                            <span className="stat-label">Total Goals</span>
                            <span className="stat-value">{summary.total_goals}</span>
                        </div>
                        <div className="card">
                            <span className="stat-label">Total Saved</span>
                            <span className="stat-value">NPR {fmt(summary.total_current_amount)}</span>
                        </div>
                        <div className="card">
                            <span className="stat-label">Target Amount</span>
                            <span className="stat-value">NPR {fmt(summary.total_target_amount)}</span>
                        </div>
                        <div className="card">
                            <span className="stat-label">Monthly Savings</span>
                            <span className="stat-value">NPR {fmt(summary.total_monthly_contribution)}</span>
                        </div>
                    </div>
                )}

                {/* Goals List */}
                {loading ? (
                    <div className="loading-container"><div className="loading-spinner"></div></div>
                ) : goals.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">🎯</div>
                        <h3>No investment goals yet</h3>
                        <p>Create your first goal to start planning your financial future</p>
                        <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setShowModal(true)}>
                            Create Goal
                        </button>
                    </div>
                ) : (
                    <div className="goals-grid">
                        {goals.map(goal => {
                            const cat = getCat(goal.category);
                            return (
                                <div key={goal.id} className="card goal-card">
                                    <div className="goal-header">
                                        <span className="goal-category" style={{ background: cat.color + '20', color: cat.color }}>
                                            {cat.label}
                                        </span>
                                        <span className={`badge ${goal.status === 'active' ? 'badge-success' : goal.status === 'completed' ? 'badge-info' : 'badge-warning'}`}>
                                            {goal.status}
                                        </span>
                                    </div>
                                    <h3 className="goal-name">{goal.name}</h3>
                                    <div className="goal-amounts">
                                        <span>NPR {fmt(goal.current_amount)} <span className="text-muted">/ {fmt(goal.target_amount)}</span></span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{
                                            width: `${goal.progress_percent}%`,
                                            background: goal.progress_percent >= 100 ? 'var(--success)' : 'var(--accent-gradient)'
                                        }}></div>
                                    </div>
                                    <span className="goal-progress-text">{goal.progress_percent}% complete</span>
                                    <div className="goal-meta">
                                        <span>Monthly: NPR {fmt(goal.monthly_contribution)}</span>
                                        <span>Target: {goal.target_date}</span>
                                    </div>
                                    <div className="goal-actions">
                                        <button className="btn btn-sm btn-primary" onClick={() => setShowContrib(goal.id)}>
                                            + Contribute
                                        </button>
                                        <button className="btn btn-sm btn-danger" onClick={() => handleDelete(goal.id)}>
                                            Delete
                                        </button>
                                    </div>

                                    {/* Contribution inline form */}
                                    {showContrib === goal.id && (
                                        <div className="contrib-form">
                                            <input type="number" placeholder="Amount (NPR)" value={contribAmount}
                                                onChange={e => setContribAmount(e.target.value)} />
                                            <input type="text" placeholder="Note (optional)" value={contribNote}
                                                onChange={e => setContribNote(e.target.value)} />
                                            <div className="contrib-btns">
                                                <button className="btn btn-sm btn-success" onClick={() => handleContribute(goal.id)}>Save</button>
                                                <button className="btn btn-sm btn-secondary" onClick={() => setShowContrib(null)}>Cancel</button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Create Goal Modal */}
                {showModal && (
                    <div className="modal-overlay" onClick={() => setShowModal(false)}>
                        <div className="modal-content" onClick={e => e.stopPropagation()}>
                            <h2 style={{ marginBottom: 20 }}>Create Investment Goal</h2>
                            <form onSubmit={handleCreate}>
                                <div className="form-group">
                                    <label>Goal Name</label>
                                    <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                                        placeholder="e.g. Buy a house" />
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Category</label>
                                        <select value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                                            {categories.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Risk Level</label>
                                        <select value={form.risk_level} onChange={e => setForm({...form, risk_level: e.target.value})}>
                                            <option value="conservative">Conservative</option>
                                            <option value="moderate">Moderate</option>
                                            <option value="aggressive">Aggressive</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Target Amount (NPR)</label>
                                        <input required type="number" min="1" value={form.target_amount}
                                            onChange={e => setForm({...form, target_amount: e.target.value})} />
                                    </div>
                                    <div className="form-group">
                                        <label>Current Savings (NPR)</label>
                                        <input type="number" min="0" value={form.current_amount}
                                            onChange={e => setForm({...form, current_amount: e.target.value})} />
                                    </div>
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Monthly Contribution (NPR)</label>
                                        <input required type="number" min="0" value={form.monthly_contribution}
                                            onChange={e => setForm({...form, monthly_contribution: e.target.value})} />
                                    </div>
                                    <div className="form-group">
                                        <label>Expected Return (%/yr)</label>
                                        <input type="number" min="0" max="50" step="0.5" value={form.expected_return_rate}
                                            onChange={e => setForm({...form, expected_return_rate: e.target.value})} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>Target Date</label>
                                    <input required type="date" value={form.target_date}
                                        onChange={e => setForm({...form, target_date: e.target.value})} />
                                </div>
                                <div className="form-group">
                                    <label>Notes</label>
                                    <textarea rows="2" value={form.notes}
                                        onChange={e => setForm({...form, notes: e.target.value})} placeholder="Optional notes..." />
                                </div>
                                <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                                    <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Create Goal</button>
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default InvestmentPlanner;
