"use client";

import { CheckCircle } from "lucide-react";

interface SubmissionStatusProps {
    status: "submitting" | "done";
    onReset: () => void;
}

export default function SubmissionStatus({ status, onReset }: SubmissionStatusProps) {
    return (
        <div className="text-center py-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {status === "submitting" ? (
                <div className="space-y-6">
                    <div className="w-12 h-12 border-[3px] border-zinc-100 border-t-zinc-900 rounded-full animate-spin mx-auto"></div>
                    <p className="text-lg font-serif font-medium text-zinc-900 tracking-tight">
                        Agents are evaluating your submission...
                    </p>
                </div>
            ) : (
                <div className="space-y-5">
                    <div className="w-20 h-20 bg-emerald-50/40 rounded-full flex items-center justify-center mx-auto border border-emerald-100/50">
                        <CheckCircle className="w-10 h-10 text-emerald-600" />
                    </div>
                    <h3 className="text-2xl font-serif font-bold text-zinc-900 tracking-tight">
                        Submission Complete
                    </h3>
                    <p className="text-base font-serif text-zinc-500 max-w-md mx-auto leading-relaxed">
                        Your assignment has been successfully processed by the MAS and is now pending final approval by your professor.
                    </p>
                    <button
                        onClick={onReset}
                        className="mt-8 px-8 py-3 text-sm font-sans font-medium text-zinc-700 bg-white border border-zinc-200 rounded-full hover:bg-zinc-50 hover:border-zinc-300 transition-all shadow-sm"
                    >
                        Submit Another
                    </button>
                </div>
            )}
        </div>
    );
}