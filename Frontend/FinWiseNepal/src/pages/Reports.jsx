/**
 * Reports.jsx — Auto-generated financial reports page.
 * Generate and view portfolio summaries, NEPSE analysis, goal progress,
 * health assessments, and monthly reviews.
 */

import { useState, useEffect } from 'react';
import { reportsAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/Reports.css';

const REPORT_TYPES = [
    { value: 'portfolio_summary', label: 'Portfolio Summary', icon: '💼', desc: 'Overview of all your investments' },
    { value: 'nepse_analysis', label: 'NEPSE Analysis', icon: '📈', desc: 'Market performance analysis' },
    { value: 'goal_progress', label: 'Goal Progress', icon: '🎯', desc: 'Investment goals tracking' },
    { value: 'health_assessment', label: 'Health Assessment', icon: '💚', desc: 'Financial wellness check' },
    { value: 'monthly_review', label: 'Monthly Review', icon: '📅', desc: 'Comprehensive monthly summary' },
];

function Reports() {
    const [reports, setReports] = useState([]);
    const [selected, setSelected] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState('');

    useEffect(() => { loadReports(); }, []);

    const loadReports = async () => {
        setLoading(true);
        try {
            const res = await reportsAPI.getReports();
            setReports(res.data);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const generateReport = async (type) => {
        setGenerating(type);
        try {
            const res = await reportsAPI.generateReport({ report_type: type });
            setSelected(res.data);
            loadReports();
        } catch (e) { console.error(e); }
        setGenerating('');
    };

    const viewReport = async (id) => {
        try {
            const res = await reportsAPI.getReport(id);
            setSelected(res.data);
        } catch (e) { console.error(e); }
    };

    const deleteReport = async (id) => {
        if (!confirm('Delete this report?')) return;
        try {
            await reportsAPI.deleteReport(id);
            if (selected?.id === id) setSelected(null);
            loadReports();
        } catch (e) { console.error(e); }
    };

    const renderContent = (content) => {
        if (!content || typeof content !== 'object') return null;
        return (
            <div className="report-content-rendered">
                {Object.entries(content).map(([key, value]) => {
                    if (key === 'generated_date') return null;
                    if (Array.isArray(value)) {
                        return (
                            <div key={key} className="report-section">
                                <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                                {value.length === 0 ? <p className="text-muted">No data</p> :
                                    typeof value[0] === 'object' ? (
                                        <div style={{ overflowX: 'auto' }}>
                                            <table className="data-table">
                                                <thead>
                                                    <tr>{Object.keys(value[0]).map(k => <th key={k}>{k.replace(/_/g, ' ')}</th>)}</tr>
                                                </thead>
                                                <tbody>
                                                    {value.slice(0, 20).map((item, i) => (
                                                        <tr key={i}>{Object.values(item).map((v, j) =>
                                                            <td key={j}>{typeof v === 'number' ? v.toLocaleString() : String(v)}</td>
                                                        )}</tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    ) : value.map((v, i) => <p key={i} className="report-list-item">• {v}</p>)
                                }
                            </div>
                        );
                    }
                    if (typeof value === 'object' && value !== null) {
                        return (
                            <div key={key} className="report-section">
                                <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                                <div className="report-kv-grid">
                                    {Object.entries(value).map(([k, v]) => (
                                        typeof v !== 'object' && (
                                            <div key={k} className="report-kv">
                                                <span className="report-kv-label">{k.replace(/_/g, ' ')}</span>
                                                <span className="report-kv-value">
                                                    {typeof v === 'number' ? v.toLocaleString() : String(v)}
                                                </span>
                                            </div>
                                        )
                                    ))}
                                </div>
                            </div>
                        );
                    }
                    return (
                        <div key={key} className="report-kv">
                            <span className="report-kv-label">{key.replace(/_/g, ' ')}</span>
                            <span className="report-kv-value">
                                {typeof value === 'number' ? value.toLocaleString() : String(value)}
                            </span>
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="reports-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">📋 Auto-Generated Reports</h1>
                        <p className="section-subtitle">Generate comprehensive financial reports with one click</p>
                    </div>
                </div>

                {/* Report Type Cards */}
                <div className="report-types-grid">
                    {REPORT_TYPES.map(rt => (
                        <div key={rt.value} className="card report-type-card"
                            onClick={() => generateReport(rt.value)}>
                            <span className="report-type-icon">{rt.icon}</span>
                            <h3>{rt.label}</h3>
                            <p>{rt.desc}</p>
                            {generating === rt.value && <span className="badge badge-info">Generating...</span>}
                        </div>
                    ))}
                </div>

                <div className="reports-layout">
                    {/* Report List */}
                    <div className="card reports-list-card">
                        <h3 className="card-title" style={{ marginBottom: 16 }}>Generated Reports</h3>
                        {loading ? (
                            <div className="loading-container"><div className="loading-spinner"></div></div>
                        ) : reports.length === 0 ? (
                            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 20 }}>
                                No reports yet. Click a report type above to generate one.
                            </p>
                        ) : (
                            <div className="reports-list">
                                {reports.map(r => (
                                    <div key={r.id}
                                        className={`report-list-item-card ${selected?.id === r.id ? 'active' : ''}`}
                                        onClick={() => viewReport(r.id)}>
                                        <div className="rli-header">
                                            <strong>{r.title}</strong>
                                            <button className="btn btn-sm btn-danger"
                                                onClick={(e) => { e.stopPropagation(); deleteReport(r.id); }}>✕</button>
                                        </div>
                                        <p className="rli-summary">{r.summary?.slice(0, 100)}...</p>
                                        <span className="rli-date">{new Date(r.created_at).toLocaleDateString()}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Report Detail */}
                    <div className="card reports-detail-card">
                        {selected ? (
                            <>
                                <h2 style={{ marginBottom: 8 }}>{selected.title}</h2>
                                <p style={{ color: 'var(--text-secondary)', marginBottom: 20, lineHeight: 1.6 }}>
                                    {selected.summary}
                                </p>
                                {renderContent(selected.content)}
                            </>
                        ) : (
                            <div className="empty-state">
                                <div className="empty-state-icon">📋</div>
                                <p>Select a report to view details</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default Reports;
