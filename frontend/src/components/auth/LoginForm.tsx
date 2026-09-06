"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useLogin } from '@/hooks/useLogin';

export default function LoginForm() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login, isLoading, error } = useLogin();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await login(email, password);
    };

    return (
        <div className="w-full max-w-md mx-auto p-8 sm:p-10 bg-white rounded-[2rem] shadow-sm border border-zinc-100 antialiased">
            {/* Header */}
            <div className="mb-8 text-center">
                <h2 className="text-3xl font-serif font-bold tracking-tight text-zinc-900">
                    Welcome Back
                </h2>
                <p className="text-sm font-serif text-zinc-500 mt-2">
                    Sign in to access your dashboard
                </p>
            </div>

            {/* Error Message */}
            {error && (
                <div className="mb-6 p-4 text-sm font-sans text-red-800 bg-red-50/50 border border-red-100 rounded-2xl">
                    {error}
                </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
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

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3 px-4 mt-2 bg-zinc-900 text-white text-sm font-sans font-medium rounded-full shadow-sm hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-zinc-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    {isLoading ? 'Signing in...' : 'Sign In'}
                </button>
            </form>

            {/* Footer */}
            <div className="mt-8 text-center text-sm font-serif text-zinc-500">
                Don’t have an account?{' '}
                <Link href="/register" className="text-zinc-900 font-sans font-medium hover:underline underline-offset-4">
                    Register here
                </Link>
            </div>
        </div>
    );
}