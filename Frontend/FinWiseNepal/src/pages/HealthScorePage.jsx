/**
 * HealthScorePage.jsx — Financial health score dashboard.
 * Computes and displays a comprehensive financial wellness assessment
 * with component breakdowns, insights, and recommendations.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { healthAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/HealthScorePage.css';

function HealthScorePage() {
    const [score, setScore] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [computing, setComputing] = useState(false);
    const gaugeRef = useRef(null);

    useEffect(() => { loadHistory(); }, []);
    useEffect(() => { if (score) drawGauge(score.overall_score); }, [score]);

    const loadHistory = async () => {
        try {
            const res = await healthAPI.getHistory();
            setHistory(res.data);
            if (res.data.length > 0) setScore(res.data[0]);
        } catch (e) { console.error(e); }
    };

    const computeScore = async () => {
        setComputing(true);
        try {
            const res = await healthAPI.computeScore();
            setScore(res.data);
            loadHistory();
        } catch (e) { console.error(e); }
        setComputing(false);
    };

    const drawGauge = useCallback((value) => {
        const canvas = gaugeRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const size = 220;
        canvas.width = size * dpr;
        canvas.height = size * dpr;
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';
        ctx.scale(dpr, dpr);

        const cx = size / 2, cy = size / 2, r = 85;
        const startAngle = 0.75 * Math.PI;
        const endAngle = 2.25 * Math.PI;
        const valueAngle = startAngle + (value / 100) * (endAngle - startAngle);

        // Background arc
        ctx.beginPath();
        ctx.arc(cx, cy, r, startAngle, endAngle);
        ctx.strokeStyle = 'rgba(255,255,255,0.08)';
        ctx.lineWidth = 14;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Value arc
        const gradient = ctx.createLinearGradient(0, 0, size, 0);
        if (value >= 70) {
            gradient.addColorStop(0, '#10b981');
            gradient.addColorStop(1, '#34d399');
        } else if (value >= 40) {
            gradient.addColorStop(0, '#f59e0b');
            gradient.addColorStop(1, '#fbbf24');
        } else {
            gradient.addColorStop(0, '#ef4444');
            gradient.addColorStop(1, '#f87171');
        }

        ctx.beginPath();
        ctx.arc(cx, cy, r, startAngle, valueAngle);
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 14;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Center text
        ctx.fillStyle = '#f1f5f9';
        ctx.font = 'bold 42px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(value, cx, cy - 8);

        ctx.fillStyle = 'rgba(148,163,184,1)';
        ctx.font = '13px Inter, sans-serif';
        ctx.fillText('out of 100', cx, cy + 22);
    }, []);

    const getGrade = (val) => {
        if (val >= 80) return { label: 'Excellent', color: '#10b981', emoji: '🌟' };
        if (val >= 60) return { label: 'Good', color: '#3b82f6', emoji: '👍' };
        if (val >= 40) return { label: 'Fair', color: '#f59e0b', emoji: '⚡' };
        return { label: 'Needs Work', color: '#ef4444', emoji: '📈' };
    };

    const components = score ? [
        { name: 'Diversification', value: score.diversification_score, icon: '🎨' },
        { name: 'Goal Progress', value: score.goal_progress_score, icon: '🎯' },
        { name: 'Savings', value: score.savings_score, icon: '💰' },
        { name: 'Risk Alignment', value: score.risk_score, icon: '⚖️' },
        { name: 'Investment Returns', value: score.investment_score, icon: '📈' },
    ] : [];

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="health-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">💚 Financial Health Score</h1>
                        <p className="section-subtitle">Comprehensive assessment of your financial wellness</p>
                    </div>
                    <button className="btn btn-primary" onClick={computeScore} disabled={computing}>
                        {computing ? '⏳ Computing...' : '🔄 Refresh Score'}
                    </button>
                </div>

                {!score ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">💚</div>
                        <h3>No health score computed yet</h3>
                        <p>Click "Refresh Score" to compute your financial health assessment</p>
                        <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={computeScore}>
                            Compute Health Score
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Gauge + Grade */}
                        <div className="health-top">
                            <div className="card health-gauge-card">
                                <canvas ref={gaugeRef}></canvas>
                                <div className="health-grade" style={{ color: getGrade(score.overall_score).color }}>
                                    {getGrade(score.overall_score).emoji} {getGrade(score.overall_score).label}
                                </div>
                            </div>

                            {/* Component Breakdown */}
                            <div className="card health-breakdown-card">
                                <h3 className="card-title" style={{ marginBottom: 16 }}>Score Breakdown</h3>
                                {components.map((c, i) => (
                                    <div key={i} className="health-component">
                                        <div className="hc-header">
                                            <span>{c.icon} {c.name}</span>
                                            <span className="hc-value">{c.value}/100</span>
                                        </div>
                                        <div className="progress-bar">
                                            <div className="progress-fill" style={{
                                                width: `${c.value}%`,
                                                background: c.value >= 70 ? 'var(--success)' :
                                                    c.value >= 40 ? 'var(--warning)' : 'var(--danger)',
                                            }}></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Insights & Recommendations */}
                        <div className="health-bottom">
                            <div className="card">
                                <h3 className="card-title" style={{ marginBottom: 16 }}>💡 Insights</h3>
                                {score.insights?.map((insight, i) => (
                                    <div key={i} className="health-insight">
                                        <span className="insight-dot">●</span>
                                        {insight}
                                    </div>
                                ))}
                            </div>
                            <div className="card">
                                <h3 className="card-title" style={{ marginBottom: 16 }}>🎯 Recommendations</h3>
                                {score.recommendations?.map((rec, i) => (
                                    <div key={i} className="health-rec">
                                        <span className="rec-num">{i + 1}</span>
                                        {rec}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}

export default HealthScorePage;
