/**
 * Education.jsx — Financial education resources page.
 * Browse and filter educational content about finance and investing.
 */

import { useState, useEffect } from 'react';
import { educationAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/Education.css';

const CATEGORIES = [
    { value: '', label: 'All Topics', icon: '📖' },
    { value: 'investing', label: 'Investing', icon: '📈' },
    { value: 'budgeting', label: 'Budgeting', icon: '💰' },
    { value: 'savings', label: 'Savings', icon: '🏦' },
    { value: 'retirement', label: 'Retirement', icon: '🏖️' },
    { value: 'taxes', label: 'Taxes', icon: '📝' },
    { value: 'insurance', label: 'Insurance', icon: '🛡️' },
    { value: 'debt', label: 'Debt Management', icon: '💳' },
];

function Education() {
    const [resources, setResources] = useState([]);
    const [loading, setLoading] = useState(true);
    const [category, setCategory] = useState('');
    const [expanded, setExpanded] = useState(null);

    useEffect(() => { loadResources(); }, [category]);

    const loadResources = async () => {
        setLoading(true);
        try {
            const params = {};
            if (category) params.category = category;
            const response = await educationAPI.getResources(params);
            setResources(response.data);
        } catch (error) {
            console.error('Failed to load resources:', error);
        }
        setLoading(false);
    };

    const getDifficultyBadge = (level) => {
        const map = {
            beginner: { class: 'badge-success', label: '🟢 Beginner' },
            intermediate: { class: 'badge-warning', label: '🟡 Intermediate' },
            advanced: { class: 'badge-danger', label: '🔴 Advanced' },
        };
        return map[level] || { class: 'badge-info', label: level };
    };

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="education-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">📚 Financial Education</h1>
                        <p className="section-subtitle">Learn about finance, investing, and money management</p>
                    </div>
                </div>

                {/* Category Filter */}
                <div className="edu-categories">
                    {CATEGORIES.map(cat => (
                        <button key={cat.value}
                            className={`edu-cat-btn ${category === cat.value ? 'active' : ''}`}
                            onClick={() => setCategory(cat.value)}>
                            {cat.icon} {cat.label}
                        </button>
                    ))}
                </div>

                {loading ? (
                    <div className="loading-container"><div className="loading-spinner"></div></div>
                ) : resources.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">📚</div>
                        <h3>No resources available</h3>
                        <p>Check back soon or try a different category</p>
                    </div>
                ) : (
                    <div className="edu-grid">
                        {resources.map(resource => {
                            const diff = getDifficultyBadge(resource.difficulty_level);
                            return (
                                <div key={resource.id} className="card edu-card"
                                    onClick={() => setExpanded(expanded === resource.id ? null : resource.id)}>
                                    <div className="edu-card-header">
                                        <span className={`badge ${diff.class}`}>{diff.label}</span>
                                        <span className="edu-cat-tag">{resource.category}</span>
                                    </div>
                                    <h3 className="edu-card-title">{resource.title}</h3>
                                    <p className="edu-card-preview">
                                        {expanded === resource.id
                                            ? resource.content
                                            : resource.content?.slice(0, 150) + '...'}
                                    </p>
                                    <span className="edu-read-more">
                                        {expanded === resource.id ? 'Show less ▲' : 'Read more ▼'}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                )}
            </main>
        </div>
    );
}

export default Education;
