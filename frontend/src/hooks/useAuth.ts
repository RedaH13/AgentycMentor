import { useState, useEffect } from 'react';
import { getToken, getRole, logout as authLogout } from '@/lib/auth';

export const useAuth = () => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [role, setRole] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        // runs only on the client side
        const token = getToken();
        const currentRole = getRole();

        if (token) {
            setIsAuthenticated(true);
            setRole(currentRole);
        }

        setIsLoading(false);
    }, []);

    const logout = () => {
        authLogout(); // Wipes localStorage and redirects to /login
    };

    return { isAuthenticated, role, isLoading, logout };
};