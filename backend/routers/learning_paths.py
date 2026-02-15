"""
EduAI Backend — Learning Paths Router
CRUD for learning paths + topic management.
"""

from fastapi import APIRouter, HTTPException, Depends

from models.schemas import CreatePathRequest, LearningPath, ChatMessage
from services import ai_service as ai
from services import firebase_service as fb
from auth_utils import get_current_user

router = APIRouter(prefix="/api/paths", tags=["learning-paths"])


@router.get("/")
async def list_paths(user=Depends(get_current_user)):
    """Get all learning paths for the current user."""
    paths_raw = fb.get_learning_paths(user["uid"])
    paths = {}
    for name, data in paths_raw.items():
        if isinstance(data, dict):
            paths[name] = {
                "name": name,
                "topics": data.get("topics", []),
                "current_topic": data.get("current_topic", ""),
                "chat_history": data.get("chat_history", []),
                "path_type": data.get("path_type", "standard"),
            }
    return {"paths": paths}


@router.post("/create")
async def create_path(req: CreatePathRequest, user=Depends(get_current_user)):
    """Create a new learning path (manual or AI-generated)."""
    uid = user["uid"]

    # Check if path name already exists
    existing = fb.get_learning_paths(uid)
    if req.name in existing:
        raise HTTPException(status_code=400, detail="A path with this name already exists")

    topics = []
    if req.method == "ai_generated" and req.goal:
        try:
            topics = ai.generate_learning_path_topics(req.goal)
        except Exception:
            topics = [req.goal]
    elif req.method == "manual":
        topics = [req.name]

    path_data = {
        "topics": topics,
        "current_topic": topics[0] if topics else "",
        "chat_history": [],
        "path_type": "standard",
    }

    fb.save_learning_path(uid, req.name, path_data)
    return {"status": "created", "path": {"name": req.name, **path_data}}


@router.delete("/{path_name}")
async def delete_path(path_name: str, user=Depends(get_current_user)):
    """Delete a learning path."""
    try:
        fb.delete_learning_path(user["uid"], path_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "deleted"}


@router.patch("/{path_name}/topic")
async def set_current_topic(path_name: str, topic: str, user=Depends(get_current_user)):
    """Set the current topic for a learning path."""
    uid = user["uid"]
    paths = fb.get_learning_paths(uid)
    path_data = paths.get(path_name)
    if not path_data:
        raise HTTPException(status_code=404, detail="Path not found")

    path_data["current_topic"] = topic
    fb.save_learning_path(uid, path_name, path_data)
    return {"status": "ok", "current_topic": topic}


@router.get("/{path_name}")
async def get_path(path_name: str, user=Depends(get_current_user)):
    """Get a specific learning path with full chat history."""
    paths = fb.get_learning_paths(user["uid"])
    path_data = paths.get(path_name)
    if not path_data:
        raise HTTPException(status_code=404, detail="Path not found")

    return {
        "name": path_name,
        "topics": path_data.get("topics", []),
        "current_topic": path_data.get("current_topic", ""),
        "chat_history": path_data.get("chat_history", []),
        "path_type": path_data.get("path_type", "standard"),
    }
