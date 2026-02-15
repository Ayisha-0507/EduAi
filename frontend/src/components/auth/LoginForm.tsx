"use client";

/**
 * EduAI — Login Form Component
 */

import { useState } from "react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { useRouter } from "next/navigation";
import { FiMail, FiLock, FiLogIn, FiUserPlus, FiUsers } from "react-icons/fi";
import { FcGoogle } from "react-icons/fc";
import { loginWithGoogle } from "@/lib/firebase";

export default function LoginForm() {
  const router = useRouter();
  const { setAuth, setGuest } = useAuthStore();
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let res;
      if (isSignup) {
        res = await api.signup(email, password, nickname || undefined);
      } else {
        res = await api.login(email, password);
      }

      const profile = await api.getProfile(res.token);
      setAuth(res.token, profile);
      router.push("/chat");
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    setError("");
    setLoading(true);
    try {
      const result = await loginWithGoogle();
      const idToken = await result.user.getIdToken();
      // Send Firebase ID token to our backend for JWT exchange
      const res = await api.login(result.user.email || "", "google-oauth");
      const profile = await api.getProfile(res.token);
      setAuth(res.token, profile);
      router.push("/chat");
    } catch (err: any) {
      setError(err.message || "Google login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleGuest = () => {
    setGuest();
    router.push("/chat");
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="glass-card">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-accent-green to-accent-blue bg-clip-text text-transparent">
            EduAI
          </h1>
          <p className="text-text-secondary mt-2 text-sm">
            Your Personal AI Tutor
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex mb-6 bg-bg-tertiary rounded-lg p-1">
          <button
            onClick={() => setIsSignup(false)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
              !isSignup
                ? "bg-accent-green text-white"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Log In
          </button>
          <button
            onClick={() => setIsSignup(true)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
              isSignup
                ? "bg-accent-green text-white"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignup && (
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Nickname
              </label>
              <div className="relative">
                <FiUserPlus className="absolute left-3 top-3 text-text-secondary" />
                <input
                  type="text"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="Your display name"
                  className="w-full pl-10 pr-4 py-2.5 bg-bg-primary border border-border-default rounded-lg text-text-primary placeholder-text-secondary/50 focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 outline-none transition"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm text-text-secondary mb-1">
              Email
            </label>
            <div className="relative">
              <FiMail className="absolute left-3 top-3 text-text-secondary" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full pl-10 pr-4 py-2.5 bg-bg-primary border border-border-default rounded-lg text-text-primary placeholder-text-secondary/50 focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 outline-none transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-1">
              Password
            </label>
            <div className="relative">
              <FiLock className="absolute left-3 top-3 text-text-secondary" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
                className="w-full pl-10 pr-4 py-2.5 bg-bg-primary border border-border-default rounded-lg text-text-primary placeholder-text-secondary/50 focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 outline-none transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <div className="spinner" />
            ) : (
              <>
                <FiLogIn />
                {isSignup ? "Create Account" : "Log In"}
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-3 my-6">
          <div className="flex-1 h-px bg-border-default" />
          <span className="text-text-secondary text-xs">or</span>
          <div className="flex-1 h-px bg-border-default" />
        </div>

        {/* Google + Guest */}
        <div className="space-y-3">
          <button
            onClick={handleGoogle}
            disabled={loading}
            className="w-full py-2.5 bg-bg-tertiary hover:bg-border-default border border-border-default text-text-primary rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <FcGoogle size={18} />
            Continue with Google
          </button>

          <button
            onClick={handleGuest}
            className="w-full py-2.5 bg-transparent hover:bg-bg-tertiary border border-border-default text-text-secondary rounded-lg font-medium transition flex items-center justify-center gap-2"
          >
            <FiUsers size={16} />
            Continue as Guest
          </button>
        </div>
      </div>
    </div>
  );
}
