import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatAPI } from '../api';
import Sidebar from '../components/Sidebar';
import '../styles/Chat.css';

function Chat() {
    const [sessions, setSessions] = useState([]);
    const [currentSession, setCurrentSession] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const messagesEndRef = useRef(null);
    const navigate = useNavigate();

    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        loadSessions();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadSessions = async () => {
        try {
            const response = await chatAPI.getSessions();
            setSessions(response.data);
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    };

    const createNewChat = async () => {
        try {
            const response = await chatAPI.createSession();
            setCurrentSession(response.data);
            setMessages([]);
            await loadSessions();
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    };

    const selectSession = async (session) => {
        try {
            const response = await chatAPI.getSession(session.id);
            setCurrentSession(response.data);
            setMessages(response.data.messages || []);
        } catch (error) {
            console.error('Failed to load session:', error);
        }
    };

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        if (!currentSession) {
            await createNewChat();
        }

        const userMessage = {
            role: 'user',
            content: inputMessage,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputMessage('');
        setLoading(true);

        try {
            const response = await chatAPI.sendMessage(currentSession.id, inputMessage);

            const aiMessage = {
                role: 'assistant',
                content: response.data.ai_message?.content || response.data.response || 'No response received.',
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, aiMessage]);
            await loadSessions();
        } catch (error) {
            console.error('Failed to send message:', error);
            const errorMessage = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const deleteSession = async (sessionId) => {
        if (!window.confirm('Delete this conversation?')) return;

        try {
            await chatAPI.deleteSession(sessionId);
            await loadSessions();

            if (currentSession?.id === sessionId) {
                setCurrentSession(null);
                setMessages([]);
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
        }
    };

    const handleLogout = () => {
        localStorage.clear();
        navigate('/');
    };

    const suggestedQuestions = [
        { icon: '💰', text: 'Help me save money' },
        { icon: '📈', text: 'Start investing' },
        { icon: '📊', text: 'Create a budget' },
        { icon: '🏖️', text: 'Retirement planning' },
    ];

    return (
        <>
        <Sidebar />
        <div className="chat-container" style={{ marginLeft: 260 }}>
            {/* Sidebar */}
            <div className={`chat-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <button onClick={createNewChat} className="new-chat-btn">
                        + New chat
                    </button>
                </div>

                <div className="chat-section-label">YOUR CHATS</div>

                <div className="chat-history">
                    {sessions.map((session) => (
                        <div
                            key={session.id}
                            className={`chat-item ${currentSession?.id === session.id ? 'active' : ''}`}
                            onClick={() => selectSession(session)}
                        >
                            <div className="chat-item-content">
                                <span className="chat-item-title">{session.title || 'New Conversation'}</span>
                                <span className="chat-item-date">
                                    {new Date(session.created_at).toLocaleDateString()}
                                </span>
                            </div>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    deleteSession(session.id);
                                }}
                                className="delete-btn"
                            >
                                🗑️
                            </button>
                        </div>
                    ))}
                </div>

                <div className="sidebar-footer">
                    <div className="user-profile">
                        <div className="user-avatar">{(user.first_name?.[0] || user.username?.[0] || 'U').toUpperCase()}</div>
                        <span className="user-name">{user.username || 'User'}</span>
                    </div>
                    <button onClick={handleLogout} className="sidebar-btn logout-btn">
                        Logout
                    </button>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="chat-main">
                <button
                    className="sidebar-toggle"
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                >
                    ☰
                </button>

                <div className="messages-container">
                    {messages.length === 0 ? (
                        <div className="empty-state">
                            <h1 className="welcome-title">How can I help you, {user.first_name || user.username}?</h1>
                            <div className="suggestion-cards">
                                {suggestedQuestions.map((q, index) => (
                                    <div
                                        key={index}
                                        className="suggestion-card"
                                        onClick={() => setInputMessage(q.text)}
                                    >
                                        <span className="suggestion-icon">{q.icon}</span>
                                        <span className="suggestion-text">{q.text}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="messages-list">
                            {messages.map((msg, index) => (
                                <div key={index} className={`message ${msg.role}`}>
                                    <div className="message-avatar">
                                        {msg.role === 'user' ? '👤' : '🤖'}
                                    </div>
                                    <div className="message-content">
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="message assistant">
                                    <div className="message-avatar">🤖</div>
                                    <div className="message-content typing-indicator">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="input-container">
                    <form onSubmit={sendMessage} className="input-form">
                        <textarea
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Ask me anything about finance..."
                            rows="1"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    sendMessage(e);
                                }
                            }}
                        />
                        <button type="submit" disabled={!inputMessage.trim() || loading}>
                            ➤
                        </button>
                    </form>
                    <p className="disclaimer">
                        FinWise AI can make mistakes. Consult a financial professional for important decisions.
                    </p>
                </div>
            </div>
        </div>
        </>
    );
}

export default Chat;
