"use client";

/**
 * EduAI — About Page
 * Read-only info about the platform with interactive particle background.
 */

import { useRouter } from "next/navigation";
import { FiArrowLeft, FiHeart } from "react-icons/fi";
import AppLayout from "@/components/layout/AppLayout";
import ParticleField from "@/components/effects/ParticleField";

export default function AboutPage() {
  const router = useRouter();

  return (
    <AppLayout>
      <div className="relative flex-1 overflow-y-auto">
        {/* Particle background */}
        <ParticleField count={35} className="!fixed" />

        <div className="relative z-10 p-4 md:p-6 max-w-3xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
            >
              <FiArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-accent-green via-accent-blue to-purple-400 bg-clip-text text-transparent">
                About EduAI
              </h1>
              <p className="text-text-secondary text-sm mt-0.5">Your Personal AI-Powered Tutor</p>
            </div>
          </div>

          {/* Hero card */}
          <div className="glass-card text-center py-8 border-accent-green/20 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-accent-green/5 via-transparent to-accent-blue/5" />
            <div className="relative z-10">
              <div className="text-5xl mb-3">🧠</div>
              <h2 className="text-xl font-bold text-text-primary mb-2">
                Learn Smarter, Not Harder
              </h2>
              <p className="text-sm text-text-secondary max-w-lg mx-auto leading-relaxed">
                EduAI is an adaptive AI tutor that personalizes your learning experience.
                It detects your emotions, adjusts its teaching style, tracks your progress,
                and helps you master any subject through conversation, quizzes, flashcards,
                and even live debates.
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: "6+", label: "AI Models" },
              { value: "15+", label: "Languages" },
              { value: "10+", label: "Features" },
            ].map((s) => (
              <div key={s.label} className="glass-card text-center py-4">
                <p className="text-2xl font-bold bg-gradient-to-r from-accent-green to-accent-blue bg-clip-text text-transparent">
                  {s.value}
                </p>
                <p className="text-xs text-text-secondary mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>

          {/* How it works */}
          <div className="glass-card space-y-3">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              📖 How It Works
            </h2>
            <div className="space-y-3">
              {[
                { step: "1", title: "Ask Anything", desc: "Type a question, attach an image, or use voice input" },
                { step: "2", title: "AI Adapts", desc: "EduAI detects your level, emotions, and preferred style" },
                { step: "3", title: "Learn & Practice", desc: "Get explanations, flashcards, quizzes, and debate challenges" },
                { step: "4", title: "Track Progress", desc: "Dashboard shows your growth, streaks, and milestones" },
              ].map((s) => (
                <div key={s.step} className="flex items-start gap-3">
                  <div className="w-7 h-7 rounded-full bg-accent-green/15 border border-accent-green/30 flex items-center justify-center flex-shrink-0 text-xs font-bold text-accent-green">
                    {s.step}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text-primary">{s.title}</p>
                    <p className="text-xs text-text-secondary">{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="glass-card text-center py-5 space-y-2 border-purple-500/20">
            <p className="text-sm text-text-secondary flex items-center justify-center gap-1.5">
              Built with <FiHeart size={14} className="text-red-400" /> for learners everywhere
            </p>
            <p className="text-xs text-text-secondary/50">
              EduAI &copy; {new Date().getFullYear()} — All rights reserved
            </p>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
