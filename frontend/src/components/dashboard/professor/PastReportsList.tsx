"use client";

import { usePastReports } from "@/hooks/usePastReports";
import { Clock, FileText, CheckCircle, ChevronRight, FileCheck, User } from "lucide-react";
import { PendingReport } from "@/hooks/usePendingReports";

interface PastReportsListProps {
    onSelectReport: (report: PendingReport) => void;
}

export default function PastReportsList({ onSelectReport }: PastReportsListProps) {
    const { reports, isLoading, error } = usePastReports();

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20 text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mr-3"></div>
                Loading past reviews...
            </div>
        );
    }

    if (error) {
        return <div className="p-4 text-sm text-red-600 bg-red-50 rounded-md">{error}</div>;
    }

    if (reports.length === 0) {
        return (
            <div className="text-center py-20 bg-white border border-gray-100 rounded-xl shadow-sm">
                <FileCheck className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">No Past Reviews</h3>
                <p className="text-sm text-gray-500 mt-1">You haven't approved any reports yet.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="p-5 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Previously Approved</h2>
                <span className="px-2.5 py-0.5 rounded-full bg-green-100 text-green-800 text-xs font-semibold">
                    {reports.length} Completed
                </span>
            </div>
            <div className="divide-y divide-gray-100">
                {reports.map((report) => (
                    <div key={report.session_id} className="p-6 hover:bg-gray-50 transition-colors flex flex-col sm:flex-row gap-6 items-start sm:items-center justify-between">
                        <div className="flex-1 space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2 text-zinc-900">
                                    <div className="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center border border-zinc-200">
                                        <User className="w-4 h-4 text-zinc-600" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold leading-tight">{report.student_name}</p>
                                        <p className="text-xs text-zinc-500 font-medium">
                                            {report.subject_submission} • {report.document_type}
                                        </p>
                                    </div>
                                </div>
                                <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                                    <CheckCircle className="w-3.5 h-3.5" />
                                    Approved
                                </span>
                            </div>

                            <div className="flex items-center gap-3">
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                                    <FileText className="w-3.5 h-3.5" />
                                    {report.langue}
                                </span>
                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500">
                                    <Clock className="w-3.5 h-3.5" />
                                    Approved on: {report.generated_at ? new Date(report.generated_at).toLocaleDateString() : 'N/A'}
                                </span>
                            </div>

                            <div>
                                <p className="text-sm text-gray-600 line-clamp-2">
                                    <span className="font-semibold text-gray-900">Summary: </span>
                                    {report.professor_summary}
                                </p>
                            </div>
                        </div>

                        <button
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-medium text-zinc-700 bg-white border border-zinc-300 rounded-lg hover:bg-zinc-50 transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-zinc-900 shrink-0"
                            onClick={() => onSelectReport(report)}
                        >
                            Edit Revisions
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}