"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Role } from '@/types/auth';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: Role[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
    const router = useRouter();
    const { isAuthenticated, role, isLoading } = useAuth();

    useEffect(() => {
        // run navigation checks after the initial auth check is done loading
        if (!isLoading) {
            if (!isAuthenticated) {
                router.push('/login');
            } else if (allowedRoles && role && !allowedRoles.includes(role as Role)) {
                // If logged in but have the wrong role, send to proper dashboard
                router.push(`/dashboard/${role}`);
            }
        }
    }, [isLoading, isAuthenticated, role, allowedRoles, router]);

    // loading state while checking localStorage
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-sm text-gray-500 animate-pulse">Verifying session...</div>
            </div>
        );
    }

    // If authenticated and authorized, render the actual page
    if (isAuthenticated && (!allowedRoles || (role && allowedRoles.includes(role as Role)))) {
        return <>{children}</>;
    }

    // Fallback while redirecting
    return null;
}