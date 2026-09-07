import { useState, useEffect } from 'react';
import api from '@/lib/api';

export interface PhaseEvaluation {
    phase_name: string;
    score: number;
    justification: string;
}

export interface ReportDetails {
    session_id: string;
    subject_submission: string;
    document_type: string;
    submission_date: string;
    submission_text: string;
    langue: string;
    total_score: number;
    passed: boolean;
    graded_at: string;
    student_feedback: string;
    phase_evaluations: PhaseEvaluation[];
    critical_errors: string[];
}

export const useReportDetails = (sessionId: string | null) => {
    const [report, setReport] = useState<ReportDetails | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!sessionId) {
            setReport(null);
            return;
        }

        const fetchDetails = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await api.get(`/student/reports/${sessionId}`);
                setReport(response.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to load report details.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchDetails();
    }, [sessionId]);

    return { report, isLoading, error };
};