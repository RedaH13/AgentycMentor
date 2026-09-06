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
        <div className="w-full max-w-md mx-auto p-8 sm:p-10 bg-white rounded-[2rem] shadow-sm border border-zinc-100 antialiased">
            {/* Header */}
            <div className="mb-8 text-center">
                <h2 className="text-3xl font-serif font-bold tracking-tight text-zinc-900">
                    Create an Account
                </h2>
                <p className="text-sm font-serif text-zinc-500 mt-2">
                    Join the MAS Pedagogic Grading Platform powered by AI
                </p>
            </div>

            {/* Status Messages */}
            {error && (
                <div className="mb-6 p-4 text-sm font-sans text-red-800 bg-red-50/50 border border-red-100 rounded-2xl">
                    {error}
                </div>
            )}

            {success && (
                <div className="mb-6 p-4 text-sm font-sans text-emerald-800 bg-emerald-50/50 border border-emerald-100 rounded-2xl">
                    Registration successful! Redirecting to login...
                </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-serif font-medium text-zinc-700 mb-3">
                        I am a...
                    </label>
                    <div className="flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer p-2 pr-4 rounded-xl hover:bg-zinc-50 transition-colors border border-transparent hover:border-zinc-100">
                            <input
                                type="radio"
                                value="student"
                                checked={role === 'student'}
                                onChange={() => setRole('student')}
                                className="text-zinc-900 border-zinc-300 focus:ring-zinc-900 focus:ring-offset-0"
                            />
                            <span className="text-sm font-serif text-zinc-700">Student</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer p-2 pr-4 rounded-xl hover:bg-zinc-50 transition-colors border border-transparent hover:border-zinc-100">
                            <input
                                type="radio"
                                value="professor"
                                checked={role === 'professor'}
                                onChange={() => setRole('professor')}
                                className="text-zinc-900 border-zinc-300 focus:ring-zinc-900 focus:ring-offset-0"
                            />
                            <span className="text-sm font-serif text-zinc-700">Professor</span>
                        </label>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-serif font-medium text-zinc-700 mb-2">
                        Email
                    </label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="w-full px-4 py-3 font-sans text-sm text-zinc-900 bg-zinc-50/50 border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all placeholder:text-zinc-400"
                        placeholder="you@university.edu"
                    />
                </div>

                <div>
                    <label className="block text-sm font-serif font-medium text-zinc-700 mb-2">
                        Password
                    </label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="w-full px-4 py-3 font-sans text-sm text-zinc-900 bg-zinc-50/50 border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all placeholder:text-zinc-400"
                        placeholder="••••••••"
                    />
                </div>

                {role === 'professor' && (
                    <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <label className="block text-sm font-serif font-medium text-zinc-700 mb-2">
                            Invite Code
                        </label>
                        <input
                            type="text"
                            value={inviteCode}
                            onChange={(e) => setInviteCode(e.target.value)}
                            required
                            className="w-full px-4 py-3 font-sans text-sm text-zinc-900 bg-zinc-50/50 border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all placeholder:text-zinc-400"
                            placeholder="e.g. MAS-PROF-2026"
                        />
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isLoading || success}
                    className="w-full py-3 px-4 mt-4 bg-zinc-900 text-white text-sm font-sans font-medium rounded-full shadow-sm hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-zinc-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    {isLoading ? 'Creating account...' : 'Create Account'}
                </button>
            </form>

            {/* Footer */}
            <div className="mt-8 text-center text-sm font-serif text-zinc-500">
                Already have an account?{' '}
                <Link href="/login" className="text-zinc-900 font-sans font-medium hover:underline underline-offset-4">
                    Sign in
                </Link>
            </div>
        </div>
    );
}