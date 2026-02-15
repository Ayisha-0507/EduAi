"""
EduAI Backend — Firebase Service
Handles all Firestore & Firebase Auth operations.
Ported from app.py's Firebase helper functions.
"""

from __future__ import annotations
import os
from datetime import datetime, timedelta
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, auth, firestore, storage

from config import settings

# ── Initialization ─────────────────────────────────────────────────────────────

_db = None


def init_firebase():
    """Initialize Firebase Admin SDK and return the Firestore client."""
    global _db
    if _db is not None:
        return _db

    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        app_options = {}
        if settings.FIREBASE_STORAGE_BUCKET:
            app_options["storageBucket"] = settings.FIREBASE_STORAGE_BUCKET
        firebase_admin.initialize_app(cred, app_options)

    _db = firestore.client()
    return _db


def get_db():
    """Get the Firestore client (initializes on first call)."""
    global _db
    if _db is None:
        init_firebase()
    return _db


# ── Auth Helpers ───────────────────────────────────────────────────────────────

def create_user(email: str, password: str, nickname: str | None = None) -> auth.UserRecord:
    """Create a Firebase Auth user and initialize their Firestore profile."""
    user_record = auth.create_user(email=email, password=password, display_name=nickname)
    db = get_db()
    db.collection("users").document(user_record.uid).set(
        {
            "email": email,
            "nickname": nickname or "",
            "full_name": "",
            "bio": "",
            "contact": "",
            "avatar_url": "",
            "tutor_persona": "Friendly Encourager",
            "model_selection_mode": "Auto",
            "manual_model_choice": "deepseek",
            "preferred_language": "English",
            "timezone": "",
            "created_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )
    return user_record


def get_user_by_email(email: str) -> auth.UserRecord:
    """Get Firebase Auth user record by email."""
    return auth.get_user_by_email(email)


def get_user_profile(uid: str) -> dict:
    """Retrieve the Firestore profile for a user."""
    db = get_db()
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict() or {}
    return {}


def update_user_profile(uid: str, updates: dict) -> None:
    """Update specific fields in a user's Firestore profile."""
    db = get_db()
    updates["updated_at"] = firestore.SERVER_TIMESTAMP
    db.collection("users").document(uid).set(updates, merge=True)


def generate_verification_link(email: str) -> str | None:
    """Generate an email verification link for the user."""
    try:
        return auth.generate_email_verification_link(email)
    except Exception:
        return None


# ── Learning Paths ─────────────────────────────────────────────────────────────

def get_learning_paths(uid: str) -> dict:
    """Fetch all learning paths for a user."""
    db = get_db()
    doc = db.collection("learning_paths").document(uid).get()
    return doc.to_dict() if doc.exists else {}


def save_learning_path(uid: str, path_name: str, path_data: dict) -> None:
    """Save/update a single learning path."""
    db = get_db()
    db.collection("learning_paths").document(uid).set(
        {path_name: path_data}, merge=True
    )


def delete_learning_path(uid: str, path_name: str) -> None:
    """Delete a learning path."""
    db = get_db()
    db.collection("learning_paths").document(uid).update(
        {path_name: firestore.DELETE_FIELD}
    )


# ── Chat History ───────────────────────────────────────────────────────────────

def append_chat_message(uid: str, path_name: str, role: str, content: str) -> None:
    """Append a message to a learning path's chat history."""
    db = get_db()
    paths = get_learning_paths(uid)
    path_data = paths.get(path_name, {"chat_history": [], "topics": [], "current_topic": ""})
    path_data.setdefault("chat_history", [])
    path_data["chat_history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().timestamp(),
    })
    save_learning_path(uid, path_name, path_data)


# ── Quiz ───────────────────────────────────────────────────────────────────────

def save_quiz_attempt(uid: str, path_name: str, topic: str, score: int, total: int) -> None:
    """Save a quiz attempt record."""
    db = get_db()
    db.collection("quiz_attempts").document().set({
        "user_id": uid,
        "path_name": path_name,
        "topic": topic,
        "score": score,
        "total": total,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })


def get_quiz_count(uid: str) -> int:
    """Count quiz attempts for a user."""
    db = get_db()
    try:
        docs = list(
            db.collection("quiz_attempts")
            .where(field_path="user_id", op_string="==", value=uid)
            .stream()
        )
        return len(docs)
    except Exception:
        return 0


# ── Feedback ───────────────────────────────────────────────────────────────────

def save_feedback(uid: str, path_name: str, topic: str, feedback: str, response: str, style: str = "", persona: str = "") -> None:
    """Store user feedback on an AI response."""
    db = get_db()
    db.collection("user_feedback").document().set({
        "user_id": uid,
        "path_name": path_name,
        "topic": topic,
        "feedback": feedback,
        "response": response,
        "style": style,
        "persona": persona,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })


# ── Spaced Repetition (SRS) ───────────────────────────────────────────────────

def get_review_items(uid: str, only_due: bool = True, limit: int = 20) -> list[dict]:
    """Fetch review queue items for a user."""
    db = get_db()
    try:
        query = db.collection("review_queue").where(field_path="user_id", op_string="==", value=uid)
        docs = list(query.stream())
        items = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Convert Firestore timestamp to string
            due = data.get("due_date")
            if hasattr(due, "isoformat"):
                data["due_date"] = due.isoformat()
            elif hasattr(due, "timestamp"):
                data["due_date"] = datetime.fromtimestamp(due.timestamp()).isoformat()
            items.append(data)

        if only_due:
            now = datetime.now()
            items = [
                item for item in items
                if datetime.fromisoformat(str(item.get("due_date", ""))) <= now
            ]

        return items[:limit]
    except Exception:
        return []


def update_review_item(item_id: str, quality: int) -> dict:
    """Apply SM-2 algorithm to update a review item's schedule."""
    db = get_db()
    doc_ref = db.collection("review_queue").document(item_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("Review item not found")

    data = doc.to_dict()
    ef = data.get("ease_factor", 2.5)
    interval = data.get("interval", 1)

    # SM-2 algorithm
    if quality < 3:
        interval = 1
    else:
        if interval == 1:
            interval = 6
        else:
            interval = round(interval * ef)

    ef += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    if ef < 1.3:
        ef = 1.3

    new_due = datetime.now() + timedelta(days=interval)
    doc_ref.update({
        "due_date": new_due,
        "interval": interval,
        "ease_factor": ef,
    })

    return {"interval": interval, "ease_factor": ef, "next_due": new_due.isoformat()}


def create_review_item(uid: str, path_name: str, topic: str, question_data: dict | None = None) -> None:
    """Create a new SRS review item."""
    db = get_db()
    db.collection("review_queue").document().set({
        "user_id": uid,
        "path_name": path_name,
        "topic": topic,
        "question_data": question_data,
        "due_date": datetime.now() + timedelta(days=1),
        "interval": 1,
        "ease_factor": 2.5,
        "created_at": firestore.SERVER_TIMESTAMP,
    })


# ── Avatar Upload ──────────────────────────────────────────────────────────────

def upload_avatar(uid: str, file_bytes: bytes, filename: str) -> str:
    """Upload avatar to Firebase Storage and return the public URL."""
    try:
        bucket = storage.bucket()
        ext = Path(filename).suffix or ".jpg"
        blob = bucket.blob(f"avatars/{uid}{ext}")
        blob.upload_from_string(file_bytes, content_type=f"image/{ext.lstrip('.')}")
        blob.make_public()
        url = blob.public_url
        # Update profile with avatar URL
        update_user_profile(uid, {"avatar_url": url})
        return url
    except Exception as e:
        raise RuntimeError(f"Avatar upload failed: {e}")


# ── Gamification ───────────────────────────────────────────────────────────────

def compute_gamification(uid: str, paths: dict, feature_flags: dict | None = None) -> dict:
    """
    Compute XP, level, and badges for a user.
    feature_flags: optional dict like {"used_feynman": True, ...}
    Returns {"xp": int, "level": int, "badges": list[str], "total_messages": int, "total_paths": int}
    """
    badges = []
    total_msgs = sum(len(p.get("chat_history", [])) for p in paths.values())
    total_paths = len(paths)
    feature_flags = feature_flags or {}

    # Tier 1: Getting Started
    if total_paths >= 1:
        badges.append("Explorer")
    if total_msgs >= 5:
        badges.append("First Steps")

    # Tier 2: Active Learning
    if total_msgs >= 20:
        badges.append("Active Learner")
    if total_msgs >= 50:
        badges.append("Knowledge Seeker")
    if total_msgs >= 100:
        badges.append("Dedicated Scholar")
    if total_paths >= 3:
        badges.append("Multi-Path Explorer")
    if total_paths >= 5:
        badges.append("Pathfinder")

    # Tier 3: Quizzing
    quiz_count = get_quiz_count(uid)
    if quiz_count >= 1:
        badges.append("Quiz Taker")
    if quiz_count >= 3:
        badges.append("Quizzer")
    if quiz_count >= 10:
        badges.append("Quiz Champion")

    # Tier 4: Feature usage
    flag_badge_map = {
        "used_feynman": "Feynman Teacher",
        "used_vision": "Visual Learner",
        "used_social_impact": "Social Impact Hero",
        "used_career_path": "Career Explorer",
        "used_summarizer": "Speed Reader",
        "used_collab_solver": "Community Builder",
    }
    for flag, badge in flag_badge_map.items():
        if feature_flags.get(flag):
            badges.append(badge)

    # XP
    from config import settings as s
    xp = total_msgs * s.XP_PER_MESSAGE + total_paths * s.XP_PER_PATH + len(badges) * s.XP_PER_BADGE

    # Level
    level = 1
    for i, threshold in enumerate(s.LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1

    return {
        "xp": xp,
        "level": level,
        "badges": badges,
        "total_messages": total_msgs,
        "total_paths": total_paths,
    }


def get_greeting(nickname: str = "") -> dict:
    """Generate a context-aware greeting based on time of day."""
    now = datetime.now()
    hour = now.hour

    if hour < 5:
        greeting = "Burning the midnight oil"
        tip = "Consider short audio-based lessons for late-night study."
    elif hour < 12:
        greeting = "Good morning"
        tip = "Morning sessions are great for complex problem-solving."
    elif hour < 17:
        greeting = "Good afternoon"
        tip = "Try a quick quiz to stay sharp after lunch."
    elif hour < 21:
        greeting = "Good evening"
        tip = "Evening is perfect for review and revision."
    else:
        greeting = "Late night session"
        tip = "Keep sessions short. Try micro-lessons for quick learning."

    display_name = f", {nickname}" if nickname else ""
    return {
        "greeting": f"{greeting}{display_name}",
        "tip": tip,
        "date_display": now.strftime("%A, %b %d"),
    }
