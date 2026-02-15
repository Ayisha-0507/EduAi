"""
EduAI Backend — Quiz Router
Quiz generation, grading, and SRS integration.
"""

from fastapi import APIRouter, HTTPException, Depends

from models.schemas import QuizGenerateRequest, QuizSubmitRequest, QuizResult, ReviewUpdateRequest
from services import ai_service as ai
from services import firebase_service as fb
from auth_utils import get_current_user

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/generate")
async def generate_quiz(req: QuizGenerateRequest, user=Depends(get_current_user)):
    """Generate quiz questions for a topic."""
    try:
        questions = ai.generate_quiz(req.topic, req.num_questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")

    return {"questions": questions}


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(req: QuizSubmitRequest, user=Depends(get_current_user)):
    """Grade a quiz submission and save the attempt."""
    uid = user["uid"]
    score = 0
    details = []

    for i, q in enumerate(req.questions):
        selected = req.answers.get(i, "")
        is_correct = selected == q.answer
        if is_correct:
            score += 1
        details.append({
            "question": q.question,
            "selected": selected,
            "correct": q.answer,
            "is_correct": is_correct,
        })

        # Create SRS review items for wrong answers
        if not is_correct:
            fb.create_review_item(uid, req.path_name, req.topic, {
                "question": q.question,
                "options": q.options,
                "answer": q.answer,
            })

    # Save attempt
    fb.save_quiz_attempt(uid, req.path_name, req.topic, score, len(req.questions))

    return QuizResult(score=score, total=len(req.questions), details=details)


# ── SRS Review Endpoints ──────────────────────────────────────────────────────

@router.get("/review")
async def get_review_items(user=Depends(get_current_user)):
    """Get due SRS review items."""
    items = fb.get_review_items(user["uid"], only_due=True)
    return {"items": items}


@router.post("/review/update")
async def update_review(req: ReviewUpdateRequest, user=Depends(get_current_user)):
    """Update an SRS review item with SM-2 algorithm."""
    try:
        result = fb.update_review_item(req.item_id, req.quality)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result
