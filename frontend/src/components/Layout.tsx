import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LayoutDashboard, User, BookOpen, MessageSquare, Map, LogOut } from 'lucide-react';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { logout, profile } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const navItems = [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Profile', path: '/profile', icon: User },
        { name: 'Courses & Activities', path: '/academics', icon: BookOpen },
        { name: '4-Year Plan', path: '/plan', icon: Map },
        { name: 'AI Advisor', path: '/chat', icon: MessageSquare },
    ];

    return (
        <div className="flex h-screen bg-gray-100 font-sans">
            {/* Sidebar */}
            <div className="w-64 bg-white shadow-xl flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold tracking-tight text-indigo-700">Strategist<span className="text-indigo-400">AI</span></h1>
                </div>

                <nav className="flex-1 px-4 space-y-2 mt-4">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.name}
                                to={item.path}
                                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                                        ? 'bg-indigo-50 text-indigo-700 font-medium shadow-sm'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-indigo-600'
                                    }`}
                            >
                                <Icon size={20} className={isActive ? 'text-indigo-600' : 'text-gray-400'} />
                                <span>{item.name}</span>
                            </Link>
                        )
                    })}
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <div className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-xl">
                        <div className="flex flex-col truncate pr-2">
                            <span className="text-sm font-semibold text-gray-800 truncate">{profile?.first_name}</span>
                            <span className="text-xs text-gray-500 truncate">Grade {profile?.current_grade || '?'}</span>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Logout"
                        >
                            <LogOut size={18} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content Pane */}
            <main className="flex-1 overflow-y-auto w-full">
                <div className="p-8 max-w-6xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};
