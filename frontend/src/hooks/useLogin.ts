import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { setAuthData } from '@/lib/auth';
import { ApiError } from '@/types/auth';

export const useLogin = () => {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const login = async (email: string, password: string) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await api.post('/auth/login', { email, password });

            const { access_token, role } = response.data;
            setAuthData(access_token, role);

            // Dynamic routing based on JWT payload
            if (role === 'professor' || role === 'admin') {
                router.push('/dashboard/professor');
            } else {
                router.push('/dashboard/student');
            }
        } catch (err: ApiError | any) {
            // extract the error thrown by FastAPI HTTPException
            setError(err.response?.data?.detail || 'An unexpected error occurred.');
        } finally {
            setIsLoading(false);
        }
    };

    return { login, isLoading, error };
};