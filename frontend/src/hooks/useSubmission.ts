import { useState } from "react";
import api from "@/lib/api";
import { UploadResponse } from "@/types/student";

type SubmissionStatus = "idle" | "uploading" | "verifying" | "submitting" | "done";

export const useSubmission = () => {
    const [status, setStatus] = useState<SubmissionStatus>("idle");
    const [error, setError] = useState<string | null>(null);

    // State to hold the backend response during HIL pause
    const [sessionId, setSessionId] = useState<string>("");
    const [extractedText, setExtractedText] = useState<string>("");
    const [langue, setLangue] = useState<string>("Unknown");

    const parseApiError = (err: any, defaultMsg: string): string => {
        if (err.response?.data?.detail) {
            const detail = err.response.data.detail;
            if (Array.isArray(detail)) {
                return detail.map(d => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(' | ');
            }
            if (typeof detail === 'string') {
                return detail;
            }
        }
        return defaultMsg;
    };

    // Upload the file to trigger OCR
    const uploadSubmission = async (file: File, engine: string) => {
        setStatus("uploading");
        setError(null);
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("engine", engine);

            const response = await api.post<UploadResponse>("/student/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setSessionId(response.data.session_id);
            setExtractedText(response.data.data.extracted_text);
            setLangue(response.data.langue);
            setStatus("verifying");
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to upload and process file.");
            setStatus("idle");
        }
    };

    // Send the verified text to resume LangGraph
    const verifyText = async (finalText: string, finalLangue: string) => {
        setStatus('submitting');
        setError(null);
        try {
            const payload = {
                session_id: sessionId,
                final_confirmed_text: finalText,
                langue: finalLangue,
            };

            await api.post(`/student/${sessionId}/verify`, payload);

            setStatus('done');
        } catch (err: any) {
            setError(parseApiError(err, 'Failed to resume pipeline.'));
            setStatus('verifying');
        }
    };

    const reset = () => {
        setStatus("idle");
        setSessionId("");
        setExtractedText("");
        setLangue("Unknown");
        setError(null);
    };

    return {
        status,
        error,
        sessionId,
        extractedText,
        langue,
        uploadSubmission,
        verifyText,
        reset,
    };
};
