"use client";

/**
 * EduAI — Learning Paths Page
 * View, create, and interact with structured learning paths.
 */

import { useState, useEffect, useRef } from "react";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FiPlus,
  FiTrash2,
  FiChevronLeft,
  FiChevronRight,
  FiSend,
  FiCpu,
  FiBook,
  FiHelpCircle,
  FiMenu,
  FiX,
} from "react-icons/fi";

interface PathData {
  name: string;
  topics: string[];
  current_topic: string;
  chat_history: { role: string; content: string; timestamp?: number }[];
  path_type: string;
}

export default function LearnPage() {
  const { token, isGuest } = useAuthStore();
  const [paths, setPaths] = useState<Record<string, PathData>>({});
  const [activePath, setActivePath] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [input, setInput] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newGoal, setNewGoal] = useState("");
  const [createMethod, setCreateMethod] = useState<"manual" | "ai_generated">("manual");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load paths
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .listPaths(token)
      .then((res) => setPaths(res.paths))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [paths, activePath]);

  const activeData = activePath ? paths[activePath] : null;

  const handleCreate = async () => {
    if (!token || !newName.trim()) return;
    setLoading(true);
    try {
      await api.createPath(token, {
        name: newName,
        method: createMethod,
        goal: createMethod === "ai_generated" ? newGoal : undefined,
      });
      const res = await api.listPaths(token);
      setPaths(res.paths);
      setActivePath(newName);
      setShowCreate(false);
      setNewName("");
      setNewGoal("");
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (name: string) => {
    if (!token || !confirm(`Delete "${name}"?`)) return;
    await api.deletePath(token, name);
    const res = await api.listPaths(token);
    setPaths(res.paths);
    if (activePath === name) setActivePath(null);
  };

  const handleTopicNav = async (dir: -1 | 1) => {
    if (!token || !activePath || !activeData) return;
    const topics = activeData.topics;
    const idx = topics.indexOf(activeData.current_topic);
    const newIdx = Math.max(0, Math.min(topics.length - 1, idx + dir));
    const newTopic = topics[newIdx];
    await api.setTopic(token, activePath, newTopic);
    const res = await api.listPaths(token);
    setPaths(res.paths);
  };

  const handleSend = async () => {
    if (!input.trim() || chatLoading || !token || !activePath) return;
    setChatLoading(true);
    try {
      await api.sendMessage(token, {
        message: input,
        path_name: activePath,
        topic: activeData?.current_topic,
      });
      const pathsRes = await api.listPaths(token);
      setPaths(pathsRes.paths);
      setInput("");
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setChatLoading(false);
    }
  };

  const selectPath = (name: string) => {
    setActivePath(name);
    setSidebarOpen(false); // close on mobile after selection
  };

  // Guest users cannot use learning paths
  if (isGuest && !token) {
    return (
      <AppLayout>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center max-w-sm">
            <FiBook className="mx-auto text-text-secondary mb-4" size={40} />
            <h2 className="text-lg font-semibold text-text-primary">Sign In Required</h2>
            <p className="text-sm text-text-secondary mt-2">
              Learning paths require an account to save your progress. Please sign in to use this feature.
            </p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex h-full min-h-0 relative">
        {/* Mobile sidebar toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="md:hidden fixed top-3 right-3 z-50 p-2 rounded-lg bg-bg-tertiary border border-border-default text-text-primary shadow-lg"
        >
          {sidebarOpen ? <FiX size={20} /> : <FiMenu size={20} />}
        </button>

        {/* Mobile overlay */}
        {sidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-black/50 z-30"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Path List Sidebar */}
        <div
          className={`
            fixed md:static inset-y-0 left-0 z-40
            w-72 md:w-64 lg:w-72
            border-r border-border-default bg-bg-secondary flex flex-col
            transform transition-transform duration-200 ease-in-out
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
          `}
        >
          <div className="p-4 border-b border-border-default flex items-center justify-between">
            <h2 className="font-semibold text-sm text-text-primary">Learning Paths</h2>
            <button
              onClick={() => setShowCreate(!showCreate)}
              className="p-1.5 rounded-md hover:bg-bg-tertiary text-text-secondary hover:text-accent-green transition"
            >
              <FiPlus size={18} />
            </button>
          </div>

          {/* Create Form */}
          {showCreate && (
            <div className="p-4 border-b border-border-default space-y-3">
              <div className="flex gap-1">
                <button
                  onClick={() => setCreateMethod("manual")}
                  className={`flex-1 text-xs py-1.5 rounded ${createMethod === "manual" ? "bg-accent-green/15 text-accent-green" : "text-text-secondary"}`}
                >
                  Manual
                </button>
                <button
                  onClick={() => setCreateMethod("ai_generated")}
                  className={`flex-1 text-xs py-1.5 rounded ${createMethod === "ai_generated" ? "bg-accent-green/15 text-accent-green" : "text-text-secondary"}`}
                >
                  AI Generated
                </button>
              </div>
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Path name"
                className="w-full bg-bg-primary border border-border-default rounded-md px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue"
              />
              {createMethod === "ai_generated" && (
                <input
                  value={newGoal}
                  onChange={(e) => setNewGoal(e.target.value)}
                  placeholder="Learning goal..."
                  className="w-full bg-bg-primary border border-border-default rounded-md px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-blue"
                />
              )}
              <button
                onClick={handleCreate}
                disabled={!newName.trim()}
                className="w-full py-2 bg-accent-green text-white text-sm rounded-md hover:bg-accent-greenHover transition disabled:opacity-50"
              >
                Create Path
              </button>
            </div>
          )}

          {/* Path List */}
          <div className="flex-1 overflow-y-auto py-2">
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="spinner" />
              </div>
            ) : Object.keys(paths).length === 0 ? (
              <div className="text-center py-8 px-4">
                <FiBook className="mx-auto text-text-secondary mb-2" size={24} />
                <p className="text-sm text-text-secondary">
                  No paths yet. Create your first learning path!
                </p>
              </div>
            ) : (
              Object.entries(paths).map(([name, data]) => (
                <div
                  key={name}
                  className={`mx-2 mb-1 flex items-center rounded-lg cursor-pointer transition ${
                    activePath === name
                      ? "bg-accent-green/10 border border-accent-green/20"
                      : "hover:bg-bg-tertiary"
                  }`}
                >
                  <button
                    onClick={() => selectPath(name)}
                    className="flex-1 text-left px-3 py-2.5"
                  >
                    <p className="text-sm font-medium text-text-primary truncate">
                      {name}
                    </p>
                    <p className="text-xs text-text-secondary mt-0.5">
                      {data.topics?.length || 0} topics ·{" "}
                      {data.chat_history?.length || 0} messages
                    </p>
                  </button>
                  <button
                    onClick={() => handleDelete(name)}
                    className="p-2 mr-1 text-text-secondary hover:text-accent-red transition"
                  >
                    <FiTrash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {activeData ? (
            <>
              {/* Topic Bar */}
              <div className="px-4 md:px-6 py-3 border-b border-border-default bg-bg-secondary/50 flex items-center gap-2 md:gap-3">
                <button
                  onClick={() => handleTopicNav(-1)}
                  className="p-1.5 rounded-md hover:bg-bg-tertiary text-text-secondary transition flex-shrink-0"
                >
                  <FiChevronLeft size={18} />
                </button>
                <div className="flex-1 text-center min-w-0">
                  <p className="text-sm font-medium truncate">
                    {activeData.current_topic || "Getting Started"}
                  </p>
                  <p className="text-xs text-text-secondary">
                    Topic{" "}
                    {activeData.topics.indexOf(activeData.current_topic) + 1} of{" "}
                    {activeData.topics.length}
                  </p>
                </div>
                <button
                  onClick={() => handleTopicNav(1)}
                  className="p-1.5 rounded-md hover:bg-bg-tertiary text-text-secondary transition flex-shrink-0"
                >
                  <FiChevronRight size={18} />
                </button>
              </div>

              {/* Topics Breadcrumb */}
              <div className="px-4 md:px-6 py-2 border-b border-border-default overflow-x-auto flex gap-2 scrollbar-thin">
                {activeData.topics.map((t, i) => (
                  <button
                    key={i}
                    onClick={() => token && api.setTopic(token, activePath!, t).then(() => api.listPaths(token).then(r => setPaths(r.paths)))}
                    className={`whitespace-nowrap px-3 py-1 rounded-full text-xs transition flex-shrink-0 ${
                      t === activeData.current_topic
                        ? "bg-accent-green/15 text-accent-green border border-accent-green/30"
                        : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>

              {/* Chat */}
              <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 space-y-4">
                {activeData.chat_history.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}
                    >
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
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="chat-bubble-ai flex items-center gap-2">
                      <div className="spinner" />
                      <span className="text-sm text-text-secondary">Thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input */}
              <div className="px-4 md:px-6 py-3 md:py-4 border-t border-border-default">
                <div className="flex gap-2 md:gap-3">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    placeholder={`Ask about ${activeData.current_topic}...`}
                    className="flex-1 bg-bg-primary border border-border-default rounded-lg px-3 md:px-4 py-2.5 md:py-3 text-text-primary placeholder-text-secondary/50 focus:border-accent-blue outline-none transition text-sm"
                  />
                  <button
                    onClick={handleSend}
                    disabled={chatLoading || !input.trim()}
                    className="px-3 md:px-4 py-2.5 md:py-3 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg transition disabled:opacity-50 flex-shrink-0"
                  >
                    <FiSend size={18} />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center p-6">
              <div className="text-center">
                <FiBook className="mx-auto text-text-secondary mb-4" size={40} />
                <h2 className="text-lg font-semibold text-text-primary">Select a Learning Path</h2>
                <p className="text-sm text-text-secondary mt-1">
                  Choose a path from the sidebar or create a new one
                </p>
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="mt-4 md:hidden px-4 py-2 bg-accent-green text-white rounded-lg text-sm hover:bg-accent-greenHover transition"
                >
                  Open Paths
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
