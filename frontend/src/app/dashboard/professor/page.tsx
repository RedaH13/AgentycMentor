"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import ProfessorHeader, { ProfessorTab } from "@/components/dashboard/professor/ProfessorHeader";
import PendingReportsList from "@/components/dashboard/professor/PendingReportsList";
import PastReportsList from "@/components/dashboard/professor/PastReportsList";
import ReviewReportPanel from "@/components/dashboard/professor/ReviewReportPanel";
import { PendingReport } from "@/hooks/usePendingReports";
import ClassMetricsPanel from "@/components/dashboard/professor/ClassMetricsPanel";

export default function ProfessorDashboard() {
    const { logout, fullName } = useAuth();
    const [activeTab, setActiveTab] = useState<ProfessorTab>("pending");

    // Track the currently selected report for review
    const [selectedReport, setSelectedReport] = useState<PendingReport | null>(null);

    return (
        <ProtectedRoute allowedRoles={["professor", "admin"]}>
            <div className="min-h-screen bg-gray-50 flex flex-col">
                <ProfessorHeader
                    onLogout={logout}
                    fullName={fullName}
                    activeTab={activeTab}
                    onTabChange={(tab) => {
                        setActiveTab(tab);
                        setSelectedReport(null);
                    }}
                />

                <main className="flex-1 w-full max-w-5xl mx-auto px-6 py-8">
                    <div className="mb-8">
                        <h1 className="text-2xl font-serif font-bold text-gray-900">
                            Welcome back, {fullName?.split(' ')[0] || 'Professor'}
                        </h1>
                        <p className="text-sm text-gray-500 mt-1">
                            {selectedReport
                                ? "Reviewing student submission and MAS feedback."
                                : activeTab === "past"
                                    ? "Viewing previously approved reports."
                                    : "Here is the latest automated grading from the MAS pipeline."}
                        </p>
                    </div>

                    {/* Conditional Rendering */}
                    {selectedReport ? (
                        <ReviewReportPanel
                            report={selectedReport}
                            onBack={() => setSelectedReport(null)}
                            onSuccess={() => setSelectedReport(null)}
                        />
                    ) : (
                        <>
                            {activeTab === "pending" && <PendingReportsList onSelectReport={setSelectedReport} />}
                            {activeTab === "past" && <PastReportsList onSelectReport={setSelectedReport} />}
                            {activeTab === "metrics" && <ClassMetricsPanel />}
                        </>
                    )}
                </main>
            </div>
        </ProtectedRoute>
    );
}