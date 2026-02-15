"use client";

/**
 * EduAI — Career Path Finder Page
 * AI-powered career counseling with skills gap visualization.
 */

import { useState } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { FiDownload } from "react-icons/fi";

export default function CareerPage() {
  const { token } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    paths_markdown: string;
    skills_gap: Record<string, number> | null;
  } | null>(null);

  const downloadAsDoc = (markdown: string) => {
    // Convert markdown to simple HTML for Word
    const html = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office"
            xmlns:w="urn:schemas-microsoft-com:office:word"
            xmlns="http://www.w3.org/TR/REC-html40">
      <head><meta charset="utf-8"><title>Career Paths - EduAI</title>
      <style>body{font-family:Calibri,sans-serif;font-size:12pt;line-height:1.6;color:#222}
      h1,h2,h3{color:#1a1a2e}h1{font-size:18pt}h2{font-size:14pt}h3{font-size:12pt}
      ul{margin-left:20px}li{margin-bottom:4px}</style></head>
      <body>${markdown
        .replace(/### (.*)/g, "<h3>$1</h3>")
        .replace(/## (.*)/g, "<h2>$1</h2>")
        .replace(/# (.*)/g, "<h1>$1</h1>")
        .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
        .replace(/\*(.*?)\*/g, "<i>$1</i>")
        .replace(/^- (.*)/gm, "<li>$1</li>")
        .replace(/\n/g, "<br>")
      }</body></html>`;
    const blob = new Blob([html], { type: "application/msword" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "EduAI_Career_Paths.doc";
    a.click();
    URL.revokeObjectURL(url);
  };

  // Form state
  const [interests, setInterests] = useState("");
  const [skills, setSkills] = useState("");
  const [education, setEducation] = useState("12th Pass");
  const [location, setLocation] = useState("City");
  const [aspirations, setAspirations] = useState("");
  const [budget, setBudget] = useState("Free resources only");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!interests.trim()) return;
    setLoading(true);
    try {
      const res = await api.getCareerPaths(token, {
        interests,
        skills,
        education,
        location,
        aspirations,
        budget,
      });
      setResult(res);
    } catch (err: any) {
      alert(err.message || "Career path generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const gapData = result?.skills_gap
    ? Object.entries(result.skills_gap).map(([name, value]) => ({
        name,
        value: Number(value),
      }))
    : [];

  return (
    <AppLayout>
      <div className="p-4 md:p-6 max-w-4xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">💼 Career Path Finder</h1>
        <p className="text-sm text-text-secondary">
          Answer a few questions about your skills and interests. The AI will
          generate personalized career paths with courses, projects, and salary
          estimates.
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="glass-card space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Your Interests
              </label>
              <input
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="e.g., coding, design, farming"
                required
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue"
              />
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Current Skills
              </label>
              <input
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                placeholder="e.g., Python, MS Excel"
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue"
              />
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Education Level
              </label>
              <select
                value={education}
                onChange={(e) => setEducation(e.target.value)}
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none"
              >
                {["Below 10th", "10th Pass", "12th Pass", "Diploma", "Undergraduate", "Postgraduate"].map((e) => (
                  <option key={e}>{e}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Location Type
              </label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none"
              >
                {["Rural village", "Small town", "City", "Metro city"].map((l) => (
                  <option key={l}>{l}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-1">
              What do you dream of becoming?
            </label>
            <textarea
              value={aspirations}
              onChange={(e) => setAspirations(e.target.value)}
              placeholder="e.g., I want to build apps, start a business..."
              rows={2}
              className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue resize-none"
            />
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-1">
              Learning Budget
            </label>
            <select
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none"
            >
              {["Free resources only", "Under 500 INR/month", "Under 2000 INR/month", "No constraint"].map((b) => (
                <option key={b}>{b}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg font-medium transition disabled:opacity-50"
          >
            {loading ? "Analyzing career landscape..." : "Generate Career Paths"}
          </button>
        </form>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            <div className="glass-card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold">Your Career Paths</h3>
                <button
                  onClick={() => downloadAsDoc(result.paths_markdown)}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs bg-accent-blue/15 text-accent-blue hover:bg-accent-blue/25 rounded-md transition"
                >
                  <FiDownload size={14} />
                  Save as Word
                </button>
              </div>
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.paths_markdown}
                </ReactMarkdown>
              </div>
            </div>

            {gapData.length > 0 && (
              <div className="glass-card">
                <h3 className="text-sm font-semibold mb-4">
                  Skills Gap Analysis
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={gapData} layout="vertical">
                    <XAxis
                      type="number"
                      domain={[0, 100]}
                      tick={{ fill: "#8b949e", fontSize: 11 }}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={120}
                      tick={{ fill: "#8b949e", fontSize: 11 }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "#161b22",
                        border: "1px solid #30363d",
                        borderRadius: 6,
                      }}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {gapData.map((entry, i) => (
                        <Cell
                          key={i}
                          fill={
                            entry.value >= 60
                              ? "#238636"
                              : entry.value >= 30
                              ? "#d29922"
                              : "#da3633"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
