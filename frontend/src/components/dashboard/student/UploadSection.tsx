"use client";

import { useRef } from "react";
import { UploadCloud } from "lucide-react";

interface UploadSectionProps {
    status: "idle" | "uploading";
    onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function UploadSection({ status, onFileSelect }: UploadSectionProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);

    return (
        <div
            className={`border-2 border-dashed rounded-[2rem] p-12 text-center transition-all duration-300 ${status === "uploading"
                    ? "border-zinc-300 bg-zinc-50/80"
                    : "border-zinc-200 hover:border-zinc-300 cursor-pointer bg-zinc-50/30 hover:bg-zinc-50/80"
                }`}
            onClick={() => status === "idle" && fileInputRef.current?.click()}
        >
            <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={onFileSelect}
                accept=".pdf,.png,.jpg,.jpeg"
            />
            <UploadCloud
                className={`w-12 h-12 mx-auto mb-5 transition-colors ${status === "uploading" ? "text-sky-500 animate-pulse" : "text-zinc-400"
                    }`}
            />
            <p className="text-lg font-serif font-medium text-zinc-900 tracking-tight">
                {status === "uploading"
                    ? "Extracting text via OCR..."
                    : "Click to upload or drag and drop"}
            </p>
            <p className="text-sm font-sans text-zinc-500 mt-2">
                PDF, PNG, JPG (max 10MB)
            </p>
        </div>
    );
}