import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { ShieldCheck, Loader2 } from 'lucide-react';

export const VerifyOTP: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const email = searchParams.get('email') || '';
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!email) {
            navigate('/register');
        }
    }, [email, navigate]);

    const handleChange = (index: number, value: string) => {
        if (!/^[0-9]?$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        // Auto-focus next input
        if (value && index < 5) {
            const nextInput = document.getElementById(`otp-${index + 1}`) as HTMLInputElement;
            if (nextInput) nextInput.focus();
        }
    };

    const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            const prevInput = document.getElementById(`otp-${index - 1}`) as HTMLInputElement;
            if (prevInput) prevInput.focus();
        }
    };

    const handleVerify = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        const code = otp.join('');
        if (code.length < 6) {
            setError('Please enter the full 6-digit code.');
            return;
        }

        setLoading(true);
        setError('');
        try {
            await api.post('/api/auth/verify-otp', { email, otp: code });
            navigate('/login', { state: { message: 'Email verified successfully! You can now log in.' } });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid or expired code.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <div className="max-w-md w-full bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
                <main className="text-center space-y-6">
                    <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-2">
                        <ShieldCheck size={32} />
                    </div>

                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Enter Verification Code</h1>
                        <p className="text-gray-500 mt-2">
                            We've sent a 6-digit code to <span className="font-medium text-gray-900">{email}</span>
                        </p>
                    </div>

                    <form onSubmit={handleVerify} className="space-y-8">
                        <div className="flex justify-center gap-2 md:gap-4">
                            {otp.map((digit, index) => (
                                <input
                                    key={index}
                                    id={`otp-${index}`}
                                    type="text"
                                    maxLength={1}
                                    value={digit}
                                    onChange={(e) => handleChange(index, e.target.value)}
                                    onKeyDown={(e) => handleKeyDown(index, e)}
                                    className="w-10 h-12 md:w-12 md:h-14 text-center text-xl font-bold bg-gray-50 border border-gray-100 rounded-xl focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-50 outline-none transition-all"
                                />
                            ))}
                        </div>

                        {error && (
                            <p className="text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-100 italic">
                                {error}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={loading || otp.join('').length < 6}
                            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100 disabled:opacity-50 flex items-center justify-center space-x-2"
                        >
                            {loading && <Loader2 className="animate-spin" size={18} />}
                            <span>Verify Code</span>
                        </button>
                    </form>

                    <p className="text-sm text-gray-500">
                        Didn't receive a code?{' '}
                        <button className="text-indigo-600 font-medium hover:underline">Resend</button>
                    </p>
                </main>
            </div>
        </div>
    );
};
