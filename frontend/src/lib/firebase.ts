/**
 * EduAI — Firebase Client SDK Configuration
 * Used for client-side auth (email/password + Google sign-in).
 */

import { initializeApp, getApps } from "firebase/app";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  type User,
} from "firebase/auth";

// ── Config ────────────────────────────────────────────────────────────────────
// Replace these with your Firebase project config from the Firebase Console.
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "",
};

// ── Initialize ────────────────────────────────────────────────────────────────

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// ── Auth Functions ────────────────────────────────────────────────────────────

export async function loginWithEmail(email: string, password: string) {
  return signInWithEmailAndPassword(auth, email, password);
}

export async function signupWithEmail(email: string, password: string) {
  return createUserWithEmailAndPassword(auth, email, password);
}

export async function loginWithGoogle() {
  return signInWithPopup(auth, googleProvider);
}

export async function logout() {
  return signOut(auth);
}

export function onAuthChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback);
}

export async function getIdToken(): Promise<string | null> {
  const user = auth.currentUser;
  if (!user) return null;
  return user.getIdToken();
}

export { auth };
export type { User };
