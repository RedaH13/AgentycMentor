"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRegister } from '@/hooks/useRegister';

export default function RegisterForm() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState<'student' | 'professor'>('student');
    const [inviteCode, setInviteCode] = useState('');

    const { register, isLoading, error, success } = useRegister();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await register(email, password, role, role === 'professor' ? inviteCode : undefined);
    };

    return (
        <div className="w-full max-w-md mx-auto p-8 bg-white border border-gray-100 rounded-lg shadow-sm">
            <div className="mb-8 text-center">
                <h2 className="text-2xl font-semibold text-gray-900">Create an account</h2>
                <p className="text-sm text-gray-500 mt-2">Join the MAS Pedagogic Grading Platform</p>
            </div>

            {error && (
                <div className="mb-6 p-3 text-sm text-red-600 bg-red-50 border border-red-100 rounded-md">
                    {error}
                </div>
            )}

            {success && (
                <div className="mb-6 p-3 text-sm text-green-700 bg-green-50 border border-green-200 rounded-md">
                    Registration successful! Redirecting to login...
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">I am a...</label>
                    <div className="flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="radio"
                                value="student"
                                checked={role === 'student'}
                                onChange={() => setRole('student')}
                                className="text-gray-900 focus:ring-gray-900"
                            />
                            <span className="text-sm text-gray-700">Student</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="radio"
                                value="professor"
                                checked={role === 'professor'}
                                onChange={() => setRole('professor')}
                                className="text-gray-900 focus:ring-gray-900"
                            />
                            <span className="text-sm text-gray-700">Professor</span>
                        </label>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="w-full px-4 py-2 text-gray-900 bg-transparent border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 transition-colors"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="w-full px-4 py-2 text-gray-900 bg-transparent border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 transition-colors"
                    />
                </div>

                {role === 'professor' && (
                    <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Invite Code</label>
                        <input
                            type="text"
                            value={inviteCode}
                            onChange={(e) => setInviteCode(e.target.value)}
                            required
                            className="w-full px-4 py-2 text-gray-900 bg-transparent border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 transition-colors"
                            placeholder="e.g. MAS-PROF-2026"
                        />
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isLoading || success}
                    className="w-full py-2.5 px-4 mt-2 bg-gray-900 text-white text-sm font-medium rounded-md hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 disabled:bg-gray-400 transition-colors"
                >
                    {isLoading ? 'Creating account...' : 'Create Account'}
                </button>
            </form>

            <div className="mt-6 text-center text-sm text-gray-500">
                Already have an account?{' '}
                <Link href="/login" className="text-gray-900 font-medium hover:underline">
                    Sign in
                </Link>
            </div>
        </div>
    );
}