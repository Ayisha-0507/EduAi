"use client";

/**
 * EduAI — Textbook Summarizer Page
 * Paste text → get bullet summaries, flashcards, exam notes, or mind maps.
 */

import { useState } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FiDownload, FiClipboard } from "react-icons/fi";

const FORMATS = [
  "Bullet-point summary",
  "Flashcards (Q&A)",
  "Exam answer notes",
  "Mind map outline",
  "All formats",
];

export default function SummarizerPage() {
  const { token } = useAuthStore();
  const [text, setText] = useState("");
  const [format, setFormat] = useState(FORMATS[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");

  const handleSubmit = async () => {
    if (!token || !text.trim()) return;
    setLoading(true);
    try {
      const res = await api.summarize(token, text, format);
      setResult(res.summary);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([result], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "summary.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setText(ev.target?.result as string);
    };
    reader.readAsText(file);
  };

  return (
    <AppLayout>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">📄 Textbook Summarizer</h1>
        <p className="text-sm text-text-secondary">
          Paste a chapter or upload a text file. The AI will extract key
          concepts and generate structured study materials.
        </p>

        <div className="glass-card space-y-4">
          {/* Input method */}
          <div className="flex gap-4 items-center">
            <label className="flex items-center gap-2 px-3 py-2 bg-bg-tertiary rounded-lg cursor-pointer text-sm text-text-secondary hover:text-text-primary transition border border-border-default">
              <FiClipboard size={16} />
              Upload .txt / .md
              <input
                type="file"
                accept=".txt,.md"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
            {text && (
              <span className="text-xs text-text-secondary">
                {text.length.toLocaleString()} characters
                {text.length > 12000 && " (will be truncated to 12,000)"}
              </span>
            )}
          </div>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your textbook content here..."
            rows={8}
            className="w-full bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-sm text-text-primary placeholder-text-secondary/50 outline-none focus:border-accent-blue resize-y"
          />

          <div className="flex flex-wrap gap-3 items-center">
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="bg-bg-primary border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary outline-none"
            >
              {FORMATS.map((f) => (
                <option key={f}>{f}</option>
              ))}
            </select>

            <button
              onClick={handleSubmit}
              disabled={loading || !text.trim()}
              className="px-6 py-2 bg-accent-green hover:bg-accent-greenHover text-white text-sm rounded-lg font-medium transition disabled:opacity-50"
            >
              {loading ? "Summarizing..." : "Summarize"}
            </button>
          </div>
        </div>

        {/* Result */}
        {result && (
          <div className="glass-card space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold">Result</h3>
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-bg-tertiary rounded-md hover:bg-border-default text-text-secondary transition"
              >
                <FiDownload size={14} />
                Download .md
              </button>
            </div>
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
