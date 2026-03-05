import { useEffect, useState } from 'react';
import { api } from '../api';
import type { StrategicPlan } from '../types';
import { Wand2, CalendarDays, CheckCircle2 } from 'lucide-react';

export const Plan = () => {
    const [plan, setPlan] = useState<StrategicPlan | null>(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    const fetchPlan = async () => {
        try {
            const res = await api.get<StrategicPlan>('/api/plan');
            setPlan(res.data);
        } catch (e: any) {
            if (e.response?.status !== 404) {
                console.error("Plan fetch error", e);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPlan();
    }, []);

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            const res = await api.post<StrategicPlan>('/api/plan/generate');
            setPlan(res.data);
        } catch (e) {
            console.error("Plan generation error", e);
        } finally {
            setGenerating(false);
        }
    };

    const toggleMilestone = async (id: number, currentStatus: string) => {
        if (currentStatus === 'completed') return; // backend only supports completing for now

        try {
            await api.put(`/api/milestones/${id}/complete`);
            // Optimistic update
            setPlan(prev => {
                if (!prev) return prev;
                return {
                    ...prev,
                    milestones: prev.milestones.map(m => m.id === id ? { ...m, status: 'completed' } : m)
                };
            });
        } catch (e) {
            console.error("Milestone update failed", e);
        }
    };

    if (loading) return <div className="animate-pulse h-64 bg-gray-100 rounded-3xl"></div>;

    if (!plan) {
        return (
            <div className="flex flex-col items-center justify-center p-12 bg-white rounded-3xl shadow-sm border border-gray-100 min-h-[60vh] text-center">
                <div className="w-20 h-20 bg-indigo-50 rounded-full flex items-center justify-center mb-6">
                    <CalendarDays className="text-indigo-600" size={40} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">No Strategic Plan Yet</h2>
                <p className="text-gray-500 max-w-md mb-8">
                    You haven't generated your personalized 4-year roadmap yet. Our multi-agent AI system will analyze your profile and goals to create one.
                </p>
                <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-70 transition-all shadow-md hover:shadow-lg"
                >
                    {generating ? <span className="animate-spin inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full" /> : <Wand2 size={20} />}
                    <span>{generating ? 'Agents are planning...' : 'Generate My Plan'}</span>
                </button>
            </div>
        );
    }

    const pd = plan.plan_data as any;

    return (
        <div className="space-y-8 animate-in fade-in duration-500 max-w-4xl mx-auto">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Your 4-Year Strategy</h1>
                    <p className="text-gray-500 mt-2">Track: {pd.academic_track || 'General'}</p>
                </div>
                <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-50 text-indigo-700 font-medium rounded-lg hover:bg-indigo-100 transition-colors"
                >
                    <Wand2 size={16} />
                    <span>{generating ? 'Regenerating...' : 'Regenerate'}</span>
                </button>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 line-clamp-4 hover:line-clamp-none transition-all">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Strategic Overview</h3>
                <p className="text-gray-600 leading-relaxed">{pd.summary}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                    <h3 className="text-xl font-bold text-gray-900">Priority Actions</h3>
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <ul className="divide-y divide-gray-50">
                            {pd.priority_actions?.map((action: string, i: number) => (
                                <li key={i} className="p-4 text-gray-700 font-medium">{action}</li>
                            ))}
                            {!pd.priority_actions?.length && <li className="p-4 text-gray-500 italic">No priorities logged.</li>}
                        </ul>
                    </div>

                    <h3 className="text-xl font-bold text-gray-900 pt-4">Course Recommendations</h3>
                    <div className="flex flex-wrap gap-2">
                        {pd.course_recommendations?.map((r: string, i: number) => (
                            <span key={i} className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-md text-sm font-medium border border-blue-100">{r}</span>
                        ))}
                    </div>

                    <h3 className="text-xl font-bold text-gray-900 pt-4">Target Activities</h3>
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 space-y-3">
                        {pd.activity_suggestions?.map((r: string, i: number) => (
                            <p key={i} className="text-gray-700 text-sm flex items-start"><span className="text-indigo-400 mr-2 font-bold">•</span>{r}</p>
                        ))}
                    </div>
                </div>

                <div className="space-y-6">
                    <h3 className="text-xl font-bold text-gray-900">Roadmap Milestones</h3>
                    <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                        {plan.milestones?.map((m) => (
                            <div key={m.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                <div
                                    className={`flex items-center justify-center w-10 h-10 rounded-full border-4 border-white shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow cursor-pointer transition-colors ${m.status === 'completed' ? 'bg-emerald-500' : 'bg-slate-300 hover:bg-slate-400'}`}
                                    onClick={() => toggleMilestone(m.id, m.status)}
                                >
                                    {m.status === 'completed' && <CheckCircle2 className="text-white w-5 h-5" />}
                                </div>

                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                                    <div className="flex items-center justify-between mb-1">
                                        <h4 className="font-bold text-gray-900">{m.title}</h4>
                                        <span className="text-xs font-semibold px-2 py-0.5 bg-gray-100 text-gray-600 rounded">{m.semester}</span>
                                    </div>
                                    <p className="text-sm text-gray-500">{m.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
