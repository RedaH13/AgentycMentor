import { useState, useEffect } from 'react';
import api from '@/lib/api';

export interface PhaseMetric {
    phase_name: string;
    average_score: number;
}

export interface ErrorMetric {
    error_text: string;
    occurrence_count: number;
}

export interface ClassMetricsData {
    total_submissions: number;
    average_score: number;
    pass_rate: number;
    phase_averages: PhaseMetric[];
    top_errors: ErrorMetric[];
}

export const useClassMetrics = () => {
    const [metrics, setMetrics] = useState<ClassMetricsData | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMetrics = async () => {
            setIsLoading(true);
            try {
                const response = await api.get('/professor/metrics/class');
                setMetrics(response.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to load class metrics.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchMetrics();
    }, []);

    return { metrics, isLoading, error };
};