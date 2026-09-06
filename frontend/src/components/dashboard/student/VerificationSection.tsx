"use client";

import { useState, useEffect } from "react";
import { FileText } from "lucide-react";

interface VerificationSectionProps {
    initialText: string;
    initialLangue: string;
    onVerify: (text: string, langue: string) => void;
    onCancel: () => void;
}

export default function VerificationSection({
    initialText,
    initialLangue,
    onVerify,
    onCancel,
}: VerificationSectionProps) {
    const [editableText, setEditableText] = useState(initialText);
    const [editableLangue, setEditableLangue] = useState(initialLangue);

    // Sync state if initial props change
    useEffect(() => {
        setEditableText(initialText);
        setEditableLangue(initialLangue);
    }, [initialText, initialLangue]);

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Soft Amber Warning Alert */}
            <div className="flex items-center gap-3 text-sm font-sans font-medium text-amber-800 bg-amber-50/60 p-4 rounded-2xl border border-amber-100/50">
                <FileText className="w-5 h-5 text-amber-600 shrink-0" />
                Action Required: Please review and correct the extracted text below.
            </div>

            <div className="space-y-2">
                <label className="block text-base font-serif font-medium text-zinc-900">
                    Extracted Text
                </label>
                <textarea
                    rows={12}
                    value={editableText}
                    onChange={(e) => setEditableText(e.target.value)}
                    className="w-full p-5 text-sm text-zinc-900 bg-zinc-50/50 border border-zinc-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all font-mono leading-relaxed"
                />
            </div>

            <div className="flex flex-col sm:flex-row justify-end gap-3 pt-6 border-t border-zinc-100">
                <button
                    onClick={onCancel}
                    className="w-full sm:w-auto px-6 py-3 text-sm font-sans font-medium text-zinc-700 bg-white border border-zinc-200 rounded-full hover:bg-zinc-50 hover:border-zinc-300 transition-all shadow-sm"
                >
                    Cancel
                </button>
                <button
                    onClick={() => onVerify(editableText, editableLangue)}
                    className="w-full sm:w-auto px-6 py-3 text-sm font-sans font-medium text-white bg-zinc-900 rounded-full hover:bg-zinc-800 hover:shadow focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-zinc-900 transition-all"
                >
                    Confirm & Submit for Grading
                </button>
            </div>
        </div>
    );
}