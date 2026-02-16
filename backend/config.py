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
        "deepseek": "google/gemini-2.5-pro",
        "arcee": "google/gemini-2.5-pro",
        "nous": "google/gemini-2.5-pro",
        "blackforest": "google/gemini-2.5-pro",
        "nemotron": "google/gemini-2.5-pro",
        "qwen_vl": "google/gemini-2.5-pro",
        "gemma_vl": "google/gemini-2.5-pro",
    }

    # Fallback models if primary fails (tried in order)
    FALLBACK_MODELS: list = [
        "google/gemini-2.5-pro",
    ]

    # Rate limit retry settings
    RATE_LIMIT_RETRIES: int = 2
    RATE_LIMIT_DELAY: float = 3.0  # seconds between retries

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
