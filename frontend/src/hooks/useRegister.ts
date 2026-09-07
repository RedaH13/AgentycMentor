import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

export const useRegister = () => {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<boolean>(false);

    const register = async (user_identifier: string, email: string, password: string, role: string, invite_code?: string) => {
        setIsLoading(true);
        setError(null);
        setSuccess(false);

        try {
            // Construct payload, only adding invite_code if it was provided
            const payload: any = { user_identifier, email, password, role };
            if (invite_code) {
                payload.invite_code = invite_code;
            }

            await api.post('/auth/register', payload);
            setSuccess(true);

            // a moment to see the success message, then push to login
            setTimeout(() => {
                router.push('/login');
            }, 2000);

        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to register account.');
        } finally {
            setIsLoading(false);
        }
    };

    return { register, isLoading, error, success };
};