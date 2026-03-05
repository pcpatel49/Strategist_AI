import { useState, useEffect } from 'react';
import { api } from '../api';
import { Plus, Trash2, BookOpen, Users, Trophy } from 'lucide-react';
import type { Course, Activity } from '../types';

export const Academics = () => {
    const [courses, setCourses] = useState<Course[]>([]);
    const [activities, setActivities] = useState<Activity[]>([]);
    const [loading, setLoading] = useState(true);

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
                    <button className="flex items-center space-x-1 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg font-medium hover:bg-indigo-100 transition-colors">
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
                    <button className="flex items-center space-x-1 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg font-medium hover:bg-indigo-100 transition-colors">
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
        </div>
    );
};
