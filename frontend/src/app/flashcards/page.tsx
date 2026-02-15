"use client";

import { useState } from "react";
import { FiRotateCw, FiLoader, FiChevronLeft, FiChevronRight, FiShuffle, FiArrowLeft } from "react-icons/fi";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import { api } from "@/lib/api";

interface Flashcard {
  question: string;
  answer: string;
}

export default function FlashcardsPage() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [numCards, setNumCards] = useState(10);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!topic.trim() || loading) return;
    setLoading(true);
    setError(null);
    setCards([]);
    setCurrentIndex(0);
    setFlipped(false);
    try {
      const res = await api.generateFlashcards(topic.trim(), numCards);
      if (res.cards.length === 0) {
        setError("No flashcards generated. Try a different topic.");
      } else {
        setCards(res.cards);
      }
    } catch (e: any) {
      setError(e.message || "Failed to generate flashcards.");
    } finally {
      setLoading(false);
    }
  };

  const nextCard = () => {
    setFlipped(false);
    setCurrentIndex((i) => (i + 1) % cards.length);
  };

  const prevCard = () => {
    setFlipped(false);
    setCurrentIndex((i) => (i - 1 + cards.length) % cards.length);
  };

  const shuffleCards = () => {
    setFlipped(false);
    const shuffled = [...cards].sort(() => Math.random() - 0.5);
    setCards(shuffled);
    setCurrentIndex(0);
  };

  const card = cards[currentIndex];

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col items-center justify-start p-4 md:p-6 gap-4 md:gap-6 overflow-y-auto">
        <div className="w-full max-w-2xl space-y-6">
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
              <h1 className="text-2xl font-bold text-text-primary">Flashcard Generator</h1>
              <p className="text-text-secondary text-sm">AI creates flashcards from any topic for quick revision</p>
            </div>
          </div>

          {/* Topic Input */}
          <div className="bg-bg-secondary rounded-xl border border-border-default p-5 space-y-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                placeholder="Enter a topic (e.g. Photosynthesis, Python Lists, World War 2)"
                className="flex-1 bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/30 outline-none transition"
              />
              <select
                value={numCards}
                onChange={(e) => setNumCards(Number(e.target.value))}
                className="bg-bg-primary border border-border-default rounded-lg px-3 py-3 text-text-primary focus:border-accent-blue outline-none"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={15}>15</option>
                <option value={20}>20</option>
              </select>
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading || !topic.trim()}
              className="w-full py-3 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <FiLoader className="animate-spin" size={18} /> Generating...
                </>
              ) : (
                <>
                  <FiRotateCw size={18} /> Generate Flashcards
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-300">
              {error}
            </div>
          )}

          {/* Flashcard Display */}
          {cards.length > 0 && (
            <div className="space-y-4">
              {/* Counter + Shuffle */}
              <div className="flex items-center justify-between text-text-secondary text-sm">
                <span>
                  Card {currentIndex + 1} of {cards.length}
                </span>
                <button
                  onClick={shuffleCards}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-bg-tertiary hover:bg-border-default transition text-text-secondary hover:text-text-primary border border-border-default"
                >
                  <FiShuffle size={14} /> Shuffle
                </button>
              </div>

              {/* Card */}
              <div
                onClick={() => setFlipped(!flipped)}
                className="cursor-pointer select-none"
              >
                <div
                  className={`relative w-full min-h-[250px] rounded-2xl border-2 transition-all duration-500 flex items-center justify-center p-8 text-center ${
                    flipped
                      ? "bg-gradient-to-br from-green-900/30 to-emerald-900/20 border-green-600/50"
                      : "bg-gradient-to-br from-cyan-900/20 to-purple-900/20 border-cyan-600/30 hover:border-cyan-500/50"
                  }`}
                >
                  <div>
                    <span
                      className={`text-xs font-medium uppercase tracking-wider mb-3 block ${
                        flipped ? "text-green-400" : "text-cyan-400"
                      }`}
                    >
                      {flipped ? "Answer" : "Question"}
                    </span>
                    <p className="text-lg text-text-primary leading-relaxed">
                      {flipped ? card.answer : card.question}
                    </p>
                    <p className="text-xs text-text-secondary mt-4">
                      {flipped ? "Click to see question" : "Click to reveal answer"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-center gap-4">
                <button
                  onClick={prevCard}
                  className="p-3 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
                >
                  <FiChevronLeft size={20} />
                </button>

                {/* Progress dots */}
                <div className="flex gap-1.5 flex-wrap justify-center max-w-[200px]">
                  {cards.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => { setCurrentIndex(i); setFlipped(false); }}
                      className={`w-2.5 h-2.5 rounded-full transition ${
                        i === currentIndex
                          ? "bg-cyan-500 scale-125"
                          : "bg-bg-tertiary hover:bg-border-default"
                      }`}
                    />
                  ))}
                </div>

                <button
                  onClick={nextCard}
                  className="p-3 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
                >
                  <FiChevronRight size={20} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
