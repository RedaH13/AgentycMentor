import { useState, useEffect } from 'react';
import api from '@/lib/api';

export interface StudentReport {
    SessionID: string;
    Subject_Submission: string;
    DocumentType: string;
    SubmissionDate: string;
    TotalScore: number | null;
    Passed: boolean | null;
    ApprovalStatus: string | null;
}

export const useMyReports = () => {
    const [reports, setReports] = useState<StudentReport[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchReports = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Calls FastAPI endpoint
            const response = await api.get('/student/reports');
            setReports(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load your reports.');
        } finally {
            setIsLoading(false);
        }
    };

    // auto Fetch when the hook is first used
    useEffect(() => {
        fetchReports();
    }, []);

    return { reports, isLoading, error, refetch: fetchReports };
};