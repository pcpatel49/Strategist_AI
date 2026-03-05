import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

export const VerifyEmail: React.FC = () => {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();
    const token = searchParams.get('token');

    useEffect(() => {
        const verify = async () => {
            if (!token) {
                setStatus('error');
                setMessage('No verification token found in URL.');
                return;
            }

            try {
                await api.post('/api/auth/verify-email', { token });
                setStatus('success');
                setMessage('Email verified successfully! You can now log in.');
                // Auto redirect after 3 seconds
                setTimeout(() => navigate('/login'), 3000);
            } catch (err: any) {
                setStatus('error');
                setMessage(err.response?.data?.detail || 'Verification failed or token expired.');
            }
        };

        verify();
    }, [token, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
                {status === 'loading' && (
                    <div className="space-y-4">
                        <Loader2 className="mx-auto text-indigo-600 animate-spin" size={48} />
                        <h2 className="text-xl font-bold text-gray-900">Verifying your email...</h2>
                    </div>
                )}

                {status === 'success' && (
                    <div className="space-y-4">
                        <CheckCircle className="mx-auto text-emerald-500" size={48} />
                        <h2 className="text-xl font-bold text-gray-900">Success!</h2>
                        <p className="text-gray-500">{message}</p>
                        <p className="text-sm text-gray-400">Redirecting to login...</p>
                        <Link to="/login" className="block mt-4 text-indigo-600 font-medium">Click here if not redirected</Link>
                    </div>
                )}

                {status === 'error' && (
                    <div className="space-y-4">
                        <XCircle className="mx-auto text-red-500" size={48} />
                        <h2 className="text-xl font-bold text-gray-900">Verification Failed</h2>
                        <p className="text-red-600">{message}</p>
                        <Link to="/register" className="block mt-6 px-6 py-2 bg-indigo-600 text-white rounded-xl">Back to Registration</Link>
                    </div>
                )}
            </div>
        </div>
    );
};
