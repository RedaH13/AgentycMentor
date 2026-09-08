import { useState } from 'react';
import api from '@/lib/api';

export const useKnowledgeBase = () => {
    const [isUploading, setIsUploading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const uploadMaterial = async (file: File) => {
        setIsUploading(true);
        setError(null);
        setSuccess(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await api.post('/professor/knowledge/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            setSuccess(response.data.message);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to upload material to Knowledge Base.');
        } finally {
            setIsUploading(false);
        }
    };

    return { uploadMaterial, isUploading, error, success, setError, setSuccess };
};