/**
 * NepseAnalytics.jsx — NEPSE Index analytics with interactive charts.
 * Displays historical price data, technical indicators, and market stats.
 * Uses a lightweight canvas-based chart since recharts is not installed.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { nepseAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/NepseAnalytics.css';

function NepseAnalytics() {
    const [summary, setSummary] = useState(null);
    const [historical, setHistorical] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [period, setPeriod] = useState('1y');
    const [loading, setLoading] = useState(true);
    const canvasRef = useRef(null);

    useEffect(() => { loadData(); }, [period]);
    useEffect(() => { if (historical.length) drawChart(); }, [historical]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [sumRes, histRes, anaRes] = await Promise.allSettled([
                nepseAPI.getSummary(),
                nepseAPI.getHistorical({ period }),
                nepseAPI.getAnalytics({ period }),
            ]);
            if (sumRes.status === 'fulfilled') setSummary(sumRes.value.data);
            if (histRes.status === 'fulfilled') setHistorical(histRes.value.data || []);
            if (anaRes.status === 'fulfilled') setAnalytics(anaRes.value.data);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const drawChart = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas || !historical.length) return;
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
        const W = rect.width, H = rect.height;
        const pad = { top: 20, right: 20, bottom: 40, left: 70 };

        const closes = historical.map(d => Number(d.close_price));
        const minP = Math.min(...closes) * 0.99;
        const maxP = Math.max(...closes) * 1.01;
        const rangeP = maxP - minP || 1;

        const toX = (i) => pad.left + (i / (closes.length - 1)) * (W - pad.left - pad.right);
        const toY = (v) => pad.top + (1 - (v - minP) / rangeP) * (H - pad.top - pad.bottom);

        // Background
        ctx.fillStyle = '#0f1729';
        ctx.fillRect(0, 0, W, H);

        // Grid lines
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = pad.top + (i / 5) * (H - pad.top - pad.bottom);
            ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(W - pad.right, y); ctx.stroke();
            ctx.fillStyle = 'rgba(255,255,255,0.4)';
            ctx.font = '11px Inter, sans-serif';
            ctx.textAlign = 'right';
            const val = maxP - (i / 5) * rangeP;
            ctx.fillText(val.toFixed(0), pad.left - 8, y + 4);
        }

        // Area fill
        ctx.beginPath();
        ctx.moveTo(toX(0), H - pad.bottom);
        closes.forEach((c, i) => ctx.lineTo(toX(i), toY(c)));
        ctx.lineTo(toX(closes.length - 1), H - pad.bottom);
        ctx.closePath();
        const grad = ctx.createLinearGradient(0, pad.top, 0, H - pad.bottom);
        grad.addColorStop(0, 'rgba(99,102,241,0.25)');
        grad.addColorStop(1, 'rgba(99,102,241,0.01)');
        ctx.fillStyle = grad;
        ctx.fill();

        // Line
        ctx.beginPath();
        closes.forEach((c, i) => { i === 0 ? ctx.moveTo(toX(i), toY(c)) : ctx.lineTo(toX(i), toY(c)); });
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Date labels
        ctx.fillStyle = 'rgba(255,255,255,0.4)';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        const step = Math.max(Math.floor(historical.length / 6), 1);
        for (let i = 0; i < historical.length; i += step) {
            const d = historical[i].date;
            ctx.fillText(d.slice(5), toX(i), H - pad.bottom + 20);
        }
    }, [historical]);

    const fmt = (n) => n != null ? Number(n).toLocaleString('en-NP', { maximumFractionDigits: 2 }) : '—';

    const periods = [
        { key: '1m', label: '1M' }, { key: '3m', label: '3M' }, { key: '6m', label: '6M' },
        { key: '1y', label: '1Y' }, { key: '2y', label: '2Y' }, { key: 'all', label: 'All' },
    ];

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="nepse-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">📈 NEPSE Analytics</h1>
                        <p className="section-subtitle">Nepal Stock Exchange index data & technical analysis</p>
                    </div>
                </div>

                {/* Market Summary Cards */}
                {summary && (
                    <div className="grid-4 nepse-summary-grid">
                        <div className="card nepse-stat-card">
                            <span className="stat-label">Latest Close</span>
                            <span className="stat-value">{fmt(summary.latest_close)}</span>
                            <span className={`stat-change ${Number(summary.daily_change) >= 0 ? 'text-positive' : 'text-negative'}`}>
                                {Number(summary.daily_change) >= 0 ? '▲' : '▼'} {Math.abs(Number(summary.daily_change)).toFixed(2)}% today
                            </span>
                        </div>
                        <div className="card nepse-stat-card">
                            <span className="stat-label">52-Week High</span>
                            <span className="stat-value">{fmt(summary.high_52w)}</span>
                            <span className="stat-change">Peak price in 1 year</span>
                        </div>
                        <div className="card nepse-stat-card">
                            <span className="stat-label">52-Week Low</span>
                            <span className="stat-value">{fmt(summary.low_52w)}</span>
                            <span className="stat-change">Lowest price in 1 year</span>
                        </div>
                        <div className="card nepse-stat-card">
                            <span className="stat-label">Yearly Change</span>
                            <span className={`stat-value ${Number(summary.yearly_change) >= 0 ? 'text-positive' : 'text-negative'}`}>
                                {Number(summary.yearly_change) > 0 ? '+' : ''}{Number(summary.yearly_change).toFixed(2)}%
                            </span>
                            <span className="stat-change">{fmt(summary.total_records)} trading days</span>
                        </div>
                    </div>
                )}

                {/* Chart */}
                <div className="card nepse-chart-card">
                    <div className="chart-header">
                        <h3 className="card-title">Price Chart</h3>
                        <div className="period-tabs">
                            {periods.map(p => (
                                <button key={p.key}
                                    className={`period-tab ${period === p.key ? 'active' : ''}`}
                                    onClick={() => setPeriod(p.key)}>
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    {loading ? (
                        <div className="loading-container"><div className="loading-spinner"></div></div>
                    ) : (
                        <canvas ref={canvasRef} className="nepse-canvas" style={{ width: '100%', height: 400 }}></canvas>
                    )}
                </div>

                {/* Analytics Data Table */}
                {analytics && analytics.data && (
                    <div className="card">
                        <h3 className="card-title" style={{ marginBottom: 16 }}>Technical Indicators (Latest 20 Days)</h3>
                        <div style={{ overflowX: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Close</th>
                                        <th>SMA 20</th>
                                        <th>SMA 50</th>
                                        <th>RSI 14</th>
                                        <th>Daily Return</th>
                                        <th>Volatility</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {analytics.data.slice(-20).reverse().map((row, i) => (
                                        <tr key={i}>
                                            <td>{row.date}</td>
                                            <td>{fmt(row.close)}</td>
                                            <td>{row.sma_20 ? fmt(row.sma_20) : '—'}</td>
                                            <td>{row.sma_50 ? fmt(row.sma_50) : '—'}</td>
                                            <td>
                                                <span className={row.rsi_14 > 70 ? 'text-negative' : row.rsi_14 < 30 ? 'text-positive' : ''}>
                                                    {row.rsi_14 ? row.rsi_14.toFixed(1) : '—'}
                                                </span>
                                            </td>
                                            <td className={row.daily_return >= 0 ? 'text-positive' : 'text-negative'}>
                                                {row.daily_return ? `${row.daily_return > 0 ? '+' : ''}${row.daily_return.toFixed(2)}%` : '—'}
                                            </td>
                                            <td>{row.volatility ? row.volatility.toFixed(3) : '—'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default NepseAnalytics;
