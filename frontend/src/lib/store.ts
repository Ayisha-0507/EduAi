/**
 * EduAI — Global Store (Zustand)
 * Manages auth state, token, user profile, and chat history.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface UserProfile {
  uid: string;
  email: string;
  nickname: string;
  full_name: string;
  bio: string;
  avatar_url: string;
  tutor_persona: string;
  model_selection_mode: string;
  manual_model_choice: string;
  preferred_language: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  model?: string;
  emotion?: string;
  timestamp: number; // epoch ms
}

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  isLoggedIn: boolean;
  isGuest: boolean;

  // Chat history keyed by date string "YYYY-MM-DD"
  chatHistory: Record<string, ChatMessage[]>;

  setAuth: (token: string, user: UserProfile) => void;
  setGuest: () => void;
  updateUser: (partial: Partial<UserProfile>) => void;
  logout: () => void;

  addChatMessage: (msg: ChatMessage) => void;
  getChatForDate: (date: string) => ChatMessage[];
  getChatDates: () => string[];
}

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isLoggedIn: false,
      isGuest: false,
      chatHistory: {},

      setAuth: (token, user) =>
        set({ token, user, isLoggedIn: true, isGuest: false }),

      setGuest: () =>
        set({
          token: null,
          user: {
            uid: "guest",
            email: "",
            nickname: "Explorer",
            full_name: "",
            bio: "",
            avatar_url: "",
            tutor_persona: "Friendly Encourager",
            model_selection_mode: "Auto",
            manual_model_choice: "deepseek",
            preferred_language: "English",
          },
          isLoggedIn: false,
          isGuest: true,
        }),

      updateUser: (partial) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partial } : null,
        })),

      logout: () =>
        set({ token: null, user: null, isLoggedIn: false, isGuest: false, chatHistory: {} }),

      addChatMessage: (msg) =>
        set((state) => {
          const key = todayKey();
          const existing = state.chatHistory[key] || [];
          return {
            chatHistory: {
              ...state.chatHistory,
              [key]: [...existing, msg],
            },
          };
        }),

      getChatForDate: (date) => {
        return get().chatHistory[date] || [];
      },

      getChatDates: () => {
        return Object.keys(get().chatHistory).sort().reverse();
      },
    }),
    {
      name: "eduai-auth",
    }
  )
);
