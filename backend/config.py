"""
EduAI Backend — Configuration
Loads environment variables and provides typed settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Settings:
    # ── AI ──────────────────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    AI_MODELS: dict = {
        "deepseek":    "deepseek/deepseek-chat-v3-0324:free",
        "arcee":       "meta-llama/llama-3.3-8b-instruct:free",
        "nous":        "mistralai/mistral-small-3.1-24b-instruct:free",
        "blackforest": "black-forest-labs/flux.2-klein-4b",
        "nemotron":    "nvidia/nemotron-nano-12b-v2-vl:free",
        "qwen_vl":     "qwen/qwen3-vl-30b-a3b-thinking:free",
    }

    # Fallback models if primary fails (tried in order)
    FALLBACK_MODELS: list = [
        "meta-llama/llama-3.3-8b-instruct:free",
        "qwen/qwen3-8b:free",
        "google/gemma-3-12b-it:free",
    ]

    # ── Firebase ────────────────────────────────────────────────────────
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        str(Path(__file__).parent.parent / "firebase_credentials.json"),
    )
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")

    # ── Auth / JWT ──────────────────────────────────────────────────────
    JWT_SECRET: str = os.getenv("JWT_SECRET", "eduai-dev-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ── Google OAuth ────────────────────────────────────────────────────
    GOOGLE_OAUTH_CLIENT_ID: str = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
    GOOGLE_OAUTH_CLIENT_SECRET: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
    GOOGLE_OAUTH_REDIRECT_URI: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:3000/auth/callback")

    # ── CORS ────────────────────────────────────────────────────────────
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # ── Gamification ────────────────────────────────────────────────────
    XP_PER_MESSAGE: int = 5
    XP_PER_PATH: int = 50
    XP_PER_BADGE: int = 25
    LEVEL_THRESHOLDS: list = [0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500]


settings = Settings()
