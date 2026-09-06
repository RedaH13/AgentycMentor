"use client";

import { useState } from "react";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";

import ProfessorHeader from "@/components/dashboard/professor/ProfessorHeader";
import PendingSubmissionsTable, { PendingSubmission } from "@/components/dashboard/professor/PendingSubmissionsTable";

export default function ProfessorDashboard() {
    const { logout, fullName } = useAuth();

    // Placeholder data - we will replace this with a usePendingReports hook next!
    const [submissions, setSubmissions] = useState<PendingSubmission[]>([
        { id: "d8a2-4f1c-b3a1", studentId: "MAS-2026", score: 12, maxScore: 15, warningFlag: null },
        { id: "e7b9-9x2a-c4b2", studentId: "MAS-2027", score: 6, maxScore: 15, warningFlag: "Decomposition Error" },
    ]);

    const handleApprove = (id: string) => {
        console.log("Approving session:", id);
        // API call will go here
    };

    const handleRevise = (id: string) => {
        console.log("Revising session:", id);
        // Navigation or Modal logic will go here
    };

    return (
        <ProtectedRoute allowedRoles={["professor", "admin"]}>
            <div className="min-h-screen bg-gray-50 flex flex-col">

                <ProfessorHeader onLogout={logout} fullName={fullName} />

                <main className="flex-grow p-8">
                    <div className="max-w-6xl mx-auto space-y-6">

                        <div className="flex justify-between items-end mb-6">
                            <div>
                                <h1 className="text-2xl font-semibold text-gray-900 mb-2">
                                    Pending Submissions
                                </h1>
                                <p className="text-sm text-gray-500">
                                    Review, revise, and approve AI-generated evaluations.
                                </p>
                            </div>
                            <div className="text-sm font-medium text-gray-500">
                                <span className="text-gray-900 font-bold">{submissions.length}</span> awaiting review
                            </div>
                        </div>

                        <PendingSubmissionsTable
                            submissions={submissions}
                            onApprove={handleApprove}
                            onRevise={handleRevise}
                        />

                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}