"use client";

/**
 * EduAI — Settings Page
 * Tutor persona and AI model selection only. Profile moved to /profile.
 */

import { useState } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import { FiSave, FiCheck, FiArrowLeft } from "react-icons/fi";
import { useRouter } from "next/navigation";

const PERSONAS = [
  { key: "Friendly Encourager", desc: "Warm, supportive tone", emoji: "😊" },
  { key: "Strict Professor", desc: "Rigorous, academic approach", emoji: "🎓" },
  { key: "Socratic Questioner", desc: "Answers with probing questions", emoji: "🤔" },
  { key: "Concise Technician", desc: "Direct, no-nonsense answers", emoji: "⚡" },
  { key: "Creative Storyteller", desc: "Uses narratives and analogies", emoji: "📖" },
];

const MODELS = [
  { key: "deepseek", label: "DeepSeek", desc: "General tutoring & reasoning", emoji: "🧠" },
  { key: "arcee", label: "Arcee", desc: "Programming & coding", emoji: "💻" },
  { key: "nous", label: "NousHermes", desc: "Roleplay & creative", emoji: "🎭" },
  { key: "nemotron", label: "Nemotron", desc: "Textbooks & diagrams", emoji: "📐" },
  { key: "qwen_vl", label: "Qwen VL", desc: "Science & visual", emoji: "🔬" },
];

export default function SettingsPage() {
  const router = useRouter();
  const { token, user, updateUser } = useAuthStore();
  const [persona, setPersona] = useState(user?.tutor_persona || "Friendly Encourager");
  const [modelMode, setModelMode] = useState(user?.model_selection_mode || "Auto");
  const [manualModel, setManualModel] = useState(user?.manual_model_choice || "deepseek");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!token) return;
    setSaving(true);
    try {
      const updates: Record<string, any> = {
        tutor_persona: persona,
        model_selection_mode: modelMode,
        manual_model_choice: manualModel,
      };
      await api.updateProfile(token, updates);
      updateUser(updates);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-4 md:p-6 max-w-3xl mx-auto space-y-6 overflow-y-auto flex-1">
        {/* Header */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
          >
            <FiArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-text-primary">⚙️ Settings</h1>
            <p className="text-xs text-text-secondary">AI behavior and model preferences</p>
          </div>
        </div>

        {/* Tutor Persona */}
        <div className="glass-card space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Tutor Persona
          </h2>
          <p className="text-xs text-text-secondary">Choose how the AI tutor speaks and teaches you</p>
          <div className="grid gap-2">
            {PERSONAS.map((p) => (
              <label
                key={p.key}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition ${
                  persona === p.key
                    ? "bg-accent-green/10 border-accent-green/30"
                    : "border-border-default hover:border-text-secondary"
                }`}
              >
                <input
                  type="radio"
                  name="persona"
                  checked={persona === p.key}
                  onChange={() => setPersona(p.key)}
                  className="sr-only"
                />
                <span className="text-lg">{p.emoji}</span>
                <div className="flex-1">
                  <p className="text-sm font-medium">{p.key}</p>
                  <p className="text-xs text-text-secondary">{p.desc}</p>
                </div>
                {persona === p.key && (
                  <div className="w-5 h-5 rounded-full bg-accent-green/20 flex items-center justify-center">
                    <FiCheck size={12} className="text-accent-green" />
                  </div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Model Selection */}
        <div className="glass-card space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            AI Model Selection
          </h2>

          <div className="flex gap-2">
            {["Auto", "Manual"].map((mode) => (
              <button
                key={mode}
                onClick={() => setModelMode(mode)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition border ${
                  modelMode === mode
                    ? "bg-accent-green/15 text-accent-green border-accent-green/30"
                    : "bg-bg-tertiary text-text-secondary border-border-default hover:text-text-primary"
                }`}
              >
                {mode === "Auto" ? "🤖 Auto" : "🎯 Manual"}
              </button>
            ))}
          </div>

          {modelMode === "Auto" ? (
            <div className="p-3 bg-accent-green/5 border border-accent-green/15 rounded-lg">
              <p className="text-xs text-text-secondary leading-relaxed">
                EduAI automatically picks the best AI model based on your question.
                Code questions → Arcee, Math → DeepSeek, Creative → NousHermes, etc.
              </p>
            </div>
          ) : (
            <div className="grid gap-2">
              {MODELS.map((m) => (
                <label
                  key={m.key}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition ${
                    manualModel === m.key
                      ? "bg-accent-blue/10 border-accent-blue/30"
                      : "border-border-default hover:border-text-secondary"
                  }`}
                >
                  <input
                    type="radio"
                    name="model"
                    checked={manualModel === m.key}
                    onChange={() => setManualModel(m.key)}
                    className="sr-only"
                  />
                  <span className="text-lg">{m.emoji}</span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{m.label}</p>
                    <p className="text-xs text-text-secondary">{m.desc}</p>
                  </div>
                  {manualModel === m.key && (
                    <div className="w-5 h-5 rounded-full bg-accent-blue/20 flex items-center justify-center">
                      <FiCheck size={12} className="text-accent-blue" />
                    </div>
                  )}
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full py-3 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {saved ? (
            <><FiCheck size={18} /> Saved!</>
          ) : saving ? (
            <div className="spinner" />
          ) : (
            <><FiSave size={18} /> Save Settings</>
          )}
        </button>
      </div>
    </AppLayout>
  );
}
