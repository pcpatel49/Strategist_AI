import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api';
import type { StudentProfile, RegisterData, LoginResponse } from '../types';

interface AuthContextType {
    isAuthenticated: boolean;
    studentId: string | null;
    profile: StudentProfile | null;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    register: (data: RegisterData) => Promise<void>;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [studentId, setStudentId] = useState<string | null>(null);
    const [profile, setProfile] = useState<StudentProfile | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // Initialize from storage & load profile
    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token');
            const sid = localStorage.getItem('student_id');

            if (token && sid) {
                setIsAuthenticated(true);
                setStudentId(sid);
                try {
                    const res = await api.get<StudentProfile>('/api/profile');
                    setProfile(res.data);
                } catch (err) {
                    console.error("Failed to load profile", err);
                    // Interceptor handles 401 redirects, but we clear state here just in case
                    setIsAuthenticated(false);
                    setStudentId(null);
                    localStorage.removeItem('token');
                    localStorage.removeItem('student_id');
                }
            }
            setIsLoading(false);
        };

        checkAuth();
    }, []);

    const login = async (email: string, password: string) => {
        const res = await api.post<LoginResponse>('/api/auth/login-json', { email, password });
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('student_id', res.data.student_id);
        setIsAuthenticated(true);
        setStudentId(res.data.student_id);

        // Fetch profile immediately after login
        const profileRes = await api.get<StudentProfile>('/api/profile');
        setProfile(profileRes.data);
    };

    const logout = async () => {
        try {
            if (localStorage.getItem('token')) {
                await api.post('/api/auth/logout');
            }
        } catch (e) {
            console.error("Logout API failed", e);
        } finally {
            localStorage.removeItem('token');
            localStorage.removeItem('student_id');
            setIsAuthenticated(false);
            setStudentId(null);
            setProfile(null);
        }
    };

    const register = async (data: RegisterData) => {
        await api.post('/api/auth/register', data);
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, studentId, profile, login, logout, register, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
