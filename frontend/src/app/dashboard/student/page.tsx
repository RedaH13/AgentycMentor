"use client";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";
import { useSubmission } from "@/hooks/useSubmission";
import { AlertCircle, User, FileText, Settings, History } from "lucide-react";

import UploadSection from "@/components/dashboard/student/UploadSection";
import VerificationSection from "@/components/dashboard/student/VerificationSection";
import SubmissionStatus from "@/components/dashboard/student/SubmissionStatus";

export default function StudentDashboard() {
    const { logout, fullName } = useAuth();
    const {
        status,
        error,
        extractedText,
        langue,
        uploadSubmission,
        verifyText,
        reset,
    } = useSubmission();

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await uploadSubmission(e.target.files[0]);
        }
    };

    return (
        <ProtectedRoute allowedRoles={["student"]}>
            <div className="min-h-screen bg-zinc-50 flex flex-col antialiased selection:bg-zinc-200">

                {/* Minimal Navigation */}
                <nav className="w-full px-8 py-3 bg-white border-b border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
                    {/* Left: Brand & Navigation Tabs */}
                    <div className="flex items-center gap-8">
                        <div className="font-bold text-gray-900 tracking-tight">AgentycMentor</div>
                        <div className="hidden sm:flex items-center gap-2">
                            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-900 bg-gray-100 rounded-md transition-colors">
                                <FileText className="w-4 h-4" />
                                New Submission
                            </button>
                            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors">
                                <History className="w-4 h-4" />
                                My Reports
                            </button>
                            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors">
                                <Settings className="w-4 h-4" />
                                Settings
                            </button>
                        </div>
                    </div>

                    {/* Right: User Identity & Logout */}
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-500">
                                <User className="w-5 h-5" />
                            </div>
                            <div className="hidden md:block text-left">
                                <p className="text-sm font-semibold text-gray-900 leading-tight">{fullName || 'Loading...'}</p>
                                <p className="text-xs text-gray-500 font-mono">Student Space</p>
                            </div>
                        </div>

                        <div className="w-px h-8 bg-gray-200 hidden sm:block"></div>

                        <button
                            onClick={logout}
                            className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
                        >
                            Sign Out
                        </button>
                    </div>
                </nav>

                {/* Main Content */}
                <main className="flex-grow p-4 sm:p-8 flex flex-col items-center">
                    <div className="max-w-3xl w-full mx-auto space-y-6 mt-4 sm:mt-8">
                        <div className="bg-white border border-zinc-100 rounded-[2rem] shadow-sm p-8 sm:p-12">

                            {/* Header */}
                            <div className="mb-10">
                                <h1 className="text-3xl font-serif font-bold tracking-tight text-zinc-900 mb-3">
                                    Submit Assignment
                                </h1>
                                <p className="text-base font-serif text-zinc-500 leading-relaxed">
                                    Upload your work for AI grading. You will have a chance to
                                    verify the extracted text before it is evaluated.
                                </p>
                            </div>

                            {/* Error Alert */}
                            {error && (
                                <div className="mb-8 p-4 flex gap-3 items-center text-sm font-sans text-red-800 bg-red-50/50 border border-red-100 rounded-2xl">
                                    <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
                                    <p>{error}</p>
                                </div>
                            )}

                            {/* Dynamic Sections based on Status */}
                            {(status === "idle" || status === "uploading") && (
                                <UploadSection status={status} onFileSelect={handleFileChange} />
                            )}

                            {status === "verifying" && (
                                <VerificationSection
                                    initialText={extractedText}
                                    initialLangue={langue}
                                    onVerify={verifyText}
                                    onCancel={reset}
                                />
                            )}

                            {(status === "submitting" || status === "done") && (
                                <SubmissionStatus status={status} onReset={reset} />
                            )}
                        </div>
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}