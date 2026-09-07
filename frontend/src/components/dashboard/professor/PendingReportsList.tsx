"use client";

import { usePendingReports } from "@/hooks/usePendingReports";
import { Clock, FileText, AlertCircle, ChevronRight, Inbox, User } from "lucide-react";

interface PendingReportsListProps {
    onSelectReport: (report: any) => void;
}

export default function PendingReportsList({ onSelectReport }: PendingReportsListProps) {
    const { reports, isLoading, error } = usePendingReports();

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20 text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mr-3"></div>
                Loading pending reviews...
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-sm text-red-600 bg-red-50 rounded-md">
                {error}
            </div>
        );
    }

    if (reports.length === 0) {
        return (
            <div className="text-center py-20 bg-white border border-gray-100 rounded-xl shadow-sm">
                <Inbox className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">All Caught Up!</h3>
                <p className="text-sm text-gray-500 mt-1">There are no pending submissions awaiting your review.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="p-5 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Needs Review</h2>
                <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold">
                    {reports.length} Pending
                </span>
            </div>
            <div className="divide-y divide-gray-100">
                {reports.map((report) => (
                    <div key={report.session_id} className="p-6 hover:bg-gray-50 transition-colors flex flex-col sm:flex-row gap-6 items-start sm:items-center justify-between">
                        <div className="flex-1 space-y-4">

                            {/* NEW: Student Name and Subject Header */}
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
                            </div>

                            <div className="flex items-center gap-3">
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                                    <FileText className="w-3.5 h-3.5" />
                                    {report.langue}
                                </span>
                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500">
                                    <Clock className="w-3.5 h-3.5" />
                                    Generated: {report.generated_at ? new Date(report.generated_at).toLocaleDateString() : 'N/A'}
                                </span>
                            </div>

                            <div>
                                <p className="text-sm text-gray-900 font-medium mb-1 line-clamp-1">
                                    AI Summary Preview:
                                </p>
                                <p className="text-sm text-gray-600 line-clamp-2">
                                    {report.professor_summary}
                                </p>
                            </div>

                            {report.pedagogical_warning && (
                                <div className="flex items-start gap-1.5 text-xs text-amber-700 font-medium">
                                    <AlertCircle className="w-4 h-4 shrink-0" />
                                    <span className="line-clamp-1">Flagged: {report.pedagogical_warning}</span>
                                </div>
                            )}
                        </div>

                        <button
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-zinc-900 rounded-lg hover:bg-zinc-800 transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-zinc-900 shrink-0"
                            onClick={() => onSelectReport(report)}
                        >
                            Review & Approve
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}