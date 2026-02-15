/**
 * EduAI — API Client
 * Typed fetch wrapper for all backend endpoints.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Helper ────────────────────────────────────────────────────────────────────

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }

  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface AuthResponse {
  token: string;
  uid: string;
  email: string;
  nickname: string;
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  signup: (email: string, password: string, nickname?: string) =>
    request<AuthResponse>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, nickname }),
    }),

  getProfile: (token: string) =>
    request<any>("/api/auth/profile", {}, token),

  updateProfile: (token: string, updates: Record<string, any>) =>
    request<any>("/api/auth/profile", {
      method: "PATCH",
      body: JSON.stringify(updates),
    }, token),

  // Chat
  sendMessage: (token: string, data: {
    message: string;
    path_name?: string;
    topic?: string;
    response_style?: string;
    language?: string;
    model_hint?: string;
  }) =>
    request<{ reply: string; model_used: string; emotion_detected: string }>(
      "/api/chat/send",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),

  sendGuestMessage: (data: {
    message: string;
    response_style?: string;
    language?: string;
  }) =>
    request<{ reply: string; model_used: string; emotion_detected: string }>(
      "/api/chat/send-guest",
      { method: "POST", body: JSON.stringify(data) },
    ),

  feynmanChat: (token: string, data: {
    message: string;
    history: { role: string; content: string }[];
  }) =>
    request<{ reply: string }>(
      "/api/chat/feynman",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),

  // Learning Paths
  listPaths: (token: string) =>
    request<{ paths: Record<string, any> }>("/api/paths/", {}, token),

  createPath: (token: string, data: {
    name: string;
    method?: string;
    goal?: string;
  }) =>
    request<any>("/api/paths/create", {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  getPath: (token: string, pathName: string) =>
    request<any>(`/api/paths/${encodeURIComponent(pathName)}`, {}, token),

  deletePath: (token: string, pathName: string) =>
    request<any>(`/api/paths/${encodeURIComponent(pathName)}`, {
      method: "DELETE",
    }, token),

  setTopic: (token: string, pathName: string, topic: string) =>
    request<any>(`/api/paths/${encodeURIComponent(pathName)}/topic?topic=${encodeURIComponent(topic)}`, {
      method: "PATCH",
    }, token),

  // Quiz
  generateQuiz: (token: string, topic: string, numQuestions?: number) =>
    request<{ questions: any[] }>("/api/quiz/generate", {
      method: "POST",
      body: JSON.stringify({ topic, num_questions: numQuestions || 5 }),
    }, token),

  submitQuiz: (token: string, data: {
    path_name: string;
    topic: string;
    answers: Record<number, string>;
    questions: any[];
  }) =>
    request<{ score: number; total: number; details: any[] }>("/api/quiz/submit", {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  getReviewItems: (token: string) =>
    request<{ items: any[] }>("/api/quiz/review", {}, token),

  updateReview: (token: string, itemId: string, quality: number) =>
    request<any>("/api/quiz/review/update", {
      method: "POST",
      body: JSON.stringify({ item_id: itemId, quality }),
    }, token),

  // Tools
  getCareerPaths: (token: string | null, data: {
    interests: string;
    skills?: string;
    education?: string;
    location?: string;
    aspirations?: string;
    budget?: string;
  }) =>
    request<{ paths_markdown: string; skills_gap: Record<string, number> | null }>(
      token ? "/api/tools/career" : "/api/tools/career-guest",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),

  summarize: (token: string, text: string, format: string) =>
    request<{ summary: string }>("/api/tools/summarize", {
      method: "POST",
      body: JSON.stringify({ text, format }),
    }, token),

  getDashboard: (token: string) =>
    request<{
      stats: { xp: number; level: number; badges: string[]; total_messages: number; total_paths: number };
      activity_by_path: Record<string, number>;
    }>("/api/tools/dashboard", {}, token),

  getGreeting: (token: string) =>
    request<{
      greeting: string;
      tip: string;
      total_paths: number;
      total_messages: number;
      date_display: string;
    }>("/api/tools/greeting", {}, token),

  // Vision
  visionSolve: (imageBase64: string, prompt?: string) =>
    request<{ answer: string; model_used: string }>("/api/tools/vision", {
      method: "POST",
      body: JSON.stringify({ image_base64: imageBase64, prompt: prompt || undefined }),
    }),

  // Flashcards
  generateFlashcards: (topic: string, numCards?: number) =>
    request<{ cards: { question: string; answer: string }[]; topic: string }>("/api/tools/flashcards", {
      method: "POST",
      body: JSON.stringify({ topic, num_cards: numCards || 10 }),
    }),

  // Chat with image (uses vision endpoint)
  chatWithImage: (imageBase64: string, message: string) =>
    request<{ answer: string; model_used: string }>("/api/tools/vision", {
      method: "POST",
      body: JSON.stringify({ image_base64: imageBase64, prompt: message }),
    }),

  // Debate Arena
  debateStart: (topic: string, userStance: string, totalRounds?: number) =>
    request<{
      ai_argument: string;
      scores: { logic: number; evidence: number; persuasion: number; fallacies: string[]; feedback: string };
      round_number: number;
      is_final: boolean;
    }>("/api/tools/debate/start", {
      method: "POST",
      body: JSON.stringify({ topic, user_stance: userStance, total_rounds: totalRounds || 3 }),
    }),

  debateRound: (data: {
    topic: string;
    user_stance: string;
    round_number: number;
    total_rounds: number;
    user_argument: string;
    history: any[];
  }) =>
    request<{
      ai_argument: string;
      scores: { logic: number; evidence: number; persuasion: number; fallacies: string[]; feedback: string };
      round_number: number;
      is_final: boolean;
    }>("/api/tools/debate/round", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  debateFinal: (topic: string, userStance: string, history: any[]) =>
    request<{
      summary: string;
      total_score: { logic: number; evidence: number; persuasion: number };
      strengths: string[];
      weaknesses: string[];
      recommendation: string;
      winner: string;
    }>("/api/tools/debate/final", {
      method: "POST",
      body: JSON.stringify({ topic, user_stance: userStance, history }),
    }),

  // Health
  health: () => request<{ status: string }>("/api/health"),
};
