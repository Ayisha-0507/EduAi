"use client";

/**
 * EduAI — Dashboard Page
 * Stats, badges, activity charts, and progress overview.
 */

import { useState, useEffect } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { FiAward, FiBook, FiMessageSquare, FiTrendingUp } from "react-icons/fi";

const BADGE_EMOJIS: Record<string, string> = {
  Explorer: "🧭",
  "First Steps": "👣",
  "Active Learner": "🔥",
  "Knowledge Seeker": "🔍",
  "Dedicated Scholar": "📚",
  "Multi-Path Explorer": "🗺️",
  Pathfinder: "🏔️",
  "Quiz Taker": "📝",
  Quizzer: "✏️",
  "Quiz Champion": "🏆",
  "Feynman Teacher": "🎓",
  "Visual Learner": "👁️",
  "Social Impact Hero": "🌍",
  "Career Explorer": "💼",
  "Speed Reader": "⚡",
  "Community Builder": "🤝",
};

const PIE_COLORS = [
  "#238636", "#58a6ff", "#a371f7", "#d29922",
  "#da3633", "#3fb950", "#79c0ff", "#bc8cff",
];

export default function DashboardPage() {
  const { token } = useAuthStore();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getDashboard(token)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="spinner" />
        </div>
      </AppLayout>
    );
  }

  if (!data) {
    return (
      <AppLayout>
        <div className="p-8 text-center text-text-secondary">
          Unable to load dashboard. Please sign in.
        </div>
      </AppLayout>
    );
  }

  const { stats, activity_by_path } = data;
  const xpThresholds = [0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500];
  const nextThreshold = xpThresholds[Math.min(stats.level, xpThresholds.length - 1)];
  const prevThreshold = xpThresholds[Math.min(stats.level - 1, xpThresholds.length - 1)];
  const progressPct = Math.min(
    1,
    (stats.xp - prevThreshold) / Math.max(1, nextThreshold - prevThreshold)
  );

  const activityData = Object.entries(activity_by_path).map(([name, count]) => ({
    name: name.length > 15 ? name.slice(0, 15) + "…" : name,
    messages: count,
  }));

  const pieData = Object.entries(activity_by_path).map(([name, count]) => ({
    name,
    value: count as number,
  }));

  return (
    <AppLayout>
      <div className="p-4 md:p-6 max-w-6xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">Dashboard</h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            {
              icon: FiTrendingUp,
              label: "Level",
              value: stats.level,
              sub: `${stats.xp} XP`,
              color: "text-accent-green",
            },
            {
              icon: FiAward,
              label: "Badges",
              value: stats.badges.length,
              sub: "earned",
              color: "text-accent-purple",
            },
            {
              icon: FiBook,
              label: "Paths",
              value: stats.total_paths,
              sub: "active",
              color: "text-accent-blue",
            },
            {
              icon: FiMessageSquare,
              label: "Messages",
              value: stats.total_messages,
              sub: "total",
              color: "text-accent-yellow",
            },
          ].map((card) => (
            <div key={card.label} className="glass-card">
              <div className="flex items-center gap-3">
                <card.icon className={card.color} size={24} />
                <div>
                  <p className="text-2xl font-bold">{card.value}</p>
                  <p className="text-xs text-text-secondary">
                    {card.label} · {card.sub}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* XP Progress */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              Level {stats.level} Progress
            </span>
            <span className="text-xs text-text-secondary">
              {stats.xp} / {nextThreshold} XP
            </span>
          </div>
          <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-accent-green to-accent-blue rounded-full transition-all duration-500"
              style={{ width: `${progressPct * 100}%` }}
            />
          </div>
        </div>

        {/* Badges */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold mb-3">Badges</h3>
          <div className="flex flex-wrap gap-2">
            {stats.badges.length === 0 ? (
              <p className="text-sm text-text-secondary">
                No badges yet. Keep learning!
              </p>
            ) : (
              stats.badges.map((badge: string) => (
                <span key={badge} className="badge-chip">
                  {BADGE_EMOJIS[badge] || "🏅"} {badge}
                </span>
              ))
            )}
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Activity Bar Chart */}
          <div className="glass-card">
            <h3 className="text-sm font-semibold mb-4">Messages per Path</h3>
            {activityData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={activityData}>
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#8b949e", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "#8b949e", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#161b22",
                      border: "1px solid #30363d",
                      borderRadius: 6,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="messages" fill="#238636" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-text-secondary text-center py-8">
                No activity data yet
              </p>
            )}
          </div>

          {/* Activity Pie Chart */}
          <div className="glass-card">
            <h3 className="text-sm font-semibold mb-4">Activity Distribution</h3>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={PIE_COLORS[i % PIE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "#161b22",
                      border: "1px solid #30363d",
                      borderRadius: 6,
                      fontSize: 12,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-text-secondary text-center py-8">
                No activity data yet
              </p>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
