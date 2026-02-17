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
    AI_MODELS: dict = {
        "gemini-2.5-pro": "models/gemini-2.5-pro",
        "gemini-2.5-flash": "models/gemini-2.5-flash",
        "gemini-2.0-flash": "models/gemini-2.0-flash",
        "gemini-2.0-flash-lite": "models/gemini-2.0-flash-lite",
        "nano": "models/gemini-nano"
    }

    # Default model-ah ippo gemini-2.5-pro-ku mathidalam
    FALLBACK_MODELS: list = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash",
        "google/gemini-3-pro-preview",
    ]
    # ── AI ──────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Google Studio API
    GOOGLE_STUDIO_API_KEY: str = os.getenv("GOOGLE_STUDIO_API_KEY", "")


   

    # ...existing code...
    
    

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
