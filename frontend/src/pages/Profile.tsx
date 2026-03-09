import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';
import { Save, User as UserIcon, GraduationCap, Target } from 'lucide-react';
import type { StudentProfile } from '../types';

export const Profile = () => {
    const { profile } = useAuth();
    const [formData, setFormData] = useState<Partial<StudentProfile>>(profile || {});
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ text: '', type: '' });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: (name === 'gpa' || name === 'sat_score' || name === 'act_score' || name === 'graduation_year' || name === 'current_grade')
                ? (value === '' ? null : parseFloat(value))
                : value
        }));
    };

    const handleArrayChange = (name: 'target_universities' | 'target_majors', value: string) => {
        setFormData(prev => ({
            ...prev,
            [name]: value.split(',').map(s => s.trim()).filter(s => s !== '')
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ text: '', type: '' });
        try {
            await api.put('/api/profile', formData);
            setMessage({ text: 'Profile updated successfully!', type: 'success' });
        } catch (err: any) {
            setMessage({ text: err.response?.data?.detail || 'Failed to update profile', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Your Profile</h1>
                <p className="text-gray-500 mt-2">Manage your academic profile and college targets.</p>
            </header>

            {message.text && (
                <div className={`p-4 rounded-xl border ${message.type === 'success' ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-red-50 border-red-100 text-red-700'
                    }`}>
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8">
                {/* Personal Info */}
                <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-2 mb-6 border-b border-gray-50 pb-4">
                        <UserIcon className="text-indigo-600" size={20} />
                        <h2 className="text-lg font-bold text-gray-900">Personal Information</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                            <input
                                name="first_name"
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.first_name || ''}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input
                                name="last_name"
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.last_name || ''}
                                onChange={handleChange}
                            />
                        </div>
                    </div>
                </section>

                {/* Academic Profile */}
                <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-2 mb-6 border-b border-gray-50 pb-4">
                        <GraduationCap className="text-indigo-600" size={20} />
                        <h2 className="text-lg font-bold text-gray-900">Academic Standing</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Current Grade</label>
                            <select
                                name="current_grade"
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none bg-white"
                                value={formData.current_grade || ''}
                                onChange={handleChange}
                            >
                                <option value="9">9th Grade</option>
                                <option value="10">10th Grade</option>
                                <option value="11">11th Grade</option>
                                <option value="12">12th Grade</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">GPA</label>
                            <input
                                name="gpa"
                                type="number"
                                step="0.01"
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.gpa || ''}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">SAT Score</label>
                            <input
                                name="sat_score"
                                type="number"
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.sat_score || ''}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">ACT Score</label>
                            <input
                                name="act_score"
                                type="number"
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.act_score || ''}
                                onChange={handleChange}
                            />
                        </div>
                    </div>
                </section>

                {/* College Targets */}
                <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-2 mb-6 border-b border-gray-50 pb-4">
                        <Target className="text-indigo-600" size={20} />
                        <h2 className="text-lg font-bold text-gray-900">College Targets</h2>
                    </div>
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Target Universities (comma separated)</label>
                            <input
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.target_universities?.join(', ') || ''}
                                onChange={(e) => handleArrayChange('target_universities', e.target.value)}
                                placeholder="MIT, Stanford, UC Berkeley..."
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Target Majors (comma separated)</label>
                            <input
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-indigo-500 outline-none"
                                value={formData.target_majors?.join(', ') || ''}
                                onChange={(e) => handleArrayChange('target_majors', e.target.value)}
                                placeholder="Computer Science, Economics, Biology..."
                            />
                        </div>
                    </div>
                </section>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex items-center space-x-2 px-8 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-all shadow-md shadow-indigo-200/50 disabled:opacity-70"
                    >
                        {loading ? <span className="animate-spin inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full mr-2" /> : <Save size={18} />}
                        <span>Save Changes</span>
                    </button>
                </div>
            </form>
        </div>
    );
};
