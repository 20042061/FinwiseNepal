/**
 * App.jsx — Main application router with all page routes.
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Education from './pages/Education';
import Profile from './pages/Profile';
import NepseAnalytics from './pages/NepseAnalytics';
import InvestmentPlanner from './pages/InvestmentPlanner';
import PortfolioPage from './pages/PortfolioPage';
import HealthScorePage from './pages/HealthScorePage';
import Reports from './pages/Reports';

function App() {
    return (
        <Router>
            <Routes>
                {/* Public routes */}
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Authenticated routes */}
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/education" element={<Education />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/nepse" element={<NepseAnalytics />} />
                <Route path="/planner" element={<InvestmentPlanner />} />
                <Route path="/portfolio" element={<PortfolioPage />} />
                <Route path="/health" element={<HealthScorePage />} />
                <Route path="/reports" element={<Reports />} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}

export default App;
