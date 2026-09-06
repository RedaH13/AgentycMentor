"use client";

import { CheckCircle, Edit3 } from "lucide-react";

// We define the shape of our data here so TypeScript can help us later
export interface PendingSubmission {
    id: string;
    studentId: string;
    score: number;
    maxScore: number;
    warningFlag: string | null;
}

interface PendingSubmissionsTableProps {
    submissions: PendingSubmission[];
    onApprove: (id: string) => void;
    onRevise: (id: string) => void;
}

export default function PendingSubmissionsTable({ submissions, onApprove, onRevise }: PendingSubmissionsTableProps) {
    if (submissions.length === 0) {
        return (
            <div className="bg-white border border-gray-100 rounded-lg shadow-sm p-12 text-center text-gray-500">
                No pending submissions awaiting review.
            </div>
        );
    }

    return (
        <div className="bg-white border border-gray-100 rounded-lg shadow-sm overflow-hidden">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="bg-gray-50 border-b border-gray-100 text-xs uppercase tracking-wider text-gray-500 font-medium">
                        <th className="p-4">Session ID</th>
                        <th className="p-4">Student ID</th>
                        <th className="p-4">AI Score</th>
                        <th className="p-4">Warning Flag</th>
                        <th className="p-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="text-sm text-gray-700 divide-y divide-gray-100">
                    {submissions.map((sub) => (
                        <tr key={sub.id} className="hover:bg-gray-50 transition-colors group">
                            <td className="p-4 font-mono text-xs">{sub.id.split('-')[0]}...</td>
                            <td className="p-4">{sub.studentId}</td>
                            <td className="p-4 font-medium">
                                <span className={sub.score >= 10 ? "text-green-600" : "text-red-600"}>
                                    {sub.score} / {sub.maxScore}
                                </span>
                            </td>
                            <td className="p-4">
                                {sub.warningFlag ? (
                                    <span className="px-2 py-1 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-100 rounded">
                                        {sub.warningFlag}
                                    </span>
                                ) : (
                                    <span className="text-gray-400">None</span>
                                )}
                            </td>
                            <td className="p-4 text-right">
                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => onRevise(sub.id)}
                                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded hover:bg-gray-50"
                                    >
                                        <Edit3 className="w-3 h-3" /> Revise
                                    </button>
                                    <button
                                        onClick={() => onApprove(sub.id)}
                                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-gray-900 rounded hover:bg-gray-800"
                                    >
                                        <CheckCircle className="w-3 h-3" /> Approve
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}