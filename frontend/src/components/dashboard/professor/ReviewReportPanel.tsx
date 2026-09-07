"use client";

import { useState } from "react";
import api from "@/lib/api";
import { PendingReport, PhaseEvaluation } from "@/hooks/usePendingReports";
import { ArrowLeft, CheckCircle, Save, AlertCircle, User, FileText, Target } from "lucide-react";

interface ReviewReportPanelProps {
    report: PendingReport;
    onBack: () => void;
    onSuccess: () => void;
}

export default function ReviewReportPanel({ report, onBack, onSuccess }: ReviewReportPanelProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Text fields
    const [summary, setSummary] = useState(report.professor_summary || "");
    const [warning, setWarning] = useState(report.pedagogical_warning || "");
    const [draftReport, setDraftReport] = useState(report.student_draft_report || "");
    const [observations, setObservations] = useState("");

    // Grades & Errors
    const [phases, setPhases] = useState<PhaseEvaluation[]>(report.phase_evaluations || []);
    const [criticalErrors, setCriticalErrors] = useState<string>((report.critical_errors || []).join("\n"));

    const isEdited =
        summary !== report.professor_summary ||
        warning !== report.pedagogical_warning ||
        draftReport !== report.student_draft_report ||
        observations.trim() !== "" ||
        JSON.stringify(phases) !== JSON.stringify(report.phase_evaluations) ||
        criticalErrors !== (report.critical_errors || []).join("\n");

    const updatePhase = (index: number, field: keyof PhaseEvaluation, value: any) => {
        const newPhases = [...phases];
        newPhases[index] = { ...newPhases[index], [field]: value };
        setPhases(newPhases);
    };

    const handleApprove = async () => {
        setIsSubmitting(true);
        setError(null);
        try {
            if (isEdited) {
                await api.put(`/professor/reports/${report.session_id}/revise`, {
                    professor_summary: summary,
                    pedagogical_warning: warning,
                    student_draft_report: draftReport,
                    professor_observations: observations,
                    phase_evaluations: phases,
                    critical_errors: criticalErrors.split("\n").filter(e => e.trim() !== ""),
                });
            } else {
                await api.post(`/professor/reports/${report.session_id}/approve`);
            }
            onSuccess();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to approve report.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="bg-white rounded-[2rem] border border-zinc-200 shadow-sm overflow-hidden animate-in fade-in duration-300 antialiased">
            {/* Header */}
            <div className="p-6 sm:p-8 border-b border-zinc-100 bg-zinc-50/50 flex items-center gap-5">
                <button
                    onClick={onBack}
                    className="p-3 text-zinc-400 hover:text-zinc-900 hover:bg-zinc-200/50 rounded-full transition-colors"
                >
                    <ArrowLeft className="w-5 h-5" />
                </button>
                <div>
                    <h2 className="text-xl font-serif font-bold text-zinc-900 flex items-center gap-2">
                        <User className="w-5 h-5 text-zinc-400" />
                        {report.student_name}
                    </h2>
                    <p className="text-sm font-sans text-zinc-500 font-medium flex items-center gap-1.5 mt-1">
                        <FileText className="w-4 h-4" />
                        {report.subject_submission} • {report.document_type} • {report.langue}
                    </p>
                </div>
            </div>

            <div className="p-6 sm:p-10 space-y-12">
                {error && (
                    <div className="p-4 flex gap-3 items-center text-sm font-sans text-red-800 bg-red-50/50 border border-red-100 rounded-2xl">
                        <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
                        <p>{error}</p>
                    </div>
                )}

                {/* --- GRADING SECTION --- */}
                <div className="space-y-6">
                    <h3 className="text-sm font-sans font-bold text-zinc-900 uppercase tracking-wider flex items-center gap-2 border-b border-zinc-100 pb-3">
                        <Target className="w-4 h-4 text-sky-600" />
                        C2PCT Phase Evaluations
                    </h3>
                    <div className="grid gap-6">
                        {phases.map((phase, index) => (
                            <div key={index} className="flex flex-col lg:flex-row gap-6 p-6 bg-zinc-50/40 border border-zinc-100 rounded-[1.5rem] items-start transition-colors hover:bg-zinc-50/80">
                                <div className="w-full lg:w-1/3">
                                    <p className="text-base font-serif font-bold text-zinc-900">{phase.phase_name}</p>
                                    <div className="mt-3 flex flex-col gap-2">
                                        <label className="text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wide">
                                            Score
                                        </label>
                                        <select
                                            value={phase.score}
                                            onChange={(e) => updatePhase(index, 'score', parseInt(e.target.value))}
                                            className="p-3 text-base font-sans font-medium bg-white border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all shadow-sm w-32"
                                        >
                                            {[0, 1, 2, 3].map(num => (
                                                <option key={num} value={num}>{num} / 3</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                                <div className="w-full lg:w-2/3">
                                    <textarea
                                        rows={4}
                                        value={phase.justification}
                                        onChange={(e) => updatePhase(index, 'justification', e.target.value)}
                                        className="w-full p-4 text-base font-sans text-zinc-900 bg-white border border-zinc-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all shadow-sm resize-y leading-relaxed placeholder:text-zinc-400"
                                        placeholder="Provide justification for this score..."
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* --- FEEDBACK SECTION --- */}
                <div className="space-y-8">
                    <h3 className="text-sm font-sans font-bold text-zinc-900 uppercase tracking-wider border-b border-zinc-100 pb-3">
                        Report Content
                    </h3>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="space-y-3">
                            <label className="block text-base font-serif font-medium text-zinc-900">
                                Professor Summary
                            </label>
                            <textarea
                                rows={7}
                                value={summary}
                                onChange={(e) => setSummary(e.target.value)}
                                className="w-full p-5 text-base font-sans text-zinc-900 bg-zinc-50/50 border border-zinc-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all leading-relaxed"
                            />
                        </div>

                        <div className="space-y-3">
                            <label className="flex items-center gap-2 text-base font-serif font-medium text-amber-900">
                                <AlertCircle className="w-4 h-4 text-amber-600" />
                                Pedagogical Warnings
                            </label>
                            <textarea
                                rows={7}
                                value={warning}
                                onChange={(e) => setWarning(e.target.value)}
                                className="w-full p-5 text-base font-sans text-amber-900 bg-amber-50/30 border border-amber-200/60 rounded-2xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 transition-all leading-relaxed"
                            />
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="block text-base font-serif font-medium text-red-900">
                            Critical Errors (One per line)
                        </label>
                        <textarea
                            rows={5}
                            value={criticalErrors}
                            onChange={(e) => setCriticalErrors(e.target.value)}
                            className="w-full p-5 text-base font-sans text-red-900 bg-red-50/30 border border-red-200/60 rounded-2xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-400 transition-all placeholder:text-red-300 leading-relaxed"
                            placeholder="e.g. Failed to convert mm to cm..."
                        />
                    </div>

                    <div className="space-y-3">
                        <label className="block text-base font-serif font-medium text-zinc-900">
                            Student Draft Report
                        </label>
                        <textarea
                            rows={10}
                            value={draftReport}
                            onChange={(e) => setDraftReport(e.target.value)}
                            className="w-full p-6 text-base font-sans text-zinc-900 bg-zinc-50/50 border border-zinc-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-400 transition-all leading-relaxed"
                        />
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="p-6 sm:p-8 border-t border-zinc-100 bg-zinc-50/50 flex flex-col sm:flex-row justify-end gap-4">
                <button
                    onClick={onBack}
                    disabled={isSubmitting}
                    className="px-8 py-3 text-sm font-sans font-medium text-zinc-700 bg-white border border-zinc-200 rounded-full hover:bg-zinc-50 hover:border-zinc-300 transition-all shadow-sm w-full sm:w-auto"
                >
                    Cancel
                </button>
                <button
                    onClick={handleApprove}
                    disabled={isSubmitting}
                    className="inline-flex justify-center items-center gap-2 px-8 py-3 text-sm font-sans font-medium text-white bg-zinc-900 rounded-full hover:bg-zinc-800 hover:shadow transition-all w-full sm:w-auto focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-zinc-900"
                >
                    {isSubmitting ? "Saving..." : isEdited ? <><Save className="w-4 h-4" /> Save Revisions</> : <><CheckCircle className="w-4 h-4" /> Approve As-Is</>}
                </button>
            </div>
        </div>
    );
}