"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import ProfessorHeader from "@/components/dashboard/professor/ProfessorHeader";
import PendingReportsList from "@/components/dashboard/professor/PendingReportsList";
import ReviewReportPanel from "@/components/dashboard/professor/ReviewReportPanel";
import { PendingReport } from "@/hooks/usePendingReports";

export default function ProfessorDashboard() {
    const { logout, fullName } = useAuth();
    // Track the currently selected report for review
    const [selectedReport, setSelectedReport] = useState<PendingReport | null>(null);

    return (
        <ProtectedRoute allowedRoles={["professor", "admin"]}>
            <div className="min-h-screen bg-gray-50 flex flex-col">
                <ProfessorHeader onLogout={logout} fullName={fullName} />

                <main className="flex-1 w-full max-w-5xl mx-auto px-6 py-8">
                    <div className="mb-8">
                        <h1 className="text-2xl font-serif font-bold text-gray-900">
                            Welcome back, {fullName?.split(' ')[0] || 'Professor'}
                        </h1>
                        <p className="text-sm text-gray-500 mt-1">
                            {selectedReport
                                ? "Reviewing student submission and MAS feedback."
                                : "Here is the latest automated grading from the MAS pipeline."}
                        </p>
                    </div>

                    {/* Conditional Rendering: Show panel if a report is selected, else show the list */}
                    {selectedReport ? (
                        <ReviewReportPanel
                            report={selectedReport}
                            onBack={() => setSelectedReport(null)}
                            onSuccess={() => {
                                setSelectedReport(null);
                                // The list will automatically refetch when re-mounted, 
                                // but you can also pass down a refetch trigger if needed.
                            }}
                        />
                    ) : (
                        <PendingReportsList onSelectReport={setSelectedReport} />
                    )}
                </main>
            </div>
        </ProtectedRoute>
    );
}