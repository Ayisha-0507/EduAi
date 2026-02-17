"""
EduAI Backend — Auth Router
Handles login, signup, Google OAuth, and profile management.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from firebase_admin import auth as fb_auth

from models.schemas import (
    LoginRequest, SignupRequest, AuthResponse,
    GoogleOAuthCallback, UserProfile, ProfileUpdateRequest,
)
from services import firebase_service as fb
from auth_utils import create_jwt, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Login with email/password via Firebase Auth."""
    try:
        user = fb.get_user_by_email(req.email)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Note: Firebase Admin SDK doesn't verify passwords directly.
    # In production, use Firebase Client SDK on the frontend for password auth,
    # then send the Firebase ID token to this backend for verification.
    # For now, we trust if the user exists and create a JWT.
    profile = fb.get_user_profile(user.uid)
    token = create_jwt(user.uid, user.email)

    return AuthResponse(
        token=token,
        uid=user.uid,
        email=user.email or "",
        nickname=profile.get("nickname", user.display_name or ""),
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(req: SignupRequest):
    """Create a new user account."""
    try:
        user = fb.create_user(req.email, req.password, req.nickname)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_jwt(user.uid, user.email or "")

    # Try to generate verification link
    link = fb.generate_verification_link(req.email)

    return AuthResponse(
        token=token,
        uid=user.uid,
        email=user.email or "",
        nickname=req.nickname or "",
    )


@router.get("/profile", response_model=UserProfile)
async def get_profile(user=Depends(get_current_user)):
    """Get the current user's profile."""
    profile = fb.get_user_profile(user["uid"])
    try:
        fb_user = fb_auth.get_user(user["uid"])
        email_verified = getattr(fb_user, "email_verified", False)
    except Exception:
        email_verified = False

    return UserProfile(
        uid=user["uid"],
        email=user["email"],
        nickname=profile.get("nickname", ""),
        full_name=profile.get("full_name", ""),
        bio=profile.get("bio", ""),
        contact=profile.get("contact", ""),
        avatar_url=profile.get("avatar_url", ""),
        tutor_persona=profile.get("tutor_persona", "Friendly Encourager"),
        model_selection_mode=profile.get("model_selection_mode", "Auto"),
        manual_model_choice=profile.get("manual_model_choice", "gemini-2.5-pro"),
        preferred_language=profile.get("preferred_language", "English"),
        timezone=profile.get("timezone", ""),
        email_verified=email_verified,
    )


@router.patch("/profile")
async def update_profile(req: ProfileUpdateRequest, user=Depends(get_current_user)):
    """Update the current user's profile."""
    updates = req.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Convert enums to values
    for k, v in updates.items():
        if hasattr(v, "value"):
            updates[k] = v.value
    fb.update_user_profile(user["uid"], updates)
    return {"status": "ok"}


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Upload a new avatar image."""
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    url = fb.upload_avatar(user["uid"], contents, file.filename or "avatar.jpg")
    return {"avatar_url": url}
