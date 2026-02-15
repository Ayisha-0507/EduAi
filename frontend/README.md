# EduAI — AI-Powered Learning Platform (PWA)

A full-stack Progressive Web App that brings personalized AI tutoring to any device. Built with **Next.js 14** (frontend) and **FastAPI** (backend), backed by Firebase and OpenRouter AI.

---

## Features

| Feature | Description |
|---|---|
| **AI Chat** | Multi-model chat with auto-routing, emotion detection, and 5 tutor personas |
| **Learning Paths** | Structured AI-generated curricula with topic-by-topic navigation |
| **Feynman Board** | Teach-the-AI mode — the AI plays a confused student so you learn by explaining |
| **Career Path Finder** | Personalized career recommendations with skills-gap visualization |
| **Textbook Summarizer** | Paste chapters → get bullet summaries, flashcards, or exam notes |
| **Dashboard** | XP bar, level progression, 16 achievement badges, charts |
| **Spaced Repetition** | SM-2 algorithm schedules quiz review items automatically |
| **PWA** | Installable on desktop & mobile, works full-screen |

---

## Architecture

```
EduAi/
├── backend/                 # FastAPI (Python)
│   ├── main.py              # App entry + CORS + Firebase init
│   ├── config.py            # Env settings & constants
│   ├── auth_utils.py        # JWT creation / verification
│   ├── models/schemas.py    # Pydantic models
│   ├── routers/             # 5 route modules
│   │   ├── auth.py          # login / signup / profile
│   │   ├── chat.py          # AI chat + Feynman
│   │   ├── learning_paths.py
│   │   ├── quiz.py          # Generate & grade quizzes
│   │   └── tools.py         # Career, Summarizer, Dashboard, Greeting
│   ├── services/
│   │   ├── ai_service.py    # OpenRouter / model routing / prompts
│   │   └── firebase_service.py  # Firestore + Storage operations
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                # Next.js 14 (React 18)
│   ├── public/
│   │   └── manifest.json    # PWA manifest
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing / Login
│   │   │   ├── chat/page.tsx       # Chat
│   │   │   ├── learn/page.tsx      # Learning Paths
│   │   │   ├── dashboard/page.tsx  # Dashboard
│   │   │   ├── feynman/page.tsx    # Feynman Board
│   │   │   ├── career/page.tsx     # Career Path Finder
│   │   │   ├── summarizer/page.tsx # Textbook Summarizer
│   │   │   └── settings/page.tsx   # Settings
│   │   ├── components/
│   │   │   ├── auth/LoginForm.tsx
│   │   │   └── layout/Sidebar.tsx, AppLayout.tsx
│   │   ├── lib/
│   │   │   ├── firebase.ts   # Firebase Client SDK
│   │   │   ├── api.ts        # Typed fetch wrapper
│   │   │   └── store.ts      # Zustand state
│   │   └── styles/globals.css
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── .env.example
│
└── README.md                # ← You are here
```

---

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- A **Firebase** project (Auth + Firestore + Storage enabled)
- An **OpenRouter** API key ([openrouter.ai](https://openrouter.ai))

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/EduAi.git
cd EduAi
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env` from the template:

```bash
cp .env.example .env
```

Fill in:

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter key |
| `FIREBASE_CREDENTIALS_PATH` | Path to `firebase_credentials.json` |
| `JWT_SECRET` | A random secret string for signing tokens |

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Check health: `GET /api/health`.

### 3. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local` from the template:

```bash
cp .env.example .env.local
```

Fill in your Firebase web-app config values (found in Firebase Console → Project Settings → Web App):

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend URL (`http://localhost:8000`) |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase API key |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | `yourproject.firebaseapp.com` |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | `yourproject.appspot.com` |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Messaging sender ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase App ID |

Start the dev server:

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## Deployment

### Frontend → GitHub Pages

The Next.js app is configured for static export (`output: "export"` in `next.config.js`).

```bash
cd frontend
npm run build    # → generates /out folder
```

Push the `out/` folder to the `gh-pages` branch or configure GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: cd frontend && npm ci && npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: frontend/out
```

**Important:** Update `NEXT_PUBLIC_API_URL` in your GitHub environment secrets to point to the deployed backend URL.

### Backend → Render / Railway / Fly.io

GitHub Pages is static-only, so the FastAPI backend must be hosted separately. Free-tier options:

| Host | How |
|---|---|
| **Render** | Connect repo → New Web Service → Build: `pip install -r requirements.txt` → Start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Railway** | Connect repo → Add Python service → `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Fly.io** | `fly launch` → deploy via Dockerfile |

Set environment variables (OPENROUTER_API_KEY, JWT_SECRET, etc.) in the hosting dashboard.

---

## PWA Installation

Once deployed, users can install the app:

- **Desktop (Chrome/Edge):** Click the install icon in the address bar
- **Android:** Tap "Add to Home Screen" in the browser menu
- **iOS:** Safari → Share → "Add to Home Screen"

---

## AI Models Used

| Key | Model | Best For |
|---|---|---|
| `deepseek` | DeepSeek V3 | General tutoring, reasoning |
| `arcee` | Arcee Blitz | Programming, code review |
| `nous` | NousHermes 2 Mixtral | Creative explanations, analogies |
| `blackforest` | FLUX.1 | Image generation |
| `nemotron` | NVIDIA Nemotron | Textbook content, diagrams |
| `qwen_vl` | Qwen2.5 VL | Science, math, visual Q&A |

In **Auto** mode, the system analyzes your question and routes to the best model.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| State | Zustand (persisted) |
| PWA | next-pwa, Web App Manifest |
| Charts | Recharts |
| Backend | FastAPI, Pydantic, Uvicorn |
| Auth | Firebase Auth (email + Google) + JWT |
| Database | Cloud Firestore |
| Storage | Firebase Storage |
| AI | OpenRouter API (6 models) |

---

## License

MIT
