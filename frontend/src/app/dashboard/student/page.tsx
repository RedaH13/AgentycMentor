"use client";

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/hooks/useAuth';

export default function StudentDashboard() {
    const { logout } = useAuth();

    return (
        <ProtectedRoute allowedRoles={['student']}>
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-4xl mx-auto bg-white border border-gray-100 rounded-lg shadow-sm p-8">
                    <div className="flex justify-between items-center mb-8 pb-4 border-b border-gray-100">
                        <h1 className="text-2xl font-semibold text-gray-900">Student Space</h1>
                        <button
                            onClick={logout}
                            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
                        >
                            Sign Out
                        </button>
                    </div>

                    <div className="text-gray-600">
                        <p>Authentication successful. Your JWT is stored securely.</p>
                        <p className="mt-2 text-sm text-gray-400">The file upload and grading pipeline will live here.</p>
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
}