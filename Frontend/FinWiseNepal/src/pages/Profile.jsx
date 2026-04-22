/**
 * Profile.jsx — User profile page with Sidebar navigation.
 * View and edit user profile settings including financial preferences.
 */

import { useState, useEffect } from 'react';
import { profileAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/Profile.css';

function Profile() {
    const [profile, setProfile] = useState(null);
    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({});
    const [saving, setSaving] = useState(false);

    useEffect(() => { loadProfile(); }, []);

    const loadProfile = async () => {
        try {
            const response = await profileAPI.getProfile();
            setProfile(response.data);
            setFormData(response.data);
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await profileAPI.updateProfile(formData);
            await loadProfile();
            setEditing(false);
        } catch (error) {
            console.error('Failed to update profile:', error);
        }
        setSaving(false);
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content" id="profile-page">
                <div className="section-header">
                    <div>
                        <h1 className="section-title">👤 Profile</h1>
                        <p className="section-subtitle">Manage your account and financial preferences</p>
                    </div>
                </div>

                {profile ? (
                    <div className="profile-grid">
                        <div className="card profile-main-card">
                            {!editing ? (
                                <div className="profile-view">
                                    <div className="profile-avatar-large">
                                        {profile.user?.first_name?.charAt(0) || '👤'}
                                    </div>
                                    <h2>{profile.user?.first_name} {profile.user?.last_name}</h2>
                                    <p className="profile-email-text">{profile.user?.email}</p>
                                    <p className="profile-username-text">@{profile.user?.username}</p>

                                    <div className="profile-details">
                                        <div className="profile-detail-item">
                                            <span className="detail-label">Financial Goals</span>
                                            <span className="detail-value">
                                                {profile.finance_goal || 'Not set'}
                                            </span>
                                        </div>
                                        <div className="profile-detail-item">
                                            <span className="detail-label">Risk Tolerance</span>
                                            <span className={`badge ${
                                                profile.risk_tolerance === 'aggressive' ? 'badge-danger' :
                                                profile.risk_tolerance === 'moderate' ? 'badge-warning' : 'badge-success'
                                            }`}>
                                                {profile.risk_tolerance || 'Not set'}
                                            </span>
                                        </div>
                                        <div className="profile-detail-item">
                                            <span className="detail-label">Member Since</span>
                                            <span className="detail-value">
                                                {new Date(profile.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>

                                    <button onClick={() => setEditing(true)} className="btn btn-primary"
                                        style={{ marginTop: 20, width: '100%' }}>
                                        Edit Profile
                                    </button>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit} className="profile-edit-form">
                                    <h2 style={{ marginBottom: 20 }}>Edit Profile</h2>
                                    <div className="form-group">
                                        <label>Financial Goals</label>
                                        <textarea
                                            name="finance_goal"
                                            value={formData.finance_goal || ''}
                                            onChange={handleChange}
                                            placeholder="What are your financial goals?"
                                            rows="4"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Risk Tolerance</label>
                                        <select name="risk_tolerance" value={formData.risk_tolerance || ''}
                                            onChange={handleChange}>
                                            <option value="">Select...</option>
                                            <option value="conservative">Conservative</option>
                                            <option value="moderate">Moderate</option>
                                            <option value="aggressive">Aggressive</option>
                                        </select>
                                    </div>
                                    <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                                        <button type="submit" className="btn btn-primary" style={{ flex: 1 }}
                                            disabled={saving}>
                                            {saving ? 'Saving...' : 'Save Changes'}
                                        </button>
                                        <button type="button" className="btn btn-secondary"
                                            onClick={() => { setEditing(false); setFormData(profile); }}>
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>

                        {/* Account Info Card */}
                        <div className="card">
                            <h3 className="card-title" style={{ marginBottom: 16 }}>🔐 Account Security</h3>
                            <div className="security-items">
                                <div className="security-item">
                                    <span>Password</span>
                                    <span className="badge badge-success">Set</span>
                                </div>
                                <div className="security-item">
                                    <span>Two-Factor Auth</span>
                                    <span className="badge badge-warning">Not Enabled</span>
                                </div>
                                <div className="security-item">
                                    <span>Login Method</span>
                                    <span className="detail-value">Email & Password</span>
                                </div>
                                <div className="security-item">
                                    <span>Session</span>
                                    <span className="badge badge-success">Active</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="loading-container"><div className="loading-spinner"></div></div>
                )}
            </main>
        </div>
    );
}

export default Profile;
