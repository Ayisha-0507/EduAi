"use client";

/**
 * EduAI — Shared App Layout (route group)
 * This layout wraps ALL authenticated pages. The Sidebar mounts ONCE
 * and stays alive across page navigations — no re-render, no blank flash.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import Sidebar from "@/components/layout/Sidebar";

// Module-level flag: once Zustand has hydrated on first load, skip the check
// on subsequent soft navigations so the layout renders instantly.
let _hydrated = false;

export default function AppGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isLoggedIn, isGuest } = useAuthStore();
  const [ready, setReady] = useState(_hydrated);

  useEffect(() => {
    _hydrated = true;
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready && !isLoggedIn && !isGuest) {
      router.replace("/");
    }
  }, [ready, isLoggedIn, isGuest, router]);

  if (!ready) return null;
  if (!isLoggedIn && !isGuest) return null;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
