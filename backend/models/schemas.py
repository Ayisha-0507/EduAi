"""
EduAI Backend — Pydantic Schemas
Request/response models for all API endpoints.
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────────────

class TutorPersona(str, Enum):
    FRIENDLY = "Friendly Encourager"
    STRICT = "Strict Professor"
    SOCRATIC = "Socratic Questioner"
    CONCISE = "Concise Technician"
    CREATIVE = "Creative Storyteller"


class ModelSelectionMode(str, Enum):
    AUTO = "Auto"
    MANUAL = "Manual"


class ModelKey(str, Enum):
    DEEPSEEK = "deepseek"
    ARCEE = "arcee"
    NOUS = "nous"
    BLACKFOREST = "blackforest"
    NEMOTRON = "nemotron"
    QWEN_VL = "qwen_vl"


class ResponseStyle(str, Enum):
    DEFAULT = "default"
    SIMPLE = "simple"
    CODE = "code"
    ANALOGY = "analogy"


class SummaryFormat(str, Enum):
    BULLETS = "Bullet-point summary"
    FLASHCARDS = "Flashcards (Q&A)"
    EXAM_NOTES = "Exam answer notes"
    MIND_MAP = "Mind map outline"
    ALL = "All formats"


# ── Auth ───────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    nickname: Optional[str] = None


class AuthResponse(BaseModel):
    token: str
    uid: str
    email: str
    nickname: str = ""


class GoogleOAuthCallback(BaseModel):
    code: str


# ── User Profile ───────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    uid: str
    email: str
    nickname: str = ""
    full_name: str = ""
    bio: str = ""
    contact: str = ""
    avatar_url: str = ""
    tutor_persona: TutorPersona = TutorPersona.FRIENDLY
    model_selection_mode: ModelSelectionMode = ModelSelectionMode.AUTO
    manual_model_choice: ModelKey = ModelKey.DEEPSEEK
    preferred_language: str = "English"
    timezone: str = ""
    email_verified: bool = False


class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    contact: Optional[str] = None
    tutor_persona: Optional[TutorPersona] = None
    model_selection_mode: Optional[ModelSelectionMode] = None
    manual_model_choice: Optional[ModelKey] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None


# ── Chat ───────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[float] = None


class ChatRequest(BaseModel):
    message: str
    path_name: Optional[str] = None
    topic: Optional[str] = None
    response_style: ResponseStyle = ResponseStyle.DEFAULT
    language: str = "English"
    model_hint: Optional[ModelKey] = None


class ChatResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    reply: str
    model_used: str
    emotion_detected: str = ""


# ── Learning Paths ─────────────────────────────────────────────────────────────

class CreatePathRequest(BaseModel):
    name: str
    method: str = "manual"  # "manual" | "ai_generated"
    goal: Optional[str] = None  # used for AI-generated paths


class LearningPath(BaseModel):
    name: str
    topics: list[str] = []
    current_topic: str = ""
    chat_history: list[ChatMessage] = []
    path_type: str = "standard"


class PathListResponse(BaseModel):
    paths: dict[str, LearningPath]


# ── Quiz ───────────────────────────────────────────────────────────────────────

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    answer: str


class QuizGenerateRequest(BaseModel):
    topic: str
    path_name: Optional[str] = None
    num_questions: int = 5


class QuizSubmitRequest(BaseModel):
    path_name: str
    topic: str
    answers: dict[int, str]  # question_index -> selected_answer
    questions: list[QuizQuestion]


class QuizResult(BaseModel):
    score: int
    total: int
    details: list[dict]


# ── Career ─────────────────────────────────────────────────────────────────────

class CareerRequest(BaseModel):
    interests: str
    skills: str = ""
    education: str = "12th Pass"
    location: str = "City"
    aspirations: str = ""
    budget: str = "Free resources only"


class CareerResponse(BaseModel):
    paths_markdown: str
    skills_gap: Optional[dict] = None


# ── Summarizer ─────────────────────────────────────────────────────────────────

class SummarizerRequest(BaseModel):
    text: str
    format: SummaryFormat = SummaryFormat.BULLETS


class SummarizerResponse(BaseModel):
    summary: str


# ── Feynman ────────────────────────────────────────────────────────────────────

class FeynmanRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


# ── Dashboard / Gamification ──────────────────────────────────────────────────

class GamificationStats(BaseModel):
    xp: int = 0
    level: int = 1
    badges: list[str] = []
    total_messages: int = 0
    total_paths: int = 0
    streak_days: int = 0


class DashboardResponse(BaseModel):
    stats: GamificationStats
    activity_by_path: dict[str, int] = {}
    recent_activity: list[dict] = []


# ── SRS (Spaced Repetition) ──────────────────────────────────────────────────

class ReviewItem(BaseModel):
    id: str
    topic: str
    question_data: Optional[dict] = None
    due_date: str
    interval: int = 1
    ease_factor: float = 2.5


class ReviewUpdateRequest(BaseModel):
    item_id: str
    quality: int = Field(ge=0, le=5)  # SM-2 quality rating


# ── Vision ────────────────────────────────────────────────────────────────────

class VisionRequest(BaseModel):
    image_base64: str
    prompt: str = "This is an educational problem. Solve it step-by-step and provide a clear explanation."


class VisionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    answer: str
    model_used: str


# ── Greeting ──────────────────────────────────────────────────────────────────

class GreetingResponse(BaseModel):
    greeting: str
    tip: str
    total_paths: int
    total_messages: int
    date_display: str
