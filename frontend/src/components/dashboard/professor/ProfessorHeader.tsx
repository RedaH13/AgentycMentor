"use client";

import { User, Inbox, BarChart2, Settings, FileCheck } from "lucide-react";

export type ProfessorTab = "pending" | "past" | "metrics" | "settings";

interface ProfessorHeaderProps {
    onLogout: () => void;
    fullName: string | null;
    activeTab: ProfessorTab;
    onTabChange: (tab: ProfessorTab) => void;
}

export default function ProfessorHeader({ onLogout, fullName, activeTab, onTabChange }: ProfessorHeaderProps) {

    // Helper to dynamically style the active tab
    const getTabClass = (tab: ProfessorTab) =>
        activeTab === tab
            ? "flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-900 bg-gray-100 rounded-md transition-colors"
            : "flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors";

    return (
        <nav className="w-full px-8 py-3 bg-white border-b border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
            {/* Left: Brand & Navigation Tabs */}
            <div className="flex items-center gap-8">
                <div className="font-bold text-gray-900 tracking-tight">AgentycMentor</div>
                <div className="hidden sm:flex items-center gap-2">
                    <button
                        onClick={() => onTabChange("pending")}
                        className={getTabClass("pending")}
                    >
                        <Inbox className="w-4 h-4" />
                        Pending Reviews
                    </button>

                    <button
                        onClick={() => onTabChange("past")}
                        className={getTabClass("past")}
                    >
                        <FileCheck className="w-4 h-4" />
                        Past Reviews
                    </button>

                    <button
                        onClick={() => onTabChange("metrics")}
                        className={getTabClass("metrics")}
                    >
                        <BarChart2 className="w-4 h-4" />
                        Class Metrics
                    </button>


                </div>
            </div>

            {/* Right: User Identity & Logout */}
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-900">
                        <User className="w-5 h-5" />
                    </div>
                    <div className="hidden md:block text-left">
                        <p className="text-sm font-semibold text-gray-900 leading-tight truncate max-w-[150px]">
                            {fullName || 'Loading...'}
                        </p>
                        <p className="text-xs text-gray-500 font-medium">Faculty Workspace</p>
                    </div>
                </div>

                <div className="w-px h-8 bg-gray-200 hidden sm:block"></div>

                <button
                    onClick={onLogout}
                    className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
                >
                    Sign Out
                </button>
            </div>
        </nav>
    );
}