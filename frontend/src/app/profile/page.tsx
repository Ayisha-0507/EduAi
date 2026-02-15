"use client";

/**
 * EduAI — My Profile Page
 * User account details, profile editing, language, and account info.
 */

import { useState } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import { FiSave, FiCheck, FiUser, FiMail, FiLogOut, FiArrowLeft, FiShield, FiGlobe } from "react-icons/fi";
import { useRouter } from "next/navigation";

const LANGUAGES = [
  "English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam",
  "Bengali", "Marathi", "Gujarati", "Urdu", "Odia", "Punjabi",
  "French", "Spanish", "Arabic",
];

export default function ProfilePage() {
  const router = useRouter();
  const { token, user, updateUser, isGuest, logout } = useAuthStore();
  const [nickname, setNickname] = useState(user?.nickname || "");
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [bio, setBio] = useState(user?.bio || "");
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

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  const initial = (user?.nickname || user?.email || "?")[0].toUpperCase();
  const joinDate = "Member since 2025"; // placeholder

  return (
    <AppLayout>
      <div className="p-6 max-w-3xl mx-auto space-y-6 overflow-y-auto flex-1">
        {/* Header */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
          >
            <FiArrowLeft size={20} />
          </button>
          <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
            <FiUser className="text-accent-blue" /> My Profile
          </h1>
        </div>

        {/* Profile Header Card */}
        <div className="glass-card flex items-center gap-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-accent-green/5 to-accent-blue/5" />
          <div className="relative z-10 flex items-center gap-4 w-full">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent-green to-accent-blue flex items-center justify-center text-white text-2xl font-bold flex-shrink-0 shadow-lg">
              {initial}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-lg font-bold text-text-primary truncate">
                {user?.nickname || "User"}
              </p>
              <p className="text-sm text-text-secondary truncate flex items-center gap-1.5">
                <FiMail size={12} />
                {isGuest ? "Guest Mode — No account" : user?.email}
              </p>
              <p className="text-xs text-text-secondary/50 mt-0.5 flex items-center gap-1">
                <FiShield size={10} />
                {isGuest ? "Guest Explorer" : joinDate}
              </p>
            </div>
          </div>
        </div>

        {/* Edit Profile */}
        {!isGuest && (
          <div className="glass-card space-y-4">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Edit Profile
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-1">Nickname</label>
                <input
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue transition"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">Full Name</label>
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue transition"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Bio</label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={2}
                placeholder="Tell us a bit about yourself..."
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue resize-none transition placeholder-text-secondary/50"
              />
            </div>
          </div>
        )}

        {/* Language */}
        <div className="glass-card space-y-3">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider flex items-center gap-1.5">
            <FiGlobe size={14} /> Preferred Language
          </h2>
          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
            {LANGUAGES.map((l) => (
              <button
                key={l}
                onClick={() => setLanguage(l)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition border ${
                  language === l
                    ? "bg-accent-blue/15 text-accent-blue border-accent-blue/30"
                    : "bg-bg-tertiary text-text-secondary border-border-default hover:text-text-primary"
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        {/* Account info */}
        <div className="glass-card space-y-3">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Account Info
          </h2>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Email</span>
              <span className="text-text-primary">{isGuest ? "N/A" : user?.email}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Account Type</span>
              <span className={`${isGuest ? "text-amber-400" : "text-accent-green"}`}>
                {isGuest ? "Guest" : "Full Account"}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Language</span>
              <span className="text-text-primary">{language}</span>
            </div>
          </div>
        </div>

        {/* Save + Logout */}
        <div className="space-y-3">
          {!isGuest && (
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
                <><FiSave size={18} /> Save Profile</>
              )}
            </button>
          )}

          <button
            onClick={handleLogout}
            className="w-full py-3 bg-transparent hover:bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg font-medium transition flex items-center justify-center gap-2"
          >
            <FiLogOut size={16} />
            {isGuest ? "Exit Guest Mode" : "Log Out"}
          </button>
        </div>
      </div>
    </AppLayout>
  );
}
