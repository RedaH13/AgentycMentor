"use client";

import { useRef } from "react";
import { useKnowledgeBase } from "@/hooks/useKnowledgeBase";
import { Database, UploadCloud, CheckCircle, AlertCircle } from "lucide-react";

export default function KnowledgeBasePanel() {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { uploadMaterial, isUploading, error, success, setError, setSuccess } = useKnowledgeBase();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            uploadMaterial(e.target.files[0]);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="bg-white rounded-[2rem] border border-zinc-200 p-8 shadow-sm">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
                        <Database className="w-6 h-6" />
                    </div>
                    <h2 className="text-xl font-serif font-bold text-zinc-900">RAG Knowledge Base</h2>
                </div>
                <p className="text-sm text-zinc-500 mb-8 max-w-2xl">
                    Upload course syllabi, specific grading rubrics, or lecture notes. The AI MAS will retrieve these documents to provide hyper-contextualized grading and feedback for your students.
                </p>

                {error && (
                    <div className="mb-6 p-4 flex items-center gap-3 text-sm text-red-800 bg-red-50 border border-red-100 rounded-2xl">
                        <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
                        {error}
                    </div>
                )}

                {success && (
                    <div className="mb-6 p-4 flex items-center gap-3 text-sm text-green-800 bg-green-50 border border-green-100 rounded-2xl">
                        <CheckCircle className="w-5 h-5 text-green-600 shrink-0" />
                        {success}
                    </div>
                )}

                <div
                    className={`border-2 border-dashed rounded-[2rem] p-12 text-center transition-all duration-300 ${isUploading
                        ? "border-indigo-300 bg-indigo-50/50"
                        : "border-zinc-200 hover:border-indigo-300 cursor-pointer bg-zinc-50/50 hover:bg-indigo-50/30"
                        }`}
                    onClick={() => !isUploading && fileInputRef.current?.click()}
                >
                    <input
                        type="file"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        accept=".pdf"
                    />
                    <UploadCloud
                        className={`w-12 h-12 mx-auto mb-5 transition-colors ${isUploading ? "text-indigo-500 animate-pulse" : "text-zinc-400"
                            }`}
                    />
                    <p className="text-lg font-serif font-medium text-zinc-900 tracking-tight">
                        {isUploading ? "Chunking and vectorizing document..." : "Click to upload course materials"}
                    </p>
                    <p className="text-sm font-sans text-zinc-500 mt-2">PDF only (Supports rubrics, syllabi, notes)</p>
                </div>
            </div>
        </div>
    );
}