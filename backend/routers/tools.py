# ── Video Generation ─────────────────────────────────────────────────────────
from models.schemas import VideoRequest, VideoResponse
router = APIRouter()

@router.post("/video", response_model=VideoResponse)
async def video_generate(req: VideoRequest):
    """Generate a video using the Veo model from a text prompt."""
    import asyncio
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: ai.generate_video(req.prompt),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return VideoResponse(**result)
"""
EduAI Backend — Tools Router
Career path, summarizer, and dashboard endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends

from models.schemas import (
    CareerRequest, CareerResponse,
    SummarizerRequest, SummarizerResponse,
    DashboardResponse, GamificationStats, GreetingResponse,
    VisionRequest, VisionResponse,
    FlashcardRequest, FlashcardResponse,
    DebateStartRequest, DebateRoundRequest, DebateRoundResponse,
    DebateFinalRequest, DebateFinalResponse,
)
from services import ai_service as ai
from services import firebase_service as fb
from auth_utils import get_current_user

router = APIRouter(prefix="/api/tools", tags=["tools"])


# ── Career Path ────────────────────────────────────────────────────────────────

@router.post("/career", response_model=CareerResponse)
async def career_path(req: CareerRequest, user=Depends(get_current_user)):
    """Generate personalized career path recommendations."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        paths_md = await loop.run_in_executor(
            None,
            lambda: ai.generate_career_paths(
                req.interests, req.skills, req.education,
                req.location, req.aspirations, req.budget,
            ),
        )
        skills_gap = None
        if req.skills:
            skills_gap = await loop.run_in_executor(
                None,
                lambda: ai.generate_skills_gap(req.skills),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CareerResponse(paths_markdown=paths_md, skills_gap=skills_gap)


@router.post("/career-guest", response_model=CareerResponse)
async def career_path_guest(req: CareerRequest):
    """Generate career paths for guest users (no auth required)."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        paths_md = await loop.run_in_executor(
            None,
            lambda: ai.generate_career_paths(
                req.interests, req.skills, req.education,
                req.location, req.aspirations, req.budget,
            ),
        )
        skills_gap = None
        if req.skills:
            skills_gap = await loop.run_in_executor(
                None,
                lambda: ai.generate_skills_gap(req.skills),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CareerResponse(paths_markdown=paths_md, skills_gap=skills_gap)


# ── Summarizer ─────────────────────────────────────────────────────────────────

@router.post("/summarize", response_model=SummarizerResponse)
async def summarize(req: SummarizerRequest, user=Depends(get_current_user)):
    """Summarize text in the requested format."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        summary = await loop.run_in_executor(
            None, lambda: ai.generate_summary(req.text, req.format.value)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return SummarizerResponse(summary=summary)


@router.post("/summarize-guest", response_model=SummarizerResponse)
async def summarize_guest(req: SummarizerRequest):
    """Summarize text for guest users (no auth required)."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        summary = await loop.run_in_executor(
            None, lambda: ai.generate_summary(req.text, req.format.value)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return SummarizerResponse(summary=summary)


# ── Dashboard ──────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(user=Depends(get_current_user)):
    """Get full dashboard data: stats, badges, activity."""
    uid = user["uid"]
    paths = fb.get_learning_paths(uid)

    # Compute gamification
    gamification = fb.compute_gamification(uid, paths)

    # Activity by path
    activity_by_path = {}
    for name, data in paths.items():
        if isinstance(data, dict):
            activity_by_path[name] = len(data.get("chat_history", []))

    stats = GamificationStats(
        xp=gamification["xp"],
        level=gamification["level"],
        badges=gamification["badges"],
        total_messages=gamification["total_messages"],
        total_paths=gamification["total_paths"],
    )

    return DashboardResponse(
        stats=stats,
        activity_by_path=activity_by_path,
    )


# ── Vision Solver ──────────────────────────────────────────────────────────────

@router.post("/vision", response_model=VisionResponse)
async def vision_solve(req: VisionRequest):
    """Analyze an image using a vision model. No auth required."""
    import asyncio
    if not req.image_base64.strip():
        raise HTTPException(status_code=400, detail="Image data cannot be empty")
    try:
        loop = asyncio.get_event_loop()
        answer, model_used = await loop.run_in_executor(
            None,
            lambda: ai.solve_vision(req.image_base64, req.prompt),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return VisionResponse(answer=answer, model_used=model_used)


# ── Flashcard Generator ───────────────────────────────────────────────────────

@router.post("/flashcards", response_model=FlashcardResponse)
async def generate_flashcards(req: FlashcardRequest):
    """Generate flashcards from a topic. No auth required."""
    import asyncio
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    try:
        loop = asyncio.get_event_loop()
        cards = await loop.run_in_executor(
            None,
            lambda: ai.generate_flashcards(req.topic, req.num_cards),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return FlashcardResponse(cards=cards, topic=req.topic)


# ── Debate Arena ───────────────────────────────────────────────────────────────

@router.post("/debate/start")
async def debate_start(req: DebateStartRequest):
    """Get the AI's opening argument for a debate. No auth required."""
    import asyncio
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: ai.debate_round(
                topic=req.topic,
                user_stance=req.user_stance,
                round_number=0,
                total_rounds=req.total_rounds,
                user_argument=None,
                history=[],
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/debate/round", response_model=DebateRoundResponse)
async def debate_round(req: DebateRoundRequest):
    """Submit user argument, get AI counter-argument + scores."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: ai.debate_round(
                topic=req.topic,
                user_stance=req.user_stance,
                round_number=req.round_number,
                total_rounds=req.total_rounds,
                user_argument=req.user_argument,
                history=req.history,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/debate/final", response_model=DebateFinalResponse)
async def debate_final(req: DebateFinalRequest):
    """Get final debate summary and overall scores."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: ai.debate_final(req.topic, req.user_stance, req.history),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ── Greeting ───────────────────────────────────────────────────────────────────

@router.get("/greeting", response_model=GreetingResponse)
async def greeting(user=Depends(get_current_user)):
    """Get a context-aware greeting."""
    profile = fb.get_user_profile(user["uid"])
    paths = fb.get_learning_paths(user["uid"])
    total_msgs = sum(
        len(p.get("chat_history", []))
        for p in paths.values()
        if isinstance(p, dict)
    )

    g = fb.get_greeting(profile.get("nickname", ""))
    return GreetingResponse(
        greeting=g["greeting"],
        tip=g["tip"],
        total_paths=len(paths),
        total_messages=total_msgs,
        date_display=g["date_display"],
    )
