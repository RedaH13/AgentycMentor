"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { User, LogOut } from "lucide-react";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

import UploadSection from "@/components/dashboard/student/UploadSection";
import VerificationSection from "@/components/dashboard/student/VerificationSection";
import SubmissionStatus from "@/components/dashboard/student/SubmissionStatus";
import { useSubmission } from "@/hooks/useSubmission";
import ReportsList from "@/components/dashboard/student/ReportsList";
import ReportDetailView from "@/components/dashboard/student/ReportDetailView";

export default function StudentDashboard() {
    const { logout, fullName } = useAuth();
    const { status, sessionId, extractedText, langue, error, uploadSubmission, verifyText, reset } = useSubmission();

    const [activeTab, setActiveTab] = useState<"new" | "reports">("new");
    const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            uploadSubmission(e.target.files[0]);
        }
    };

    return (
        <ProtectedRoute allowedRoles={["student"]}>
            <div className="min-h-screen bg-gray-50 flex flex-col">
                {/* Navbar */}
                <nav className="w-full px-8 py-3 bg-white border-b border-gray-100 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-zinc-900 rounded-lg flex items-center justify-center">
                            <span className="text-white font-serif font-bold text-lg leading-none">AM</span>
                        </div>
                        <span className="text-xl font-serif font-semibold text-zinc-900 tracking-tight">AgentycMentor</span>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-500">
                                <User className="w-5 h-5" />
                            </div>
                            <div className="hidden md:block text-left">
                                <p className="text-sm font-semibold text-gray-900 leading-tight truncate max-w-[150px]">
                                    {fullName || 'Loading...'}
                                </p>
                                <p className="text-xs text-gray-500 font-medium">Student Space</p>
                            </div>
                        </div>

                        <div className="w-px h-8 bg-gray-200 hidden sm:block"></div>

                        <button
                            onClick={logout}
                            className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors flex items-center gap-2"
                        >
                            <LogOut className="w-4 h-4" />
                            Sign Out
                        </button>
                    </div>
                </nav>

                {/* Main Content Area */}
                <main className="flex-1 w-full max-w-5xl mx-auto px-6 py-8">

                    {/* Tabs */}
                    <div className="flex space-x-1 bg-gray-100/50 p-1 rounded-lg w-fit mb-8 border border-gray-200">
                        <button
                            onClick={() => setActiveTab("new")}
                            className={`px-6 py-2 text-sm font-medium rounded-md transition-all ${activeTab === "new"
                                ? "bg-white text-gray-900 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                                }`}
                        >
                            New Submission
                        </button>
                        <button
                            onClick={() => setActiveTab("reports")}
                            className={`px-6 py-2 text-sm font-medium rounded-md transition-all ${activeTab === "reports"
                                ? "bg-white text-gray-900 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                                }`}
                        >
                            My Reports
                        </button>
                    </div>

                    {/* Content Rendering based on Tab */}
                    {activeTab === "reports" ? (
                        selectedReportId ? (
                            <ReportDetailView
                                sessionId={selectedReportId}
                                onBack={() => setSelectedReportId(null)}
                            />
                        ) : (
                            <ReportsList onViewReport={setSelectedReportId} />
                        )
                    ) : (
                        < div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
                            {error && (
                                <div className="mb-6 p-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg">
                                    {error}
                                </div>
                            )}

                            {/* Upload Section (idle or uploading) */}
                            {(status === 'idle' || status === 'uploading') && (
                                <UploadSection
                                    status={status}
                                    onFileSelect={handleFileSelect}
                                />
                            )}

                            {/* Verification Section */}
                            {status === 'verifying' && (
                                <VerificationSection
                                    initialText={extractedText}
                                    initialLangue={langue}
                                    onVerify={verifyText}
                                    onCancel={reset}
                                />
                            )}

                            {/* Submission Status Section */}
                            {(status === 'submitting' || status === 'done') && (
                                <SubmissionStatus status={status} onReset={reset} />
                            )}
                        </div>
                    )}
                </main>
            </div >
        </ProtectedRoute >
    );
}