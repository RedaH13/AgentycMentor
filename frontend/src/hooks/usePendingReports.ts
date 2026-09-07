import { useState, useEffect } from 'react';
import api from '@/lib/api';

export interface PhaseEvaluation {
    phase_name: string;
    score: number;
    justification: string;
}

export interface PendingReport {
    session_id: string;
    professor_summary: string;
    pedagogical_warning: string;
    student_draft_report: string;
    langue: string;
    generated_at: string;
    student_name: string;
    subject_submission: string;
    document_type: string;
    phase_evaluations: PhaseEvaluation[];
    critical_errors: string[];
}

export const usePendingReports = () => {
    const [reports, setReports] = useState<PendingReport[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPendingReports = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await api.get('/professor/reports/pending');
            setReports(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load pending reports.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPendingReports();
    }, []);

    return { reports, isLoading, error, refetch: fetchPendingReports };
};