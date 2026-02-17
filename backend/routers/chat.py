"""
EduAI Backend — Chat Router
Handles AI chat, Feynman board, and emotion-aware conversations.
"""

from fastapi import APIRouter, HTTPException, Depends

from models.schemas import ChatRequest, ChatResponse, FeynmanRequest
from services import ai_service as ai
from services import firebase_service as fb
from auth_utils import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(req: ChatRequest, user=Depends(get_current_user)):
    """Send a chat message and get an AI response."""
    import asyncio
    uid = user["uid"]

    # Get user profile for persona preference
    profile = fb.get_user_profile(uid)
    persona = profile.get("tutor_persona", "Friendly Encourager")

    # Detect emotion
    emotion_name, emotion_prefix = ai.detect_emotion(req.message)

    # Use Gemini for all requests
    model_hint = "gemini-2.5-pro"

    # Build chat history from path if provided
    history = []
    if req.path_name:
        paths = fb.get_learning_paths(uid)
        path_data = paths.get(req.path_name, {})
        history = path_data.get("chat_history", [])

    # Build messages
    messages = ai.build_chat_messages(
        user_message=req.message,
        history=history,
        persona=persona,
        response_style=req.response_style.value if req.response_style else "default",
        language=req.language,
        topic=req.topic,
        emotion_prefix=emotion_prefix,
    )

    # Call AI (non-blocking)
    try:
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, lambda: ai.call_ai(messages, model_hint=model_hint))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not reply:
        raise HTTPException(status_code=500, detail="AI returned empty response")

    # Persist to chat history if path provided
    if req.path_name:
        fb.append_chat_message(uid, req.path_name, "user", req.message)
        fb.append_chat_message(uid, req.path_name, "assistant", reply)

    return ChatResponse(
        reply=reply,
        model_used=model_hint,
        emotion_detected=emotion_name,
    )


@router.post("/send-guest", response_model=ChatResponse)
async def send_guest_message(req: ChatRequest):
    """Guest chat — no auth required, no history persistence."""
    import asyncio

    emotion_name, emotion_prefix = ai.detect_emotion(req.message)
    model_hint = ai.auto_route(req.message)

    messages = ai.build_chat_messages(
        user_message=req.message,
        history=[],
        persona="Friendly Encourager",
        response_style=req.response_style.value if req.response_style else "default",
        language=req.language,
        emotion_prefix=emotion_prefix,
    )

    try:
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, lambda: ai.call_ai(messages, model_hint=model_hint))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not reply:
        raise HTTPException(status_code=500, detail="AI returned empty response")

    return ChatResponse(
        reply=reply,
        model_used=model_hint,
        emotion_detected=emotion_name,
    )


@router.post("/feynman", response_model=ChatResponse)
async def feynman_chat(req: FeynmanRequest, user=Depends(get_current_user)):
    """Feynman Board: user teaches the AI, AI asks probing questions."""
    import asyncio
    history = [{"role": m.role, "content": m.content} for m in req.history]

    try:
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(
            None, lambda: ai.generate_feynman_response(req.message, history)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not reply:
        raise HTTPException(status_code=500, detail="AI returned empty response")

    return ChatResponse(reply=reply, model_used="gemini", emotion_detected="")
