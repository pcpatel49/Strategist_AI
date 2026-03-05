import { useEffect, useState } from 'react';
import { api } from '../api';
import type { DashboardStats } from '../types';
import { CheckCircle2, Circle, GraduationCap, Target, Award } from 'lucide-react';

export const Dashboard = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const res = await api.get<DashboardStats>('/api/profile/dashboard');
                setStats(res.data);
            } catch (e) {
                console.error("Dashboard fetch error", e);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboard();
    }, []);

    if (loading) {
        return (
            <div className="space-y-8 animate-pulse">
                <div className="h-10 bg-gray-200 rounded-xl w-64" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-24 bg-gray-100 rounded-2xl" />
                    ))}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="h-64 bg-gray-100 rounded-2xl" />
                    <div className="h-64 bg-gray-100 rounded-2xl" />
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Your Strategy Dashboard</h1>
                <p className="text-gray-500 mt-2">Here's where you stand on your journey to college.</p>
            </header>

            {/* Top Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
                    <div className="p-3 bg-blue-50 text-blue-600 rounded-xl"><Target size={24} /></div>
                    <div>
                        <p className="text-sm font-medium text-gray-500">Profile Completion</p>
                        <h3 className="text-2xl font-bold text-gray-900">{stats?.profile_completion || 0}%</h3>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
                    <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl"><GraduationCap size={24} /></div>
                    <div>
                        <p className="text-sm font-medium text-gray-500">Readiness Score</p>
                        <h3 className="text-2xl font-bold text-gray-900">{stats?.readiness_score || 0}/100</h3>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
                    <div className="p-3 bg-purple-50 text-purple-600 rounded-xl"><Award size={24} /></div>
                    <div>
                        <p className="text-sm font-medium text-gray-500">Active Milestones</p>
                        <h3 className="text-2xl font-bold text-gray-900">{stats?.upcoming_milestones?.length || 0}</h3>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Milestones Panel */}
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Upcoming Milestones</h3>

                    {stats?.upcoming_milestones?.length === 0 ? (
                        <div className="text-center py-8 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                            <p className="text-gray-500">No active milestones right now.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {stats?.upcoming_milestones?.map((m) => (
                                <div key={m.id} className="flex items-start space-x-4 p-4 rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
                                    {m.status === 'completed' ? (
                                        <CheckCircle2 className="text-emerald-500 mt-0.5 flex-shrink-0" />
                                    ) : (
                                        <Circle className="text-gray-300 mt-0.5 flex-shrink-0" />
                                    )}
                                    <div>
                                        <h4 className="font-semibold text-gray-900 text-sm">{m.title}</h4>
                                        <p className="text-sm text-gray-500 mt-1">{m.description}</p>
                                        <span className="inline-block mt-2 text-xs font-medium px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-md">
                                            {m.semester}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Recent Activity Panel */}
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Extracurriculars</h3>

                    {stats?.recent_activities?.length === 0 ? (
                        <div className="text-center py-8 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                            <p className="text-gray-500">You haven't logged any activities yet.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {stats?.recent_activities?.map((a) => (
                                <div key={a.id} className="p-4 rounded-xl bg-gray-50 border border-gray-100">
                                    <div className="flex justify-between items-start">
                                        <h4 className="font-semibold text-gray-900">{a.activity_name}</h4>
                                        <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">{a.category}</span>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-2">{a.role} • {a.hours_per_week} hrs/wk</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
