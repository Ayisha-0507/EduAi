"use client";

/**
 * EduAI — Feynman Board Page
 * Teach a concept to the AI to deepen your understanding.
 */

import { useState, useRef, useEffect } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FiSend, FiRefreshCw } from "react-icons/fi";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function FeynmanPage() {
  const { token, isGuest } = useAuthStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading || !token) return;

    const userMsg: Message = { role: "user", content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await api.feynmanChat(token, {
        message: input,
        history: newMessages.map((m) => ({ role: m.role, content: m.content })),
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.reply },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setInput("");
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-screen">
        {/* Header */}
        <header className="px-3 md:px-6 py-4 border-b border-border-default bg-bg-secondary/50">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold">🎓 Feynman Board</h1>
              <p className="text-xs text-text-secondary mt-0.5">
                Teach me a concept — I&apos;ll be your confused student. If you
                can explain it simply, you truly understand it.
              </p>
            </div>
            <button
              onClick={handleReset}
              className="p-2 rounded-md hover:bg-bg-tertiary text-text-secondary transition"
              title="Reset conversation"
            >
              <FiRefreshCw size={16} />
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-3 md:px-6 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="text-4xl mb-4">🤔</div>
                <h2 className="text-lg font-semibold">Teach me something!</h2>
                <p className="text-sm text-text-secondary mt-2">
                  Start by explaining any concept. I&apos;ll ask clarifying
                  questions like a curious student. This is based on the Feynman
                  Technique — the best way to learn is to teach.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  {[
                    "Explain recursion",
                    "How does photosynthesis work?",
                    "What is blockchain?",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => setInput(q)}
                      className="px-3 py-1.5 text-xs bg-bg-tertiary border border-border-default rounded-full text-text-secondary hover:text-text-primary transition"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}>
                {msg.role === "assistant" ? (
                  <div className="markdown-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm">{msg.content}</p>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="chat-bubble-ai flex items-center gap-2">
                <div className="spinner" />
                <span className="text-sm text-text-secondary">Hmm, let me think about that...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="px-3 md:px-6 py-4 border-t border-border-default">
          <div className="flex gap-3 max-w-4xl mx-auto">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Explain a concept to me..."
              className="flex-1 bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-accent-blue outline-none transition"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-4 py-3 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg transition disabled:opacity-50"
            >
              <FiSend size={18} />
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
