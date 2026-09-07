"use client";

import { useReportDetails } from "@/hooks/useReportDetails";
import { ArrowLeft, CheckCircle, XCircle, AlertTriangle, Target, MessageSquare, FileText } from "lucide-react";

interface ReportDetailViewProps {
    sessionId: string;
    onBack: () => void;
}

export default function ReportDetailView({ sessionId, onBack }: ReportDetailViewProps) {
    const { report, isLoading, error } = useReportDetails(sessionId);

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-32 text-zinc-500">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-zinc-900 mb-4"></div>
                <p className="font-medium font-sans">Loading your detailed feedback...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 text-sm text-red-800 bg-red-50 border border-red-200 rounded-2xl flex flex-col items-start gap-4">
                <p>{error}</p>
                <button onClick={onBack} className="text-red-900 font-bold hover:underline flex items-center gap-2">
                    <ArrowLeft className="w-4 h-4" /> Go Back
                </button>
            </div>
        );
    }

    if (!report) return null;

    return (
        <div className="bg-white rounded-[2rem] border border-zinc-200 shadow-sm overflow-hidden animate-in fade-in duration-500 antialiased">
            {/* Header Area */}
            <div className="p-6 sm:p-10 border-b border-zinc-100 bg-zinc-50/50 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="flex items-center gap-5">
                    <button
                        onClick={onBack}
                        className="p-3 text-zinc-400 hover:text-zinc-900 hover:bg-zinc-200/50 rounded-full transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h2 className="text-2xl font-serif font-bold text-zinc-900 tracking-tight">
                            {report.subject_submission} Report
                        </h2>
                        <p className="text-sm font-sans text-zinc-500 font-medium mt-1">
                            {report.document_type} • Submitted on {new Date(report.submission_date).toLocaleDateString()}
                        </p>
                    </div>
                </div>

                {/* Big Score Display */}
                <div className={`flex items-center gap-4 px-6 py-4 rounded-2xl border ${report.passed ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'}`}>
                    {report.passed ? <CheckCircle className="w-8 h-8 text-green-600" /> : <XCircle className="w-8 h-8 text-red-600" />}
                    <div>
                        <p className="text-xs font-bold uppercase tracking-wider opacity-80">Total Score</p>
                        <p className="text-3xl font-black font-sans leading-none mt-1">
                            {report.total_score} <span className="text-lg opacity-50 font-medium">/ 15</span>
                        </p>
                    </div>
                </div>
            </div>

            <div className="p-6 sm:p-10 space-y-12">
                {/* Critical Errors Alert (Only shows if there are errors) */}
                {report.critical_errors && report.critical_errors.length > 0 && (
                    <div className="p-6 bg-red-50/50 border border-red-100 rounded-[1.5rem] space-y-4">
                        <h3 className="text-base font-bold text-red-900 flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                            Critical Errors Identified
                        </h3>
                        <ul className="list-disc list-inside space-y-2 text-sm text-red-800 font-medium leading-relaxed">
                            {report.critical_errors.map((error, idx) => (
                                <li key={idx}>{error}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Main Pedagogical Feedback */}
                <div className="space-y-4">
                    <h3 className="text-sm font-sans font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-2 border-b border-zinc-100 pb-3">
                        <MessageSquare className="w-4 h-4 text-sky-600" />
                        Pedagogical Feedback
                    </h3>
                    <div className="p-6 sm:p-8 bg-zinc-50/40 border border-zinc-100 rounded-[1.5rem] text-zinc-800 text-base font-sans leading-loose whitespace-pre-wrap">
                        {report.student_feedback}
                    </div>
                </div>

                {/* C2PCT Phase Breakdown */}
                <div className="space-y-4">
                    <h3 className="text-sm font-sans font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-2 border-b border-zinc-100 pb-3">
                        <Target className="w-4 h-4 text-sky-600" />
                        C2PCT Skill Evaluation
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {report.phase_evaluations.map((phase, idx) => (
                            <div key={idx} className="p-5 border border-zinc-200 rounded-[1.5rem] flex flex-col justify-between hover:border-zinc-300 transition-colors bg-white">
                                <div>
                                    <h4 className="font-serif font-bold text-zinc-900 mb-2">{phase.phase_name}</h4>
                                    <p className="text-sm text-zinc-600 leading-relaxed mb-4">{phase.justification}</p>
                                </div>
                                <div className="mt-auto pt-4 border-t border-zinc-100 flex justify-between items-center">
                                    <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Score</span>
                                    <span className="text-lg font-black text-zinc-900">{phase.score} <span className="text-sm text-zinc-400 font-medium">/ 3</span></span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Original Submission Text (Hidden by default, optional viewing) */}
                <div className="space-y-4">
                    <details className="group">
                        <summary className="flex items-center gap-2 cursor-pointer text-sm font-bold text-zinc-600 hover:text-zinc-900 transition-colors select-none">
                            <FileText className="w-4 h-4" />
                            View Original Extracted Text
                        </summary>
                        <div className="mt-4 p-5 bg-zinc-100 text-zinc-700 font-mono text-xs rounded-xl whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto">
                            {report.submission_text}
                        </div>
                    </details>
                </div>
            </div>
        </div>
    );
}