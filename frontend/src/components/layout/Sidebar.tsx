"use client";

/**
 * EduAI — Sidebar Component
 * Navigation sidebar with profile, paths, and tools.
 */

import { usePathname } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/lib/store";
import {
  FiMessageSquare,
  FiBook,
  FiBarChart2,
  FiFileText,
  FiBriefcase,
  FiCpu,
  FiLogOut,
  FiMenu,
  FiX,
  FiSettings,
  FiCamera,
} from "react-icons/fi";
import { useState, useCallback } from "react";

const navItems = [
  { href: "/chat", label: "Home Chat", icon: FiMessageSquare },
  { href: "/vision", label: "Vision Solver", icon: FiCamera },
  { href: "/learn", label: "Learning Paths", icon: FiBook },
  { href: "/dashboard", label: "Dashboard", icon: FiBarChart2 },
  { href: "/feynman", label: "Feynman Board", icon: FiCpu },
  { href: "/career", label: "Career Path", icon: FiBriefcase },
  { href: "/summarizer", label: "Summarizer", icon: FiFileText },
  { href: "/settings", label: "Settings", icon: FiSettings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout, isGuest } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = useCallback(() => {
    logout();
    window.location.href = "/";
  }, [logout]);

  const navContent = (
    <>
      {/* Logo */}
      <div className="p-5 border-b border-border-default">
        <h2 className="text-xl font-bold bg-gradient-to-r from-accent-green to-accent-blue bg-clip-text text-transparent">
          EduAI
        </h2>
        {user && (
          <p className="text-xs text-text-secondary mt-1 truncate">
            {isGuest ? "Guest Explorer" : user.nickname || user.email}
          </p>
        )}
      </div>

      {/* Nav Links */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              prefetch={true}
              onClick={() => setMobileOpen(false)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? "bg-accent-green/15 text-accent-green border border-accent-green/30"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
              }`}
            >
              <item.icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="p-4 border-t border-border-default">
        {user && (
          <div className="flex items-center gap-3 mb-3 px-1">
            <div className="w-8 h-8 rounded-full bg-accent-green/20 flex items-center justify-center text-accent-green text-sm font-bold">
              {(user.nickname || user.email || "?")[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-text-primary truncate">
                {user.nickname || "User"}
              </p>
              <p className="text-xs text-text-secondary truncate">
                {isGuest ? "Guest Mode" : user.email}
              </p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-red-400 hover:bg-red-500/10 transition"
        >
          <FiLogOut size={16} />
          {isGuest ? "Exit Guest Mode" : "Log Out"}
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 bg-bg-secondary border border-border-default rounded-lg"
      >
        {mobileOpen ? <FiX size={20} /> : <FiMenu size={20} />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-[#010409] border-r border-border-default z-40 flex flex-col transition-transform duration-300 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0 md:static md:z-auto`}
      >
        {navContent}
      </aside>
    </>
  );
}
