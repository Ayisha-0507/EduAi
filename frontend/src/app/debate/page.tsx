"use client";

import { useState, useRef, useEffect } from "react";
import {
  FiArrowLeft,
  FiSend,
  FiZap,
  FiAlertTriangle,
  FiAward,
  FiChevronRight,
  FiRotateCw,
} from "react-icons/fi";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import { api } from "@/lib/api";
import { playSendSound } from "@/lib/sfx";

interface Scores {
  logic: number;
  evidence: number;
  persuasion: number;
  fallacies: string[];
  feedback: string;
}

interface RoundData {
  round: number;
  user: string;
  ai: string;
  scores: Scores;
}

interface FinalResult {
  summary: string;
  total_score: { logic: number; evidence: number; persuasion: number };
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
  winner: string;
}

type Phase = "setup" | "debating" | "results";

export default function DebatePage() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("setup");

  // Setup
  const [topic, setTopic] = useState("");
  const [stance, setStance] = useState<"for" | "against">("for");
  const [totalRounds, setTotalRounds] = useState(3);

  // Debate
  const [currentRound, setCurrentRound] = useState(1);
  const [aiOpening, setAiOpening] = useState("");
  const [userInput, setUserInput] = useState("");
  const [history, setHistory] = useState<RoundData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestAi, setLatestAi] = useState("");
  const [latestScores, setLatestScores] = useState<Scores | null>(null);

  // Results
  const [finalResult, setFinalResult] = useState<FinalResult | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, latestAi, finalResult]);

  const aiStance = stance === "for" ? "against" : "for";

  // ── Start Debate ──
  const handleStart = async () => {
    if (!topic.trim() || loading) return;
    playSendSound();
    setLoading(true);
    setError(null);
    try {
      const res = await api.debateStart(topic.trim(), stance, totalRounds);
      setAiOpening(res.ai_argument);
      setPhase("debating");
      setCurrentRound(1);
      setHistory([]);
      setLatestAi("");
      setLatestScores(null);
    } catch (e: any) {
      if (e.message?.includes("Not Found")) {
        setError("Debate service not reachable. Please refresh and try again.");
      } else {
        setError(e.message || "Failed to start debate.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ── Submit Argument ──
  const handleSubmitArgument = async () => {
    if (!userInput.trim() || loading) return;
    playSendSound();
    setLoading(true);
    setError(null);
    const arg = userInput.trim();
    setUserInput("");

    try {
      const res = await api.debateRound({
        topic,
        user_stance: stance,
        round_number: currentRound,
        total_rounds: totalRounds,
        user_argument: arg,
        history: history.map((h) => ({
          round: h.round,
          user: h.user,
          ai: h.ai,
          scores: h.scores,
        })),
      });

      const newRound: RoundData = {
        round: currentRound,
        user: arg,
        ai: res.ai_argument,
        scores: res.scores,
      };

      const updatedHistory = [...history, newRound];
      setHistory(updatedHistory);
      setLatestAi(res.ai_argument);
      setLatestScores(res.scores);

      if (res.is_final || currentRound >= totalRounds) {
        // Get final results
        const finalRes = await api.debateFinal(topic, stance, updatedHistory);
        setFinalResult(finalRes);
        setPhase("results");
      } else {
        setCurrentRound((r) => r + 1);
      }
    } catch (e: any) {
      setError(e.message || "Failed to process round.");
    } finally {
      setLoading(false);
    }
  };

  // ── Reset ──
  const handleReset = () => {
    setPhase("setup");
    setTopic("");
    setStance("for");
    setCurrentRound(1);
    setAiOpening("");
    setHistory([]);
    setLatestAi("");
    setLatestScores(null);
    setFinalResult(null);
    setError(null);
  };

  // ── Score Bar ──
  const ScoreBar = ({ label, value, max = 10 }: { label: string; value: number; max?: number }) => (
    <div className="flex items-center gap-2">
      <span className="text-xs text-text-secondary w-20">{label}</span>
      <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${(value / max) * 100}%`,
            background:
              value >= 8
                ? "linear-gradient(90deg, #10b981, #34d399)"
                : value >= 5
                ? "linear-gradient(90deg, #f59e0b, #fbbf24)"
                : "linear-gradient(90deg, #ef4444, #f87171)",
          }}
        />
      </div>
      <span className="text-xs font-bold text-text-primary w-6 text-right">{value}</span>
    </div>
  );

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col items-center justify-start p-4 md:p-6 gap-4 md:gap-6 overflow-y-auto">
        <div className="w-full max-w-3xl space-y-6">
          {/* Header */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
              title="Go back"
            >
              <FiArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
                <FiZap className="text-amber-400" /> Debate Arena
              </h1>
              <p className="text-text-secondary text-sm">
                Argue your stance against AI — get scored on logic, evidence &amp; persuasion
              </p>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* ═══════════ SETUP PHASE ═══════════ */}
          {phase === "setup" && (
            <div className="glass-card space-y-5">
              <div>
                <label className="block text-sm text-text-secondary mb-1.5">Debate Topic</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleStart()}
                  placeholder="e.g. 'AI will replace teachers', 'Nuclear energy is the future'"
                  className="w-full bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 outline-none transition"
                />
              </div>

              <div>
                <label className="block text-sm text-text-secondary mb-1.5">Your Stance</label>
                <div className="flex gap-3">
                  <button
                    onClick={() => setStance("for")}
                    className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition border ${
                      stance === "for"
                        ? "bg-accent-green/20 border-accent-green text-accent-green"
                        : "bg-bg-tertiary border-border-default text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    👍 FOR
                  </button>
                  <button
                    onClick={() => setStance("against")}
                    className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition border ${
                      stance === "against"
                        ? "bg-red-500/20 border-red-500 text-red-400"
                        : "bg-bg-tertiary border-border-default text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    👎 AGAINST
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm text-text-secondary mb-1.5">Rounds</label>
                <div className="flex gap-2">
                  {[2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      onClick={() => setTotalRounds(n)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition border ${
                        totalRounds === n
                          ? "bg-accent-blue/20 border-accent-blue text-accent-blue"
                          : "bg-bg-tertiary border-border-default text-text-secondary hover:text-text-primary"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleStart}
                disabled={!topic.trim() || loading}
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <>
                    <FiZap size={18} />
                    Start Debate
                  </>
                )}
              </button>
            </div>
          )}

          {/* ═══════════ DEBATING PHASE ═══════════ */}
          {phase === "debating" && (
            <div className="space-y-4">
              {/* Topic banner */}
              <div className="glass-card py-3 px-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div>
                  <span className="text-xs text-text-secondary">Topic:</span>
                  <p className="text-sm font-medium text-text-primary">{topic}</p>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs px-2 py-1 rounded-full bg-accent-green/20 text-accent-green border border-accent-green/30">
                    You: {stance.toUpperCase()}
                  </span>
                  <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    AI: {aiStance.toUpperCase()}
                  </span>
                  <span className="text-xs text-text-secondary">
                    Round {currentRound}/{totalRounds}
                  </span>
                </div>
              </div>

              {/* AI Opening */}
              {aiOpening && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center flex-shrink-0 mt-1">
                    <FiZap size={14} className="text-purple-400" />
                  </div>
                  <div className="glass-card flex-1 border-purple-500/20">
                    <p className="text-xs text-purple-400 mb-1 font-medium">AI Opening ({aiStance})</p>
                    <p className="text-sm text-text-primary leading-relaxed">{aiOpening}</p>
                  </div>
                </div>
              )}

              {/* Previous rounds */}
              {history.map((round, idx) => (
                <div key={idx} className="space-y-3">
                  {/* User argument */}
                  <div className="flex gap-3 justify-end">
                    <div className="glass-card max-w-[80%] border-accent-green/20">
                      <p className="text-xs text-accent-green mb-1 font-medium">
                        You — Round {round.round} ({stance})
                      </p>
                      <p className="text-sm text-text-primary leading-relaxed">{round.user}</p>
                    </div>
                  </div>

                  {/* Scores */}
                  <div className="glass-card mx-1 sm:mx-8 bg-bg-tertiary/50 space-y-2">
                    <p className="text-xs font-medium text-amber-400 flex items-center gap-1">
                      <FiAward size={12} /> Round {round.round} Scores
                    </p>
                    <ScoreBar label="Logic" value={round.scores.logic} />
                    <ScoreBar label="Evidence" value={round.scores.evidence} />
                    <ScoreBar label="Persuasion" value={round.scores.persuasion} />
                    {round.scores.fallacies.length > 0 && (
                      <div className="flex items-start gap-1.5 mt-1">
                        <FiAlertTriangle size={12} className="text-red-400 mt-0.5 flex-shrink-0" />
                        <p className="text-xs text-red-400">
                          Fallacies: {round.scores.fallacies.join(", ")}
                        </p>
                      </div>
                    )}
                    {round.scores.feedback && (
                      <p className="text-xs text-text-secondary italic">{round.scores.feedback}</p>
                    )}
                  </div>

                  {/* AI counter */}
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center flex-shrink-0 mt-1">
                      <FiZap size={14} className="text-purple-400" />
                    </div>
                    <div className="glass-card flex-1 border-purple-500/20">
                      <p className="text-xs text-purple-400 mb-1 font-medium">
                        AI Counter — Round {round.round} ({aiStance})
                      </p>
                      <p className="text-sm text-text-primary leading-relaxed">{round.ai}</p>
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading skeleton */}
              {loading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center flex-shrink-0 mt-1 animate-pulse">
                    <FiZap size={14} className="text-purple-400" />
                  </div>
                  <div className="glass-card flex-1 space-y-2.5 animate-pulse">
                    <div className="h-3 bg-border-default/60 rounded-full w-[85%]" />
                    <div className="h-3 bg-border-default/40 rounded-full w-[65%]" />
                    <div className="h-3 bg-border-default/30 rounded-full w-[45%]" />
                  </div>
                </div>
              )}

              <div ref={scrollRef} />

              {/* Input area */}
              {!loading && currentRound <= totalRounds && (
                <div className="glass-card border-accent-green/20 space-y-3">
                  <p className="text-xs text-text-secondary">
                    Round {currentRound} of {totalRounds} — Present your argument ({stance})
                  </p>
                  <textarea
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmitArgument();
                      }
                    }}
                    placeholder="Type your argument... (Enter to submit, Shift+Enter for newline)"
                    rows={3}
                    className="w-full bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-accent-green focus:ring-1 focus:ring-accent-green/30 outline-none transition resize-none text-sm"
                  />
                  <button
                    onClick={handleSubmitArgument}
                    disabled={!userInput.trim()}
                    className="w-full py-2.5 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <FiSend size={14} />
                    Submit Argument
                    {currentRound === totalRounds && " (Final Round)"}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ═══════════ RESULTS PHASE ═══════════ */}
          {phase === "results" && finalResult && (
            <div className="space-y-5">
              {/* Winner card */}
              <div
                className={`glass-card text-center py-6 border-2 ${
                  finalResult.winner === "student"
                    ? "border-accent-green/50 bg-accent-green/5"
                    : finalResult.winner === "tie"
                    ? "border-amber-500/50 bg-amber-500/5"
                    : "border-purple-500/50 bg-purple-500/5"
                }`}
              >
                <div className="text-4xl mb-2">
                  {finalResult.winner === "student" ? "🏆" : finalResult.winner === "tie" ? "🤝" : "🤖"}
                </div>
                <h2 className="text-xl font-bold text-text-primary mb-1">
                  {finalResult.winner === "student"
                    ? "You Won!"
                    : finalResult.winner === "tie"
                    ? "It's a Tie!"
                    : "AI Wins This Round"}
                </h2>
                <p className="text-sm text-text-secondary max-w-md mx-auto">
                  {finalResult.summary}
                </p>
              </div>

              {/* Overall scores */}
              <div className="glass-card space-y-3">
                <h3 className="text-sm font-medium text-amber-400 flex items-center gap-1.5">
                  <FiAward size={14} /> Overall Scores
                </h3>
                <ScoreBar label="Logic" value={finalResult.total_score.logic} />
                <ScoreBar label="Evidence" value={finalResult.total_score.evidence} />
                <ScoreBar label="Persuasion" value={finalResult.total_score.persuasion} />
                <div className="pt-2 border-t border-border-default">
                  <p className="text-xs text-text-secondary">
                    Average:{" "}
                    <span className="text-text-primary font-bold">
                      {(
                        (finalResult.total_score.logic +
                          finalResult.total_score.evidence +
                          finalResult.total_score.persuasion) /
                        3
                      ).toFixed(1)}
                      /10
                    </span>
                  </p>
                </div>
              </div>

              {/* Strengths / Weaknesses */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="glass-card space-y-2">
                  <h3 className="text-sm font-medium text-accent-green">💪 Strengths</h3>
                  <ul className="space-y-1">
                    {finalResult.strengths.map((s, i) => (
                      <li key={i} className="text-xs text-text-primary flex items-start gap-1.5">
                        <FiChevronRight size={12} className="text-accent-green mt-0.5 flex-shrink-0" />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="glass-card space-y-2">
                  <h3 className="text-sm font-medium text-red-400">⚡ Areas to Improve</h3>
                  <ul className="space-y-1">
                    {finalResult.weaknesses.map((w, i) => (
                      <li key={i} className="text-xs text-text-primary flex items-start gap-1.5">
                        <FiChevronRight size={12} className="text-red-400 mt-0.5 flex-shrink-0" />
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Recommendation */}
              <div className="glass-card border-accent-blue/20">
                <h3 className="text-sm font-medium text-accent-blue mb-1.5">📚 Study Recommendation</h3>
                <p className="text-sm text-text-primary leading-relaxed">
                  {finalResult.recommendation}
                </p>
              </div>

              {/* Play again */}
              <button
                onClick={handleReset}
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white rounded-lg font-medium transition flex items-center justify-center gap-2"
              >
                <FiRotateCw size={16} />
                New Debate
              </button>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
