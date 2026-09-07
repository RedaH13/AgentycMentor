"use client";

import { FileText, Clock, CheckCircle, XCircle, ChevronRight, FileSearch } from "lucide-react";
import { useMyReports } from "@/hooks/useMyReports";

export default function ReportsList() {
    const { reports, isLoading, error } = useMyReports();

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20 text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mr-3"></div>
                Loading your reports...
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
                <FileSearch className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">No submissions yet</h3>
                <p className="text-sm text-gray-500 mt-1">Upload your first assignment to get started.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Assignment</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date Submitted</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Grade</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {reports.map((report) => {
                            const isApproved = report.ApprovalStatus === 'Approved';
                            const isPending = !isApproved;

                            return (
                                <tr key={report.SessionID} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                                                <FileText className="w-4 h-4" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">{report.Subject_Submission}</p>
                                                <p className="text-xs text-gray-500">{report.DocumentType}</p>
                                            </div>
                                        </div>
                                    </td>

                                    <td className="px-6 py-4">
                                        <p className="text-sm text-gray-600">
                                            {new Date(report.SubmissionDate).toLocaleDateString(undefined, {
                                                year: 'numeric', month: 'short', day: 'numeric'
                                            })}
                                        </p>
                                    </td>

                                    <td className="px-6 py-4">
                                        {isPending ? (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                                                <Clock className="w-3.5 h-3.5" />
                                                Pending Review
                                            </span>
                                        ) : report.Passed ? (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                                                <CheckCircle className="w-3.5 h-3.5" />
                                                Passed
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
                                                <XCircle className="w-3.5 h-3.5" />
                                                Needs Revision
                                            </span>
                                        )}
                                    </td>

                                    <td className="px-6 py-4">
                                        {isPending ? (
                                            <span className="text-sm text-gray-400 italic">--</span>
                                        ) : (
                                            <span className="text-sm font-semibold text-gray-900">
                                                {report.TotalScore} <span className="text-gray-400 font-normal">/ 15</span>
                                            </span>
                                        )}
                                    </td>

                                    <td className="px-6 py-4 text-right">
                                        <button
                                            disabled={isPending}
                                            className={`inline-flex items-center gap-1 text-sm font-medium transition-colors ${isPending
                                                ? 'text-gray-300 cursor-not-allowed'
                                                : 'text-blue-600 hover:text-blue-700'
                                                }`}
                                        >
                                            View Report
                                            <ChevronRight className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}