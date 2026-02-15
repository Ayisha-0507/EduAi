"use client";

/**
 * EduAI — Settings Page
 * User profile, tutor persona, model selection, and preferences.
 */

import { useState, useEffect } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import { FiSave, FiCheck } from "react-icons/fi";

const PERSONAS = [
  { key: "Friendly Encourager", desc: "Warm, supportive tone" },
  { key: "Strict Professor", desc: "Rigorous, academic approach" },
  { key: "Socratic Questioner", desc: "Answers with probing questions" },
  { key: "Concise Technician", desc: "Direct, no-nonsense answers" },
  { key: "Creative Storyteller", desc: "Uses narratives and analogies" },
];

const MODELS = [
  { key: "deepseek", label: "DeepSeek", desc: "General tutoring & reasoning" },
  { key: "arcee", label: "Arcee", desc: "Programming & coding" },
  { key: "nous", label: "NousHermes", desc: "Roleplay & creative" },
  { key: "nemotron", label: "Nemotron", desc: "Textbooks & diagrams" },
  { key: "qwen_vl", label: "Qwen VL", desc: "Science & visual" },
];

const LANGUAGES = [
  "English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam",
  "Bengali", "Marathi", "Gujarati", "Urdu", "Odia", "Punjabi",
  "French", "Spanish", "Arabic",
];

export default function SettingsPage() {
  const { token, user, updateUser } = useAuthStore();
  const [nickname, setNickname] = useState(user?.nickname || "");
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [persona, setPersona] = useState(user?.tutor_persona || "Friendly Encourager");
  const [modelMode, setModelMode] = useState(user?.model_selection_mode || "Auto");
  const [manualModel, setManualModel] = useState(user?.manual_model_choice || "deepseek");
  const [language, setLanguage] = useState(user?.preferred_language || "English");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!token) return;
    setSaving(true);
    try {
      const updates: Record<string, any> = {
        nickname,
        full_name: fullName,
        bio,
        tutor_persona: persona,
        model_selection_mode: modelMode,
        manual_model_choice: manualModel,
        preferred_language: language,
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
      <div className="p-6 max-w-3xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">⚙️ Settings</h1>

        {/* Profile */}
        <div className="glass-card space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Profile
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Nickname
              </label>
              <input
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue"
              />
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Full Name
              </label>
              <input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm text-text-secondary mb-1">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={2}
              className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue resize-none"
            />
          </div>
          <div>
            <label className="block text-sm text-text-secondary mb-1">
              Preferred Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none"
            >
              {LANGUAGES.map((l) => (
                <option key={l}>{l}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Tutor Persona */}
        <div className="glass-card space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Tutor Persona
          </h2>
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
                <div
                  className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                    persona === p.key
                      ? "border-accent-green"
                      : "border-border-default"
                  }`}
                >
                  {persona === p.key && (
                    <div className="w-2 h-2 rounded-full bg-accent-green" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium">{p.key}</p>
                  <p className="text-xs text-text-secondary">{p.desc}</p>
                </div>
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
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
                  modelMode === mode
                    ? "bg-accent-green/15 text-accent-green border border-accent-green/30"
                    : "bg-bg-tertiary text-text-secondary border border-transparent"
                }`}
              >
                {mode}
              </button>
            ))}
          </div>

          {modelMode === "Auto" ? (
            <p className="text-xs text-text-secondary">
              EduAI automatically picks the best AI model based on what you ask.
              Code questions → Arcee, Math → DeepSeek, etc.
            </p>
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
                  <div
                    className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                      manualModel === m.key
                        ? "border-accent-blue"
                        : "border-border-default"
                    }`}
                  >
                    {manualModel === m.key && (
                      <div className="w-2 h-2 rounded-full bg-accent-blue" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{m.label}</p>
                    <p className="text-xs text-text-secondary">{m.desc}</p>
                  </div>
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
            <>
              <FiCheck size={18} /> Saved!
            </>
          ) : saving ? (
            <div className="spinner" />
          ) : (
            <>
              <FiSave size={18} /> Save Settings
            </>
          )}
        </button>
      </div>
    </AppLayout>
  );
}
