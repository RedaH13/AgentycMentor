"use client";

import { useRef, useState } from "react";
import { UploadCloud, Wand2, Sparkles, Cloud, Cpu } from "lucide-react";

interface UploadSectionProps {
    status: "idle" | "uploading";
    onFileSelect: (file: File, engine: string) => void;
}

export default function UploadSection({ status, onFileSelect }: UploadSectionProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedEngine, setSelectedEngine] = useState("auto");

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            onFileSelect(e.target.files[0], selectedEngine);
        }
    };

    const engines = [
        { id: "auto", name: "Smart Auto", icon: Wand2, desc: "Best balance" },
        { id: "gemini", name: "Gemini Vision", icon: Sparkles, desc: "Highest accuracy" },
        { id: "ocrspace", name: "OCR.Space", icon: Cloud, desc: "Cloud fallback" },
        { id: "tesseract", name: "Tesseract", icon: Cpu, desc: "Local fast OCR" },
    ];

    return (
        <div className="space-y-6">
            {/* Engine Selection Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {engines.map((eng) => {
                    const Icon = eng.icon;
                    const isActive = selectedEngine === eng.id;
                    return (
                        <button
                            key={eng.id}
                            onClick={() => setSelectedEngine(eng.id)}
                            disabled={status === "uploading"}
                            className={`p-4 rounded-2xl border text-left transition-all ${isActive
                                    ? "bg-zinc-900 border-zinc-900 shadow-md text-white"
                                    : "bg-zinc-50/50 border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50 text-zinc-600 disabled:opacity-50"
                                }`}
                        >
                            <Icon className={`w-5 h-5 mb-2 ${isActive ? "text-white" : "text-zinc-500"}`} />
                            <p className={`text-sm font-bold ${isActive ? "text-white" : "text-zinc-900"}`}>{eng.name}</p>
                            <p className={`text-xs mt-0.5 ${isActive ? "text-zinc-300" : "text-zinc-500"}`}>{eng.desc}</p>
                        </button>
                    );
                })}
            </div>

            {/* Upload Area */}
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
                    onChange={handleFileChange}
                    accept=".pdf,.png,.jpg,.jpeg"
                />
                <UploadCloud
                    className={`w-12 h-12 mx-auto mb-5 transition-colors ${status === "uploading" ? "text-sky-500 animate-pulse" : "text-zinc-400"
                        }`}
                />
                <p className="text-lg font-serif font-medium text-zinc-900 tracking-tight">
                    {status === "uploading"
                        ? `Extracting text via ${engines.find(e => e.id === selectedEngine)?.name}...`
                        : "Click to upload or drag and drop"}
                </p>
                <p className="text-sm font-sans text-zinc-500 mt-2">PDF, PNG, JPG (max 10MB)</p>
            </div>
        </div>
    );
}