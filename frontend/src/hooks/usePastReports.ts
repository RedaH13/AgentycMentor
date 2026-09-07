import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { PendingReport } from './usePendingReports';

export const usePastReports = () => {
    const [reports, setReports] = useState<PendingReport[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPastReports = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await api.get('/professor/reports/past');
            setReports(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load past reports.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPastReports();
    }, []);

    return { reports, isLoading, error, refetch: fetchPastReports };
};