"use client";

/**
 * EduAI — Sidebar Component
 * Navigation sidebar with profile, paths, and tools.
 * Collapsible on ALL screen sizes via a toggle button.
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
  FiLayers,
  FiZap,
  FiUser,
  FiInfo,
  FiWifiOff,
  FiChevronLeft,
  FiChevronRight,
} from "react-icons/fi";
import { useState, useCallback, useEffect } from "react";

const navItems = [
  { href: "/chat", label: "Home Chat", icon: FiMessageSquare },
  { href: "/offline-chat", label: "Offline Chat", icon: FiWifiOff },
  { href: "/vision", label: "Vision Solver", icon: FiCamera },
  { href: "/flashcards", label: "Flashcards", icon: FiLayers },
  { href: "/debate", label: "Debate Arena", icon: FiZap },
  { href: "/learn", label: "Learning Paths", icon: FiBook },
  { href: "/dashboard", label: "Dashboard", icon: FiBarChart2 },
  { href: "/feynman", label: "Feynman Board", icon: FiCpu },
  { href: "/career", label: "Career Path", icon: FiBriefcase },
  { href: "/summarizer", label: "Summarizer", icon: FiFileText },
  { href: "/settings", label: "Settings", icon: FiSettings },
  { href: "/profile", label: "My Profile", icon: FiUser },
  { href: "/about", label: "About EduAI", icon: FiInfo },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout, isGuest } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  // On mobile, default collapsed; on desktop, read from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("sidebar-collapsed");
      if (saved !== null) setCollapsed(saved === "true");
    }
  }, []);

  const toggleCollapsed = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("sidebar-collapsed", String(next));
      return next;
    });
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    window.location.href = "/";
  }, [logout]);

  const navContent = (
    <>
      {/* Logo */}
      <div className="p-4 border-b border-border-default flex items-center justify-between">
        {!collapsed && (
          <div>
            <h2 className="text-xl font-bold bg-gradient-to-r from-accent-green to-accent-blue bg-clip-text text-transparent">
              EduAI
            </h2>
            {user && (
              <p className="text-xs text-text-secondary mt-1 truncate">
                {isGuest ? "Guest Explorer" : user.nickname || user.email}
              </p>
            )}
          </div>
        )}
        {collapsed && (
          <span className="text-lg font-bold text-accent-green mx-auto">E</span>
        )}
      </div>

      {/* Nav Links */}
      <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              prefetch={true}
              onClick={() => setMobileOpen(false)}
              title={collapsed ? item.label : undefined}
              className={`w-full flex items-center gap-3 rounded-lg text-base md:text-sm font-medium transition ${
                collapsed ? "justify-center px-2 py-2.5" : "px-3 py-2.5"
              } ${
                isActive
                  ? "bg-accent-green/15 text-accent-green border border-accent-green/30"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
              }`}
            >
              <item.icon size={20} className="flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="p-3 border-t border-border-default">
        {user && !collapsed && (
          <div className="flex items-center gap-3 mb-3 px-1">
            <div className="w-8 h-8 rounded-full bg-accent-green/20 flex items-center justify-center text-accent-green text-sm font-bold flex-shrink-0">
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
          title={collapsed ? (isGuest ? "Exit Guest Mode" : "Log Out") : undefined}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-red-400 hover:bg-red-500/10 transition ${
            collapsed ? "justify-center" : ""
          }`}
        >
          <FiLogOut size={16} />
          {!collapsed && (isGuest ? "Exit Guest Mode" : "Log Out")}
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile hamburger toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed top-3 left-3 z-50 md:hidden p-2.5 bg-bg-secondary border border-border-default rounded-lg shadow-lg"
        aria-label="Toggle menu"
      >
        {mobileOpen ? <FiX size={22} /> : <FiMenu size={22} />}
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
        className={`fixed top-0 left-0 h-full bg-[#010409] border-r border-border-default z-40 flex flex-col transition-all duration-300 ${
          mobileOpen ? "translate-x-0 w-64" : "-translate-x-full w-64"
        } md:translate-x-0 md:static md:z-auto ${
          collapsed ? "md:w-16" : "md:w-64"
        }`}
      >
        {navContent}
      </aside>

      {/* Desktop collapse toggle — sits on sidebar edge */}
      <button
        onClick={toggleCollapsed}
        className="hidden md:flex fixed z-50 items-center justify-center w-6 h-6 rounded-full bg-bg-secondary border border-border-default shadow-md hover:bg-bg-tertiary transition-all duration-300"
        style={{ top: 20, left: collapsed ? 52 : 248 }}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? <FiChevronRight size={14} /> : <FiChevronLeft size={14} />}
      </button>
    </>
  );
}
