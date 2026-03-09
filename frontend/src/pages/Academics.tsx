import { useState, useEffect } from 'react';
import { api } from '../api';
import { Plus, Trash2, BookOpen, Users, Trophy } from 'lucide-react';
import type { Course, Activity } from '../types';

export const Academics = () => {
    const [courses, setCourses] = useState<Course[]>([]);
    const [activities, setActivities] = useState<Activity[]>([]);
    const [loading, setLoading] = useState(true);

    const [isCourseModalOpen, setIsCourseModalOpen] = useState(false);
    const [courseForm, setCourseForm] = useState({
        course_name: '', course_level: 'Regular', grade: '', credits: 1.0, semester: 'Fall', year: new Date().getFullYear()
    });
    const [isSavingCourse, setIsSavingCourse] = useState(false);

    const [isActivityModalOpen, setIsActivityModalOpen] = useState(false);
    const [activityForm, setActivityForm] = useState({
        activity_name: '', category: 'Club', role: 'Member', hours_per_week: 1, achievements: ''
    });
    const [isSavingActivity, setIsSavingActivity] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [courseRes, activityRes] = await Promise.all([
                    api.get<Course[]>('/api/courses'),
                    api.get<Activity[]>('/api/activities'),
                ]);
                setCourses(courseRes.data);
                setActivities(activityRes.data);
            } catch (e) {
                console.error("Data fetch error", e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const deleteCourse = async (id: number) => {
        try {
            await api.delete(`/api/courses/${id}`);
            setCourses(courses.filter(c => c.id !== id));
        } catch (e) {
            console.error("Delete course error", e);
        }
    };

    const deleteActivity = async (id: number) => {
        try {
            await api.delete(`/api/activities/${id}`);
            setActivities(activities.filter(a => a.id !== id));
        } catch (e) {
            console.error("Delete activity error", e);
        }
    };

    const handleAddCourse = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSavingCourse(true);
        try {
            const res = await api.post<Course>('/api/courses', courseForm);
            setCourses([res.data, ...courses]);
            setIsCourseModalOpen(false);
            setCourseForm({ course_name: '', course_level: 'Regular', grade: '', credits: 1.0, semester: 'Fall', year: new Date().getFullYear() });
        } catch (err) {
            console.error(err);
        } finally {
            setIsSavingCourse(false);
        }
    };

    const handleAddActivity = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSavingActivity(true);
        try {
            const payload = {
                ...activityForm,
                achievements: activityForm.achievements ? activityForm.achievements.split(',').map(s => s.trim()).filter(Boolean) : []
            };
            const res = await api.post<Activity>('/api/activities', payload);
            setActivities([res.data, ...activities]);
            setIsActivityModalOpen(false);
            setActivityForm({ activity_name: '', category: 'Club', role: 'Member', hours_per_week: 1, achievements: '' });
        } catch (err) {
            console.error(err);
        } finally {
            setIsSavingActivity(false);
        }
    };

    if (loading) return <div className="animate-pulse h-64 bg-gray-100 rounded-3xl"></div>;

    return (
        <div className="space-y-12 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Academics & Activities</h1>
                <p className="text-gray-500 mt-2">Document your achievements and course history.</p>
            </header>

            {/* Courses Section */}
            <section className="space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <BookOpen className="text-indigo-600" size={24} />
                        <h2 className="text-xl font-bold text-gray-900">My Courses</h2>
                    </div>
                    <button onClick={() => setIsCourseModalOpen(true)} className="flex items-center space-x-1 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg font-medium hover:bg-indigo-100 transition-colors">
                        <Plus size={18} />
                        <span>Add Course</span>
                    </button>
                </div>

                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 border-b border-gray-100">
                            <tr>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Course Name</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Level</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Grade</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Year</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {courses.map((course) => (
                                <tr key={course.id} className="hover:bg-gray-50/50 transition-colors">
                                    <td className="px-6 py-4 font-medium text-gray-900">{course.course_name}</td>
                                    <td className="px-6 py-4 text-gray-600">
                                        <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md font-semibold">{course.course_level}</span>
                                    </td>
                                    <td className="px-6 py-4 font-bold text-gray-900">{course.grade || '-'}</td>
                                    <td className="px-6 py-4 text-gray-600">{course.year}</td>
                                    <td className="px-6 py-4 text-right">
                                        <button onClick={() => deleteCourse(course.id)} className="text-gray-400 hover:text-red-600 p-2"><Trash2 size={16} /></button>
                                    </td>
                                </tr>
                            ))}
                            {courses.length === 0 && (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500 italic">No courses added yet.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </section>

            {/* Activities Section */}
            <section className="space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Users className="text-indigo-600" size={24} />
                        <h2 className="text-xl font-bold text-gray-900">Extracurricular Activities</h2>
                    </div>
                    <button onClick={() => setIsActivityModalOpen(true)} className="flex items-center space-x-1 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg font-medium hover:bg-indigo-100 transition-colors">
                        <Plus size={18} />
                        <span>Add Activity</span>
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {activities.map((activity) => (
                        <div key={activity.id} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 relative group">
                            <button
                                onClick={() => deleteActivity(activity.id)}
                                className="absolute top-4 right-4 text-gray-400 hover:text-red-600 p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <Trash2 size={16} />
                            </button>
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="font-bold text-gray-900 text-lg">{activity.activity_name}</h3>
                                    <span className="text-xs font-semibold px-2 py-1 bg-gray-100 text-gray-600 rounded mt-1 inline-block">{activity.category}</span>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm mt-4">
                                <div className="bg-gray-50 p-3 rounded-xl">
                                    <p className="text-gray-500 mb-1">Role</p>
                                    <p className="font-semibold text-gray-900">{activity.role}</p>
                                </div>
                                <div className="bg-gray-50 p-3 rounded-xl">
                                    <p className="text-gray-500 mb-1">Commitment</p>
                                    <p className="font-semibold text-gray-900">{activity.hours_per_week} hrs/wk</p>
                                </div>
                            </div>
                            {activity.achievements && activity.achievements.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-gray-50">
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2 flex items-center">
                                        <Trophy size={12} className="mr-1" /> Achievements
                                    </p>
                                    <ul className="space-y-2">
                                        {activity.achievements.map((item, i) => (
                                            <li key={i} className="text-sm text-gray-700 flex items-start">
                                                <span className="text-indigo-500 mr-2">•</span> {item}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ))}
                    {activities.length === 0 && (
                        <div className="col-span-full py-12 text-center bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                            <p className="text-gray-500">No activities added yet. Start documenting your impact!</p>
                        </div>
                    )}
                </div>
            </section>

            {/* Course Form Modal */}
            {isCourseModalOpen && (
                <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50 p-4">
                    <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-lg border border-gray-100 animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center space-x-3 mb-6">
                            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
                                <BookOpen size={20} />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900">Add New Course</h2>
                        </div>
                        <form onSubmit={handleAddCourse} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Course Name *</label>
                                <input required className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={courseForm.course_name} onChange={e => setCourseForm({ ...courseForm, course_name: e.target.value })} placeholder="e.g. AP Calculus BC" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
                                    <select className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all bg-white" value={courseForm.course_level} onChange={e => setCourseForm({ ...courseForm, course_level: e.target.value })}>
                                        <option>Regular</option>
                                        <option>Honors</option>
                                        <option>AP</option>
                                        <option>IB</option>
                                        <option>College</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Grade</label>
                                    <input className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={courseForm.grade} onChange={e => setCourseForm({ ...courseForm, grade: e.target.value })} placeholder="e.g. A, 98" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Credits</label>
                                    <input type="number" step="0.5" min="0" required className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={courseForm.credits} onChange={e => setCourseForm({ ...courseForm, credits: parseFloat(e.target.value) || 0 })} />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                                    <input type="number" required className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={courseForm.year} onChange={e => setCourseForm({ ...courseForm, year: parseInt(e.target.value) || new Date().getFullYear() })} />
                                </div>
                            </div>
                            <div className="flex justify-end space-x-3 mt-8 pt-4 border-t border-gray-50">
                                <button type="button" onClick={() => setIsCourseModalOpen(false)} className="px-5 py-2.5 text-gray-600 font-medium hover:bg-gray-100 rounded-xl transition-colors">Cancel</button>
                                <button type="submit" disabled={isSavingCourse} className="px-5 py-2.5 bg-indigo-600 font-medium text-white rounded-xl hover:bg-indigo-700 transition-colors shadow-md shadow-indigo-200 disabled:opacity-50">
                                    {isSavingCourse ? 'Saving...' : 'Save Course'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Activity Form Modal */}
            {isActivityModalOpen && (
                <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50 p-4">
                    <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-lg border border-gray-100 animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center space-x-3 mb-6">
                            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
                                <Users size={20} />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900">Add New Activity</h2>
                        </div>
                        <form onSubmit={handleAddActivity} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Activity Name *</label>
                                <input required className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={activityForm.activity_name} onChange={e => setActivityForm({ ...activityForm, activity_name: e.target.value })} placeholder="e.g. Model UN, Varsity Tennis" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                                    <input className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={activityForm.category} onChange={e => setActivityForm({ ...activityForm, category: e.target.value })} placeholder="e.g. Club, Sport, Volunteer" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                                    <input className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={activityForm.role} onChange={e => setActivityForm({ ...activityForm, role: e.target.value })} placeholder="e.g. President, Member" />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Hours / Week</label>
                                    <input type="number" min="0" required className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={activityForm.hours_per_week} onChange={e => setActivityForm({ ...activityForm, hours_per_week: parseInt(e.target.value) || 0 })} />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Achievements <span className="text-gray-400 font-normal">(comma separated)</span></label>
                                <input className="w-full border border-gray-200 rounded-xl p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" value={activityForm.achievements} onChange={e => setActivityForm({ ...activityForm, achievements: e.target.value })} placeholder="e.g. State Finalist, Outstanding Delegate" />
                            </div>
                            <div className="flex justify-end space-x-3 mt-8 pt-4 border-t border-gray-50">
                                <button type="button" onClick={() => setIsActivityModalOpen(false)} className="px-5 py-2.5 text-gray-600 font-medium hover:bg-gray-100 rounded-xl transition-colors">Cancel</button>
                                <button type="submit" disabled={isSavingActivity} className="px-5 py-2.5 bg-indigo-600 font-medium text-white rounded-xl hover:bg-indigo-700 transition-colors shadow-md shadow-indigo-200 disabled:opacity-50">
                                    {isSavingActivity ? 'Saving...' : 'Save Activity'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
