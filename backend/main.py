"""
EduAI Backend — FastAPI Main Application
Entry point with CORS, lifecycle, and router registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from services.firebase_service import init_firebase
from routers import auth, chat, learning_paths, quiz, tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Firebase on startup."""
    init_firebase()
    yield


app = FastAPI(
    title="EduAI API",
    description="Adaptive Multi-Model Tutoring Platform API",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ayisha-0507.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(learning_paths.router)
app.include_router(quiz.router)
app.include_router(tools.router)


# ── Health Check ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
