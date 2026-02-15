"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import LoginForm from "@/components/auth/LoginForm";

export default function HomePage() {
  const { isLoggedIn, isGuest } = useAuthStore();
  const router = useRouter();
  const [phase, setPhase] = useState<"boot" | "fadeout" | "login">("boot");

  // Boot → fade-out → login transition
  useEffect(() => {
    if (phase !== "boot") return;
    const timer = setTimeout(() => setPhase("fadeout"), 4000);
    return () => clearTimeout(timer);
  }, [phase]);

  useEffect(() => {
    if (phase !== "fadeout") return;
    const timer = setTimeout(() => setPhase("login"), 700);
    return () => clearTimeout(timer);
  }, [phase]);

  return (
    <>
      {/* Boot animation overlay – original Streamlit cyber-brain */}
      {phase !== "login" && (
        <div
          className={`loading-container${phase === "fadeout" ? " fade-out" : ""}`}
        >
          <div className="cyber-brain-container">
            <svg
              className="cyber-brain-svg"
              viewBox="0 0 100 100"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient
                  id="liquid-gradient"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop
                    offset="0%"
                    style={{ stopColor: "#a275e3", stopOpacity: 1 }}
                  />
                  <stop
                    offset="100%"
                    style={{ stopColor: "#ffffff", stopOpacity: 1 }}
                  />
                </linearGradient>
              </defs>
              <path
                className="brain-outline"
                d="M50,5 C25,5 25,30 25,30 C10,30 10,50 10,50 C10,75 25,75 25,75 C25,95 50,95 50,95 C75,95 75,75 75,75 C90,75 90,50 90,50 C90,30 75,30 75,30 C75,5 50,5 50,5 Z"
              />
              <path
                className="brain-veins"
                d="M50,5 C50,20 35,20 35,35 S50,50 50,50 S65,50 65,65 S50,80 50,80"
              />
              <path
                className="brain-veins"
                d="M50,95 C50,80 35,80 35,65 S50,50 50,50 S65,50 65,35 S50,20 50,20"
              />
              <path
                className="brain-veins"
                d="M25,30 C35,30 35,40 40,50 S60,60 60,70 S75,75 75,75"
              />
              <path
                className="brain-veins"
                d="M10,50 C20,55 30,60 40,60 S60,55 70,50 S90,50 90,50"
              />
            </svg>
          </div>
          <div className="loading-text">Booting Cognitive Core...</div>
        </div>
      )}

      {/* Login form – shown after boot animation completes */}
      {phase === "login" && (
        <main
          className="min-h-screen flex items-center justify-center p-4"
          style={{
            background: "#0a0118",
            animation: "fade-in 0.5s ease-out",
          }}
        >
          <LoginForm />
        </main>
      )}
    </>
  );
}
