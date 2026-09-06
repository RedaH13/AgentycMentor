import { useState, useEffect } from 'react';
import { getToken, getRole, getUserIdentifier, logout as authLogout } from '@/lib/auth';

export const useAuth = () => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [role, setRole] = useState<string | null>(null);
    const [fullName, setFullName] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        const token = getToken();
        const currentRole = getRole();
        const currentIdentifier = getUserIdentifier();

        if (token) {
            setIsAuthenticated(true);
            setRole(currentRole);
            setFullName(currentIdentifier);
        }

        setIsLoading(false);
    }, []);

    const logout = () => {
        authLogout();
    };

    return { isAuthenticated, role, fullName, isLoading, logout };
};