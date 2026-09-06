"use client";

import Link from 'next/link';
import { ArrowRight, BrainCircuit, FileText, CheckCircle2 } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-zinc-50 flex flex-col antialiased selection:bg-zinc-200">
      {/* Minimal Navigation */}
      <nav className="w-full px-6 py-5 flex justify-between items-center border-b border-zinc-200/60 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="text-xl font-serif font-bold text-zinc-900 tracking-tight">
          AgentycMentor
        </div>
        <div className="flex gap-2 sm:gap-4 items-center">
          <Link
            href="/login"
            className="px-4 py-2 text-sm font-sans font-medium text-zinc-600 hover:text-zinc-900 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-5 py-2 text-sm font-sans font-medium text-white bg-zinc-900 rounded-full hover:bg-zinc-800 transition-all shadow-sm"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-grow flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center rounded-full px-4 py-1.5 text-xs font-sans font-medium bg-white text-zinc-700 mb-4 border border-zinc-200 shadow-sm">
            Powered by LangGraph & Generative AI
          </div>

          <h1 className="text-4xl md:text-6xl font-serif font-bold text-zinc-900 tracking-tight leading-[1.15]">
            Elevate educational engineering with multi-agent intelligence.
          </h1>

          <p className="text-lg md:text-xl font-serif text-zinc-600 max-w-2xl mx-auto leading-relaxed mt-6">
            A stateful AI platform that evaluates unstructured assignments using the strict C2PCT pedagogical framework, ensuring rigorous grading and empathetic feedback.
          </p>

          <div className="pt-8 flex justify-center gap-4">
            <Link
              href="/register"
              className="flex items-center gap-2 px-8 py-3 bg-zinc-900 text-white font-sans font-medium rounded-full hover:bg-zinc-800 hover:shadow transition-all group"
            >
              Join as Student or Professor
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
        </div>

        {/* Functionalities Grid */}
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mt-24">

          {/* Card 1 - Sky Blue Theme */}
          <div className="p-8 rounded-[2rem] bg-sky-50/40 border border-sky-100/50 transition-colors hover:bg-sky-50/80">
            <div className="w-12 h-12 bg-sky-100/50 flex items-center justify-center rounded-2xl mb-6 border border-sky-100">
              <FileText className="w-6 h-6 text-sky-700" />
            </div>
            <h3 className="text-lg font-serif font-medium text-sky-900 mb-3">
              Smart OCR Ingestion
            </h3>
            <p className="text-sm font-serif text-sky-800/80 leading-relaxed">
              Upload handwritten diagrams or digital PDFs. Our Human-in-the-Loop breakpoint ensures perfect text transcription before grading begins.
            </p>
          </div>

          {/* Card 2 - Emerald Green Theme */}
          <div className="p-8 rounded-[2rem] bg-emerald-50/40 border border-emerald-100/50 transition-colors hover:bg-emerald-50/80">
            <div className="w-12 h-12 bg-emerald-100/50 flex items-center justify-center rounded-2xl mb-6 border border-emerald-100">
              <BrainCircuit className="w-6 h-6 text-emerald-700" />
            </div>
            <h3 className="text-lg font-serif font-medium text-emerald-900 mb-3">
              Multi-Agent Evaluation
            </h3>
            <p className="text-sm font-serif text-emerald-800/80 leading-relaxed">
              Submissions are analyzed against the C2PCT methodology by autonomous LangGraph agents grounded in professor-injected resources.
            </p>
          </div>

          {/* Card 3 - Violet Theme */}
          <div className="p-8 rounded-[2rem] bg-violet-50/40 border border-violet-100/50 transition-colors hover:bg-violet-50/80">
            <div className="w-12 h-12 bg-violet-100/50 flex items-center justify-center rounded-2xl mb-6 border border-violet-100">
              <CheckCircle2 className="w-6 h-6 text-violet-700" />
            </div>
            <h3 className="text-lg font-serif font-medium text-violet-900 mb-3">
              Professor Authority
            </h3>
            <p className="text-sm font-serif text-violet-800/80 leading-relaxed">
              AI generates clinical summaries and empathetic feedback, but professors maintain ultimate oversight and revision control via secure dashboards.
            </p>
          </div>

        </div>
      </main>
    </div>
  );
}