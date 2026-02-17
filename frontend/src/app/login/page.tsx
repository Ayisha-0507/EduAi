"use client";

import { useState } from "react";
import { useAuthStore } from "@/lib/store";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const { setAuth, setGuest } = useAuthStore();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      // TODO: Call your API for login
      // Example: const { token, user } = await api.login(email, password);
      // setAuth(token, user);
      // router.push("/chat");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-bg-primary">
      <form onSubmit={handleLogin} className="glass-card p-8 w-full max-w-md space-y-6">
        <h1 className="text-2xl font-bold text-center">Login to EduAI</h1>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border border-border-default rounded-lg"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border border-border-default rounded-lg"
          required
        />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <button
          type="submit"
          className="w-full bg-accent-green text-white py-2 rounded-lg font-semibold hover:bg-accent-blue transition"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
