"use client";

/**
 * EduAI — App Layout (authenticated pages)
 * Sidebar + content area, shared across all logged-in pages.
 *
 * Uses a module-level flag so that only the FIRST page load waits for
 * Zustand hydration. All subsequent tab navigations render instantly.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import Sidebar from "@/components/layout/Sidebar";

// Survives component unmount/remount across page navigations.
// Once Zustand has hydrated on the first load, every subsequent
// mount of AppLayout skips the blank frame entirely.
let _storeHydrated = false;

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isLoggedIn, isGuest } = useAuthStore();
  const [ready, setReady] = useState(_storeHydrated);

  useEffect(() => {
    _storeHydrated = true;
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready && !isLoggedIn && !isGuest) {
      router.replace("/");
    }
  }, [ready, isLoggedIn, isGuest, router]);

  // First load only: wait one frame for Zustand hydration
  if (!ready) return null;
  if (!isLoggedIn && !isGuest) return null;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
