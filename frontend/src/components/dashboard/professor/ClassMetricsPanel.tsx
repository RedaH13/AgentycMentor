"use client";

import { useClassMetrics } from "@/hooks/useClassMetrics";
import { Users, BarChart2, Target, TrendingUp, AlertTriangle, FileCheck } from "lucide-react";

export default function ClassMetricsPanel() {
    const { metrics, isLoading, error } = useClassMetrics();

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20 text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-900 mr-3"></div>
                Analyzing class data...
            </div>
        );
    }

    if (error) {
        return <div className="p-4 text-sm text-red-600 bg-red-50 rounded-md">{error}</div>;
    }

    if (!metrics || metrics.total_submissions === 0) {
        return (
            <div className="text-center py-20 bg-white border border-gray-100 rounded-[2rem] shadow-sm">
                <BarChart2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">No Data Available</h3>
                <p className="text-sm text-gray-500 mt-1">Approve some submissions to see class metrics.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Top Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white border border-zinc-200 rounded-[1.5rem] shadow-sm flex items-center gap-4">
                    <div className="p-4 bg-zinc-50 rounded-full"><FileCheck className="w-6 h-6 text-zinc-700" /></div>
                    <div>
                        <p className="text-sm font-bold text-zinc-500 uppercase tracking-wider">Total Evaluated</p>
                        <p className="text-2xl font-black text-zinc-900">{metrics.total_submissions}</p>
                    </div>
                </div>
                <div className="p-6 bg-white border border-zinc-200 rounded-[1.5rem] shadow-sm flex items-center gap-4">
                    <div className="p-4 bg-blue-50 rounded-full"><Target className="w-6 h-6 text-blue-600" /></div>
                    <div>
                        <p className="text-sm font-bold text-zinc-500 uppercase tracking-wider">Class Average</p>
                        <p className="text-2xl font-black text-zinc-900">{metrics.average_score} <span className="text-base text-zinc-400 font-medium">/ 15</span></p>
                    </div>
                </div>
                <div className="p-6 bg-white border border-zinc-200 rounded-[1.5rem] shadow-sm flex items-center gap-4">
                    <div className="p-4 bg-green-50 rounded-full"><TrendingUp className="w-6 h-6 text-green-600" /></div>
                    <div>
                        <p className="text-sm font-bold text-zinc-500 uppercase tracking-wider">Pass Rate</p>
                        <p className="text-2xl font-black text-zinc-900">{metrics.pass_rate}%</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Phase Breakdown */}
                <div className="p-6 sm:p-8 bg-white border border-zinc-200 rounded-[2rem] shadow-sm">
                    <h3 className="text-lg font-serif font-bold text-zinc-900 mb-6">C2PCT Phase Averages</h3>
                    <div className="space-y-5">
                        {metrics.phase_averages.map((phase, idx) => (
                            <div key={idx}>
                                <div className="flex justify-between items-end mb-1">
                                    <span className="text-sm font-bold text-zinc-700">{phase.phase_name}</span>
                                    <span className="text-sm font-black text-zinc-900">{phase.average_score} <span className="text-zinc-400 font-medium">/ 3</span></span>
                                </div>
                                <div className="w-full bg-zinc-100 rounded-full h-2.5">
                                    <div
                                        className="bg-zinc-900 h-2.5 rounded-full transition-all duration-1000"
                                        style={{ width: `${(phase.average_score / 3) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Critical Errors */}
                <div className="p-6 sm:p-8 bg-white border border-zinc-200 rounded-[2rem] shadow-sm">
                    <h3 className="text-lg font-serif font-bold text-zinc-900 mb-6 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                        Most Common Errors
                    </h3>
                    <div className="space-y-4">
                        {metrics.top_errors.length > 0 ? (
                            metrics.top_errors.map((error, idx) => (
                                <div key={idx} className="p-4 bg-amber-50/50 border border-amber-100 rounded-2xl flex gap-4 items-start">
                                    <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-700 font-bold flex items-center justify-center shrink-0 text-sm">
                                        {error.occurrence_count}
                                    </div>
                                    <p className="text-sm font-medium text-amber-900 leading-relaxed pt-1">
                                        {error.error_text}
                                    </p>
                                </div>
                            ))
                        ) : (
                            <p className="text-sm text-zinc-500 italic">No critical errors logged across the class.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}