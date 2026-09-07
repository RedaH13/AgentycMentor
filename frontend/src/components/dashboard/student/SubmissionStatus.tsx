"use client";

import { useState, useEffect } from "react";
import { CheckCircle, BrainCircuit } from "lucide-react";

interface SubmissionStatusProps {
    status: "submitting" | "done";
    onReset: () => void;
}

const AGENT_STATUSES = [
    "Initializing multi-agent graph...",
    "Transcribing final text...",
    "Analyzing C2PCT pedagogical phases...",
    "Agents debating score justification...",
    "Drafting final feedback report...",
    "Waiting for professor approval..."
];

export default function SubmissionStatus({ status, onReset }: SubmissionStatusProps) {
    const [statusIndex, setStatusIndex] = useState(0);

    // Cycle through the agent statuses every 3.5 seconds while submitting
    useEffect(() => {
        if (status === "submitting") {
            const interval = setInterval(() => {
                setStatusIndex((prev) =>
                    prev < AGENT_STATUSES.length - 1 ? prev + 1 : prev
                );
            }, 3500);
            return () => clearInterval(interval);
        }
    }, [status]);

    return (
        <div className="text-center py-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {status === "submitting" ? (
                <div className="space-y-6 max-w-sm mx-auto">
                    <div className="relative w-16 h-16 mx-auto">
                        {/* Outer spinning ring */}
                        <div className="absolute inset-0 border-4 border-gray-100 border-t-gray-900 rounded-full animate-spin"></div>
                        {/* Inner icon */}
                        <div className="absolute inset-0 flex items-center justify-center text-gray-900">
                            <BrainCircuit className="w-6 h-6 animate-pulse" />
                        </div>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            MAS Evaluation in Progress
                        </h3>
                        {/* Animated text that cycles through the array */}
                        <p className="text-sm text-gray-500 font-mono transition-opacity duration-300">
                            &gt; {AGENT_STATUSES[statusIndex]}
                        </p>
                    </div>
                </div>
            ) : (
                <div className="space-y-4">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                    <h3 className="text-xl font-semibold text-gray-900">
                        Submission Complete
                    </h3>
                    <p className="text-sm text-gray-500 max-w-md mx-auto">
                        Your assignment has been successfully processed by the MAS and is now in the queue for your professor's final review.
                    </p>
                    <button
                        onClick={onReset}
                        className="mt-6 px-6 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                    >
                        Submit Another
                    </button>
                </div>
            )}
        </div>
    );
}