"use client";

/**
 * EduAI — Chat Page.
 */

import { useState, useRef, useEffect } from "react";
import { useAuthStore, ChatMessage } from "@/lib/store";
import { api } from "@/lib/api";
import { playSendSound } from "@/lib/sfx";
import AppLayout from "@/components/layout/AppLayout";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FiSend,
  FiZap,
  FiCode,
  FiBookOpen,
  FiGlobe,
  FiCopy,
  FiCheck,
  FiCalendar,
  FiChevronLeft,
  FiMic,
  FiMicOff,
  FiPaperclip,
  FiX,
} from "react-icons/fi";

const STYLE_BUTTONS = [
  { key: "default", label: "Default", icon: FiZap },
  { key: "simple", label: "Simple", icon: FiBookOpen },
  { key: "code", label: "Code", icon: FiCode },
  { key: "analogy", label: "Analogy", icon: FiGlobe },
];

const LANGUAGES = [
  "English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam",
  "Bengali", "Marathi", "Gujarati", "Urdu", "Odia", "Punjabi",
  "French", "Spanish", "Arabic",
];

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function formatDateLabel(dateStr: string) {
  const today = todayKey();
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  if (dateStr === today) return "Today";
  if (dateStr === yesterday) return "Yesterday";
  return new Date(dateStr + "T00:00:00").toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export default function ChatPage() {
  const { token, isGuest, chatHistory, addChatMessage, getChatDates } =
    useAuthStore();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [style, setStyle] = useState("default");
  const [language, setLanguage] = useState("English");
  const [greeting, setGreeting] = useState<any>(null);
  const [copied, setCopied] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState(todayKey());
  const [showDatePanel, setShowDatePanel] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const [attachedPreview, setAttachedPreview] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const dates = getChatDates();
  // Derive messages directly from the store — no stale closures
  const messages = chatHistory[selectedDate] || [];
  const isToday = selectedDate === todayKey();

  const toggleVoice = () => {
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      return;
    }
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = language === "English" ? "en-US" : language === "Hindi" ? "hi-IN" : language === "Tamil" ? "ta-IN" : "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => (prev ? prev + " " + transcript : transcript));
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  };

  const handleImageAttach = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setAttachedPreview(dataUrl);
      setAttachedImage(dataUrl.split(",")[1]);
    };
    reader.readAsDataURL(file);
  };

  const clearAttachment = () => {
    setAttachedImage(null);
    setAttachedPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Load greeting on mount
  useEffect(() => {
    if (token) {
      api.getGreeting(token).then(setGreeting).catch(() => {});
    }
  }, [token]);

  // Auto-scroll when messages change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if ((!input.trim() && !attachedImage) || loading) return;

    playSendSound();

    // Capture input before clearing
    const msg = input.trim();
    const hasImage = !!attachedImage;
    const imageToSend = attachedImage;
    const userMsg: ChatMessage = {
      role: "user",
      content: hasImage ? `${msg || "(image)"}\n📎 Image attached` : msg,
      timestamp: Date.now(),
    };
    addChatMessage(userMsg);
    setInput("");
    clearAttachment();
    setLoading(true);

    // Switch to today if viewing old date
    if (!isToday) setSelectedDate(todayKey());

    try {
      let res;
      if (hasImage && imageToSend) {
        // Image attached — use vision endpoint
        const visionRes = await api.chatWithImage(imageToSend, msg || "Describe this image");
        res = { reply: visionRes.answer, model_used: visionRes.model_used, emotion_detected: undefined };
      } else if (isGuest || !token) {
        // Guest mode — use unauthenticated endpoint
        res = await api.sendGuestMessage({
          message: msg,
          response_style: style,
          language,
        });
      } else {
        res = await api.sendMessage(token, {
          message: msg,
          response_style: style,
          language,
        });
      }
      const aiMsg: ChatMessage = {
        role: "assistant",
        content: res.reply,
        model: res.model_used,
        emotion: res.emotion_detected,
        timestamp: Date.now(),
      };
      addChatMessage(aiMsg);
    } catch (err: any) {
      const errMsg: ChatMessage = {
        role: "assistant",
        content: `Error: ${err.message}`,
        timestamp: Date.now(),
      };
      addChatMessage(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopied(idx);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <AppLayout>
      <div className="flex h-screen">
        {/* Date sidebar panel */}
        <div
          className={`${
            showDatePanel ? "w-48 border-r border-border-default" : "w-0"
          } bg-[#010409] flex-shrink-0 overflow-hidden transition-all duration-200`}
        >
          <div className="p-3">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
              Chat History
            </h3>
            {dates.length === 0 ? (
              <p className="text-xs text-text-secondary">No history yet</p>
            ) : (
              <div className="space-y-1">
                {dates.map((d) => (
                  <button
                    key={d}
                    onClick={() => {
                      setSelectedDate(d);
                      setShowDatePanel(false);
                    }}
                    className={`w-full text-left px-3 py-2 rounded-md text-xs transition ${
                      d === selectedDate
                        ? "bg-accent-green/15 text-accent-green"
                        : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
                    }`}
                  >
                    {formatDateLabel(d)}
                    <span className="block text-[10px] opacity-60">
                      {(chatHistory[d] || []).length} messages
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main chat area */}
        <div className="flex flex-col flex-1 min-w-0">
          {/* Header */}
          <header className="px-3 md:px-6 py-3 border-b border-border-default bg-bg-secondary/50 flex items-center gap-3">
            <button
              onClick={() => setShowDatePanel(!showDatePanel)}
              className="p-2 rounded-md hover:bg-bg-tertiary text-text-secondary transition"
              title="Chat history"
            >
              {showDatePanel ? <FiChevronLeft size={16} /> : <FiCalendar size={16} />}
            </button>
            <div className="flex-1 min-w-0">
              {greeting && isToday ? (
                <>
                  <h1 className="text-sm font-semibold truncate">{greeting.greeting}</h1>
                  <p className="text-xs text-text-secondary truncate">{greeting.tip}</p>
                </>
              ) : !isToday ? (
                <h1 className="text-sm font-semibold">
                  Chat from {formatDateLabel(selectedDate)}
                </h1>
              ) : (
                <h1 className="text-sm font-semibold">Home Chat</h1>
              )}
            </div>
            {!isToday && (
              <button
                onClick={() => setSelectedDate(todayKey())}
                className="text-xs px-3 py-1.5 bg-accent-green/15 text-accent-green rounded-md hover:bg-accent-green/25 transition"
              >
                Back to Today
              </button>
            )}
          </header>

          {/* Controls Bar */}
          <div className="px-3 md:px-6 py-2 border-b border-border-default flex flex-wrap items-center gap-2">
            <div className="flex gap-1">
              {STYLE_BUTTONS.map((s) => (
                <button
                  key={s.key}
                  onClick={() => setStyle(s.key)}
                  className={`flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition ${
                    style === s.key
                      ? "bg-accent-green/15 text-accent-green border border-accent-green/30"
                      : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary border border-transparent"
                  }`}
                >
                  <s.icon size={13} />
                  {s.label}
                </button>
              ))}
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="ml-auto bg-bg-primary border border-border-default rounded-md px-2 py-1.5 text-xs text-text-primary outline-none"
            >
              {LANGUAGES.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 md:px-6 py-4 space-y-4">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-4xl mb-4">🧠</div>
                  <h2 className="text-lg font-semibold text-text-primary">
                    {isToday ? "Start a conversation" : "No messages on this day"}
                  </h2>
                  <p className="text-sm text-text-secondary mt-1 max-w-md">
                    {isToday
                      ? "Ask me anything — math, science, coding, career advice. I'll route your question to the best AI model automatically."
                      : "Select a different date or go back to today to chat."}
                  </p>
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={`${selectedDate}-${i}`}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={
                    msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"
                  }
                >
                  {msg.role === "assistant" ? (
                    <div className="markdown-body">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-border-default/50">
                        {msg.model && (
                          <span className="text-[10px] text-text-secondary bg-bg-tertiary px-2 py-0.5 rounded">
                            {msg.model}
                          </span>
                        )}
                        {msg.emotion && (
                          <span className="text-[10px] text-accent-yellow bg-accent-yellow/10 px-2 py-0.5 rounded">
                            {msg.emotion}
                          </span>
                        )}
                        <span className="text-[10px] text-text-secondary ml-auto mr-1">
                          {new Date(msg.timestamp).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                        <button
                          onClick={() => handleCopy(msg.content, i)}
                          className="p-1 text-text-secondary hover:text-text-primary transition"
                        >
                          {copied === i ? (
                            <FiCheck size={13} className="text-accent-green" />
                          ) : (
                            <FiCopy size={13} />
                          )}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm">{msg.content}</p>
                      <p className="text-[10px] text-text-secondary/50 mt-1 text-right">
                        {new Date(msg.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="chat-bubble-ai w-[70%] max-w-lg">
                  <div className="space-y-2.5 animate-pulse">
                    <div className="h-3 bg-border-default/60 rounded-full w-[85%]" />
                    <div className="h-3 bg-border-default/40 rounded-full w-[65%]" />
                    <div className="h-3 bg-border-default/30 rounded-full w-[45%]" />
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="px-3 md:px-6 py-3 border-t border-border-default bg-bg-secondary/50">
            {/* Image preview strip */}
            {attachedPreview && (
              <div className="max-w-4xl mx-auto mb-2 flex items-center gap-2">
                <div className="relative inline-block">
                  <img src={attachedPreview} alt="Attached" className="h-16 w-16 object-cover rounded-lg border border-border-default" />
                  <button
                    onClick={clearAttachment}
                    className="absolute -top-1.5 -right-1.5 bg-red-500 text-white rounded-full p-0.5 hover:bg-red-600 transition"
                  >
                    <FiX size={12} />
                  </button>
                </div>
                <span className="text-xs text-text-secondary">Image attached</span>
              </div>
            )}
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="hidden"
              onChange={handleImageAttach}
            />
            <div className="flex gap-2 max-w-4xl mx-auto">
              <button
                onClick={toggleVoice}
                disabled={!isToday}
                className={`px-3 py-3 rounded-lg transition disabled:opacity-50 ${
                  isListening
                    ? "bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse"
                    : "bg-bg-tertiary text-text-secondary hover:text-text-primary border border-border-default"
                }`}
                title={isListening ? "Stop listening" : "Voice input"}
              >
                {isListening ? <FiMicOff size={18} /> : <FiMic size={18} />}
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={!isToday}
                className="px-3 py-3 rounded-lg bg-bg-tertiary text-text-secondary hover:text-text-primary border border-border-default transition disabled:opacity-50"
                title="Attach image"
              >
                <FiPaperclip size={18} />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && !e.shiftKey && handleSend()
                }
                placeholder={isListening ? "Listening..." : isToday ? "Ask anything..." : "Switch to today to chat..."}
                disabled={!isToday}
                className="flex-1 bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 outline-none transition disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={loading || (!input.trim() && !attachedImage) || !isToday}
                className="px-4 py-3 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FiSend size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
