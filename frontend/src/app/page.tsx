"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-zinc-50 p-4 sm:p-8 antialiased selection:bg-zinc-200">
      <div className="max-w-4xl w-full text-center px-6 py-16 sm:p-16 bg-white rounded-[2rem] shadow-sm border border-zinc-100">

        {/* Header Section */}
        <h1 className="text-4xl sm:text-5xl font-serif text-zinc-900 mb-6 tracking-tight">
          AgentycMentor Platform
        </h1>
        <p className="text-lg text-zinc-600 mb-12 max-w-2xl mx-auto leading-relaxed font-serif">
          This Multi-Agent System leverages{" "}
          <span className="font-medium text-zinc-900">multi‑agent AI</span> to
          revolutionize academic evaluation. Intelligent agents collaborate to
          automate grading, deliver personalized feedback, and provide professors
          with real‑time insights.
        </p>

        {/* Features Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left mb-12">
          {/* Feature 1 - Subtle Sky Blue */}
          <div className="p-6 rounded-2xl bg-sky-50/40 border border-sky-100/50 transition-colors hover:bg-sky-50/80">
            <h3 className="font-serif text-sky-900 mb-2 font-medium">Autonomous Agents</h3>
            <p className="text-sm font-serif text-sky-800/80 leading-relaxed">
              Each agent specializes in tasks such as grading, analytics, or
              feedback, working together to form a dynamic ecosystem.
            </p>
          </div>

          {/* Feature 2 - Subtle Emerald Green */}
          <div className="p-6 rounded-2xl bg-emerald-50/40 border border-emerald-100/50 transition-colors hover:bg-emerald-50/80">
            <h3 className="font-serif text-emerald-900 mb-2 font-medium">AI‑Driven Adaptability</h3>
            <p className="text-sm font-serif text-emerald-800/80 leading-relaxed">
              The system learns from interactions, adapting to diverse teaching
              styles and student needs for personalized outcomes.
            </p>
          </div>

          {/* Feature 3 - Subtle Violet */}
          <div className="p-6 rounded-2xl bg-violet-50/40 border border-violet-100/50 transition-colors hover:bg-violet-50/80">
            <h3 className="font-serif text-violet-900 mb-2 font-medium">Transparent Collaboration</h3>
            <p className="text-sm font-serif text-violet-800/80 leading-relaxed">
              Professors and students engage through intelligent workflows,
              supported by clear, AI‑powered analytics dashboards.
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-3 bg-zinc-900 text-white rounded-full shadow-sm hover:bg-zinc-800 hover:shadow transition-all font-sans font-medium text-sm text-center"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="w-full sm:w-auto px-8 py-3 bg-white border border-zinc-200 text-zinc-900 rounded-full hover:border-zinc-300 hover:bg-zinc-50 transition-all font-sans font-medium text-sm text-center"
          >
            Register
          </Link>
        </div>

        {/* Footer Note */}
        <p className="mt-16 text-sm font-serif text-zinc-400">
          Step into the future of education with intelligent multi‑agent systems.
        </p>
      </div>
    </main>
  );
}