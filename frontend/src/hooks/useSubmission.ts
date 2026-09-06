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

    // Upload the file to trigger OCR
    const uploadSubmission = async (file: File) => {
        setStatus("uploading");
        setError(null);
        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await api.post<UploadResponse>("/student/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setSessionId(response.data.session_id);
            setExtractedText(response.data.data.extracted_text);
            setLangue(response.data.langue);
            setStatus("verifying"); // Move to HIL pause
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to upload and process file.");
            setStatus("idle");
        }
    };

    // Send the verified text to resume LangGraph
    const verifyText = async (finalText: string, finalLangue: string) => {
        setStatus("submitting");
        setError(null);
        try {
            await api.post(`/student/${sessionId}/verify`, {
                final_confirmed_text: finalText,
                langue: finalLangue,
            });
            setStatus("done");
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to resume pipeline.");
            setStatus("verifying");
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
