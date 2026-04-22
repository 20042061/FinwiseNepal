/**
 * PortfolioPage.jsx — Portfolio management with AI auto-rebalancing engine.
 * Create portfolios, manage assets, and run AI rebalancing analysis.
 */

import { useState, useEffect } from 'react';
import { portfolioAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/PortfolioPage.css';

const ASSET_TYPES = [
    { value: 'stocks', label: 'Stocks', icon: '📈' },
    { value: 'bonds', label: 'Government Bonds', icon: '🏛️' },
    { value: 'mutual_fund', label: 'Mutual Funds', icon: '📊' },
    { value: 'fixed_deposit', label: 'Fixed Deposits', icon: '🏦' },
    { value: 'gold', label: 'Gold', icon: '🥇' },
    { value: 'real_estate', label: 'Real Estate', icon: '🏠' },
    { value: 'crypto', label: 'Cryptocurrency', icon: '₿' },
    { value: 'savings', label: 'Savings Account', icon: '💰' },
    { value: 'other', label: 'Other', icon: '📌' },
];

function PortfolioPage() {
    const [portfolios, setPortfolios] = useState([]);
    const [selected, setSelected] = useState(null);
    const [showNewPortfolio, setShowNewPortfolio] = useState(false);
    const [showAddAsset, setShowAddAsset] = useState(false);
    const [rebalanceResult, setRebalanceResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [rebalancing, setRebalancing] = useState(false);
    const [newName, setNewName] = useState('');
    const [assetForm, setAssetForm] = useState({
        name: '', asset_type: 'stocks', invested_amount: '', current_value: '', target_allocation: '',
    });

    useEffect(() => { loadPortfolios(); }, []);

    const loadPortfolios = async () => {
        setLoading(true);
        try {
            const res = await portfolioAPI.getPortfolios();
            setPortfolios(res.data);
            if (res.data.length > 0 && !selected) setSelected(res.data[0]);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const createPortfolio = async () => {
        if (!newName.trim()) return;
        try {
            const res = await portfolioAPI.createPortfolio({ name: newName });
            setNewName('');
            setShowNewPortfolio(false);
            await loadPortfolios();
            setSelected(res.data);
        } catch (e) { console.error(e); }
    };

    const addAsset = async (e) => {
        e.preventDefault();
        if (!selected) return;
        try {
            await portfolioAPI.addAsset(selected.id, assetForm);
            setShowAddAsset(false);
            setAssetForm({ name: '', asset_type: 'stocks', invested_amount: '', current_value: '', target_allocation: '' });
            const res = await portfolioAPI.getPortfolio(selected.id);
            setSelected(res.data);
            loadPortfolios();
        } catch (e) { console.error(e); }
    };

    const deleteAsset = async (assetId) => {
        if (!confirm('Remove this asset?')) return;
        try {
            await portfolioAPI.deleteAsset(selected.id, assetId);
            const res = await portfolioAPI.getPortfolio(selected.id);
            setSelected(res.data);
            loadPortfolios();
        } catch (e) { console.error(e); }
    };

    const runRebalance = async () => {
        if (!selected) return;
        setRebalancing(true);
        try {
            const res = await portfolioAPI.rebalance(selected.id);
            setRebalanceResult(res.data);
        } catch (e) { console.error(e); }
        setRebalancing(false);
    };

    const fmt = (n) => Number(n || 0).toLocaleString('en-NP', { maximumFractionDigits: 2 });
    const getType = (v) => ASSET_TYPES.find(t => t.value === v) || ASSET_TYPES[8];

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="portfolio-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">💼 Portfolio Management</h1>
                        <p className="section-subtitle">Manage assets & run AI auto-rebalancing</p>
                    </div>
                    <button className="btn btn-primary" onClick={() => setShowNewPortfolio(true)}>
                        + New Portfolio
                    </button>
                </div>

                {/* Portfolio selector tabs */}
                {portfolios.length > 0 && (
                    <div className="portfolio-tabs">
                        {portfolios.map(p => (
                            <button key={p.id}
                                className={`portfolio-tab ${selected?.id === p.id ? 'active' : ''}`}
                                onClick={() => { setSelected(p); setRebalanceResult(null); }}>
                                {p.name}
                            </button>
                        ))}
                    </div>
                )}

                {loading ? (
                    <div className="loading-container"><div className="loading-spinner"></div></div>
                ) : !selected ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">💼</div>
                        <h3>No portfolios yet</h3>
                        <p>Create your first portfolio to start tracking investments</p>
                    </div>
                ) : (
                    <>
                        {/* Portfolio Summary */}
                        <div className="grid-3 port-summary">
                            <div className="card">
                                <span className="stat-label">Total Invested</span>
                                <span className="stat-value">NPR {fmt(selected.total_invested)}</span>
                            </div>
                            <div className="card">
                                <span className="stat-label">Current Value</span>
                                <span className="stat-value">NPR {fmt(selected.total_value)}</span>
                            </div>
                            <div className="card">
                                <span className="stat-label">Total Return</span>
                                <span className={`stat-value ${selected.total_return_pct >= 0 ? 'text-positive' : 'text-negative'}`}>
                                    {selected.total_return_pct >= 0 ? '+' : ''}{selected.total_return_pct}%
                                </span>
                            </div>
                        </div>

                        {/* Assets */}
                        <div className="card port-assets-card">
                            <div className="card-header">
                                <h3 className="card-title">Assets ({selected.assets?.length || 0})</h3>
                                <div style={{ display: 'flex', gap: 8 }}>
                                    <button className="btn btn-sm btn-primary" onClick={() => setShowAddAsset(true)}>
                                        + Add Asset
                                    </button>
                                    <button className="btn btn-sm btn-secondary" onClick={runRebalance} disabled={rebalancing}>
                                        {rebalancing ? '⏳ Analyzing...' : '🤖 Auto-Rebalance'}
                                    </button>
                                </div>
                            </div>

                            {(!selected.assets || selected.assets.length === 0) ? (
                                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 32 }}>
                                    No assets yet. Add your first investment asset.
                                </p>
                            ) : (
                                <div style={{ overflowX: 'auto' }}>
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Asset</th>
                                                <th>Type</th>
                                                <th>Invested</th>
                                                <th>Current Value</th>
                                                <th>Return</th>
                                                <th>Allocation</th>
                                                <th>Target</th>
                                                <th>Drift</th>
                                                <th></th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {selected.assets.map(a => {
                                                const type = getType(a.asset_type);
                                                return (
                                                    <tr key={a.id}>
                                                        <td><strong>{a.name}</strong></td>
                                                        <td>{type.icon} {type.label}</td>
                                                        <td>NPR {fmt(a.invested_amount)}</td>
                                                        <td>NPR {fmt(a.current_value)}</td>
                                                        <td className={a.return_pct >= 0 ? 'text-positive' : 'text-negative'}>
                                                            {a.return_pct >= 0 ? '+' : ''}{a.return_pct}%
                                                        </td>
                                                        <td>{a.actual_allocation}%</td>
                                                        <td>{a.target_allocation}%</td>
                                                        <td className={Math.abs(a.drift) > 2 ? (a.drift > 0 ? 'text-warning' : 'text-negative') : 'text-positive'}>
                                                            {a.drift > 0 ? '+' : ''}{a.drift}%
                                                        </td>
                                                        <td>
                                                            <button className="btn btn-sm btn-danger" onClick={() => deleteAsset(a.id)}>✕</button>
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>

                        {/* Rebalancing Results */}
                        {rebalanceResult && (
                            <div className="card rebalance-card">
                                <h3 className="card-title" style={{ marginBottom: 16 }}>
                                    🤖 AI Rebalancing Recommendations
                                </h3>
                                <div className="rebalance-summary">
                                    <span className="badge badge-success">{rebalanceResult.summary.holds} Hold</span>
                                    <span className="badge badge-info">{rebalanceResult.summary.buys} Buy</span>
                                    <span className="badge badge-danger">{rebalanceResult.summary.sells} Sell</span>
                                </div>
                                <div className="rebalance-list">
                                    {rebalanceResult.recommendations.map((rec, i) => (
                                        <div key={i} className={`rebalance-item action-${rec.action}`}>
                                            <div className="rebalance-action">
                                                <span className={`action-badge ${rec.action}`}>
                                                    {rec.action === 'buy' ? '🟢 BUY' : rec.action === 'sell' ? '🔴 SELL' : '⚪ HOLD'}
                                                </span>
                                                <strong>{rec.asset_name}</strong>
                                                {rec.amount > 0 && (
                                                    <span className="rebalance-amount">NPR {fmt(rec.amount)}</span>
                                                )}
                                            </div>
                                            <p className="rebalance-reason">{rec.reason}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </>
                )}

                {/* New Portfolio Modal */}
                {showNewPortfolio && (
                    <div className="modal-overlay" onClick={() => setShowNewPortfolio(false)}>
                        <div className="modal-content" onClick={e => e.stopPropagation()}>
                            <h2 style={{ marginBottom: 20 }}>Create Portfolio</h2>
                            <div className="form-group">
                                <label>Portfolio Name</label>
                                <input value={newName} onChange={e => setNewName(e.target.value)}
                                    placeholder="e.g. Long-term Growth" />
                            </div>
                            <div style={{ display: 'flex', gap: 12 }}>
                                <button className="btn btn-primary" onClick={createPortfolio} style={{ flex: 1 }}>Create</button>
                                <button className="btn btn-secondary" onClick={() => setShowNewPortfolio(false)}>Cancel</button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Add Asset Modal */}
                {showAddAsset && (
                    <div className="modal-overlay" onClick={() => setShowAddAsset(false)}>
                        <div className="modal-content" onClick={e => e.stopPropagation()}>
                            <h2 style={{ marginBottom: 20 }}>Add Asset</h2>
                            <form onSubmit={addAsset}>
                                <div className="form-group">
                                    <label>Asset Name</label>
                                    <input required value={assetForm.name}
                                        onChange={e => setAssetForm({...assetForm, name: e.target.value})}
                                        placeholder="e.g. NABIL Bank Stocks" />
                                </div>
                                <div className="form-group">
                                    <label>Asset Type</label>
                                    <select value={assetForm.asset_type}
                                        onChange={e => setAssetForm({...assetForm, asset_type: e.target.value})}>
                                        {ASSET_TYPES.map(t => (
                                            <option key={t.value} value={t.value}>{t.icon} {t.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Invested Amount (NPR)</label>
                                        <input required type="number" min="0" value={assetForm.invested_amount}
                                            onChange={e => setAssetForm({...assetForm, invested_amount: e.target.value})} />
                                    </div>
                                    <div className="form-group">
                                        <label>Current Value (NPR)</label>
                                        <input required type="number" min="0" value={assetForm.current_value}
                                            onChange={e => setAssetForm({...assetForm, current_value: e.target.value})} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>Target Allocation (%)</label>
                                    <input required type="number" min="0" max="100" step="0.5"
                                        value={assetForm.target_allocation}
                                        onChange={e => setAssetForm({...assetForm, target_allocation: e.target.value})} />
                                </div>
                                <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                                    <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Add Asset</button>
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowAddAsset(false)}>Cancel</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default PortfolioPage;
