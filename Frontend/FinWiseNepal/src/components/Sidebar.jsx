/**
 * Sidebar — Shared navigation component for all authenticated pages.
 * Provides consistent navigation with active state highlighting.
 */

import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/Sidebar.css';

const navItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/nepse', icon: '📈', label: 'NEPSE Analytics' },
    { path: '/planner', icon: '🎯', label: 'Goal Planner' },
    { path: '/portfolio', icon: '💼', label: 'Portfolio' },
    { path: '/health', icon: '💚', label: 'Health Score' },
    { path: '/reports', icon: '📋', label: 'Reports' },
    { path: '/chat', icon: '🤖', label: 'AI Chat' },
    { path: '/education', icon: '📚', label: 'Education' },
    { path: '/profile', icon: '👤', label: 'Profile' },
];

function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const handleLogout = () => {
        localStorage.clear();
        navigate('/');
    };

    return (
        <aside className="sidebar" id="main-sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo" onClick={() => navigate('/dashboard')}>
                    <span className="logo-icon">₹</span>
                    <span className="logo-text">FinWise Nepal</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <button
                        key={item.path}
                        id={`nav-${item.path.replace('/', '')}`}
                        className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                        onClick={() => navigate(item.path)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </button>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-user">
                    <div className="user-avatar">
                        {user.first_name?.charAt(0) || user.username?.charAt(0) || 'U'}
                    </div>
                    <div className="user-info">
                        <span className="user-name">{user.first_name || user.username}</span>
                        <span className="user-email">{user.email}</span>
                    </div>
                </div>
                <button className="logout-btn" id="logout-btn" onClick={handleLogout}>
                    Logout
                </button>
            </div>
        </aside>
    );
}

export default Sidebar;
