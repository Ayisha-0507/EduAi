# EduAI — Complete Project Documentation

> **Edu AI: Your Personal AI Tutor**
> **Author:** Ayisha
> **Version:** 10.1 — Multi-Model AI (DeepSeek · Arcee · NousHermes · BlackForest)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Architecture & Data Flow](#4-architecture--data-flow)
5. [Setup & Installation](#5-setup--installation)
6. [Configuration](#6-configuration)
7. [Authentication & User Management](#7-authentication--user-management)
8. [Multi-Model AI System](#8-multi-model-ai-system)
9. [Core Features](#9-core-features)
   - 9.1 [Home Chat](#91-home-chat)
   - 9.2 [Learning Paths](#92-learning-paths)
   - 9.3 [Live Vision Solver](#93-live-vision-solver)
   - 9.4 [Feynman Board](#94-feynman-board)
   - 9.5 [Social Impact & Accessibility](#95-social-impact--accessibility)
   - 9.6 [Career Path Finder](#96-career-path-finder)
   - 9.7 [Textbook Summarizer](#97-textbook-summarizer)
   - 9.8 [Collaborative Problem Solver](#98-collaborative-problem-solver)
   - 9.9 [Peer Learning Groups](#99-peer-learning-groups)
   - 9.10 [Spaced Repetition System (SRS)](#910-spaced-repetition-system-srs)
   - 9.11 [Knowledge Graph](#911-knowledge-graph)
   - 9.12 [Dashboard & Analytics](#912-dashboard--analytics)
10. [Gamification System](#10-gamification-system)
11. [Adaptive & Intelligent Features](#11-adaptive--intelligent-features)
12. [Accessibility & Inclusivity](#12-accessibility--inclusivity)
13. [UI/UX Design](#13-uiux-design)
14. [Database Schema](#14-database-schema)
15. [API Reference — Key Functions](#15-api-reference--key-functions)
16. [Deployment & Running](#16-deployment--running)
17. [Utility Scripts](#17-utility-scripts)
18. [Security Considerations](#18-security-considerations)

---

## 1. Project Overview

**EduAI** is a comprehensive, AI-powered personal tutoring platform built with [Streamlit](https://streamlit.io/). It provides an inclusive, adaptive learning experience designed for students from diverse backgrounds — from metro cities to rural villages. The platform combines multiple AI models, gamification, accessibility tools, and social-impact features into a unified web application.

### Key Highlights

- **Multi-Model AI:** Intelligently routes queries to 6 specialized AI models via OpenRouter
- **Adaptive Learning:** Emotional intelligence detection, context-aware greetings, and adaptive tutor personas
- **Social Impact Focus:** Rural analogy engine, bias-free unity filter, SMS simulator, and multi-channel lesson packs
- **Gamification:** XP, levels, badges, and streak tracking to encourage consistent learning
- **Accessibility:** 15 languages, font size controls, high contrast mode, text-to-speech, and voice input
- **Firebase Backend:** Persistent user profiles, learning paths, quiz history, and spaced repetition data

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit (Python) | Web UI framework with reactive components |
| **AI Backend** | OpenRouter API (OpenAI-compatible) | Multi-model AI inference |
| **Database** | Firebase Firestore | User data, learning paths, quiz attempts, feedback |
| **Authentication** | Firebase Auth | Email/password + Google OAuth 2.0 |
| **Storage** | Firebase Cloud Storage | User avatar images |
| **Visualization** | Plotly, streamlit-agraph | Charts, graphs, knowledge maps |
| **Optional UI** | streamlit-ace, streamlit-cropper, streamlit-tour | Code editor, avatar cropping, guided tours |
| **Image Processing** | Pillow (PIL) | Avatar resizing and optimization |

### Python Dependencies (`requirements.txt`)

```
streamlit
openai
firebase-admin
Pillow
google-auth
requests
pandas
plotly
streamlit-agraph
streamlit-ace
streamlit-cropper
```

---

## 3. Project Structure

```
EduAI/
├── app.py                       # Main application (3534 lines, 92 functions)
├── check_models.py              # Utility: test Google Gemini model availability
├── requirements.txt             # Python dependency list
├── firebase_credentials.json    # Firebase service account key (secret)
├── workspace.code-workspace     # VS Code workspace config
├── .streamlit/
│   └── secrets.toml             # API keys and configuration secrets
├── .venv/                       # Python virtual environment
└── __pycache__/                 # Compiled Python bytecode
```

---

## 4. Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT WEB UI                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Home    │ │ Vision   │ │ Feynman  │ │ Social   │ │ Career   │ │
│  │  Chat    │ │ Solver   │ │ Board    │ │ Impact   │ │ Path     │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │             │            │             │            │       │
│       └─────────────┴────────────┴─────────────┴────────────┘       │
│                              │                                      │
│                    ┌─────────▼──────────┐                           │
│                    │  Auto-Router       │                           │
│                    │  _auto_route()     │                           │
│                    └─────────┬──────────┘                           │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   OpenRouter API    │
                    │   (6 AI Models)     │
                    ├─────────────────────┤
                    │ DeepSeek → General  │
                    │ Arcee    → Code     │
                    │ Nous     → Roleplay │
                    │ BlackF.  → Images   │
                    │ Nemotron → Visual   │
                    │ Qwen VL  → Sci/Math │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Firebase Suite    │
                    ├─────────────────────┤
                    │ Auth     → Login    │
                    │ Firestore→ Data     │
                    │ Storage  → Avatars  │
                    └─────────────────────┘
```

### Request Flow

1. User interacts with any feature tab (Home Chat, Vision, etc.)
2. The system checks the **Model Selection Mode** (Auto or Manual):
   - **Auto Mode:** Analyzes the prompt for keywords using `_auto_route()`.
   - **Manual Mode:** Uses the user's fixed model choice from settings.
3. The selected AI model is used for the request.
4. The request is sent to **OpenRouter** via the OpenAI-compatible API.
5. The response is displayed to the user and optionally persisted to **Firestore**

---

## 5. Setup & Installation

### Prerequisites

- Python 3.10+
- A Firebase project with Auth, Firestore, and Storage enabled
- An OpenRouter API key

### Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd EduAI

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Additional optional dependencies
pip install streamlit-agraph streamlit-cropper plotly pandas

# 6. Place your Firebase service account key as:
#    firebase_credentials.json

# 7. Configure secrets (see Configuration section)

# 8. Run the app
streamlit run app.py
```

---

## 6. Configuration

### `.streamlit/secrets.toml`

This file stores all sensitive API keys and configuration. Required keys:

```toml
OPENROUTER_API_KEY = "sk-or-..."

# Optional: Firebase Storage bucket
FIREBASE_STORAGE_BUCKET = "your-project.appspot.com"

# Optional: Google OAuth
[google_oauth]
client_id = "..."
client_secret = "..."
redirect_uri = "http://localhost:8501"
scope = "openid email profile"

# Optional: SMTP for verification emails
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your-email@gmail.com"
password = "app-password"
use_tls = true
```

### `firebase_credentials.json`

Standard Firebase Admin SDK service account key (JSON format). Required fields: `project_id`, `private_key`, `client_email`, etc.

---

## 7. Authentication & User Management

EduAI supports three authentication methods:

### 7.1 Email/Password Login

- Uses Firebase Auth for user creation (`auth.create_user`) and retrieval (`auth.get_user_by_email`)
- Passwords are handled by Firebase (never stored locally)
- Email verification links are generated via `auth.generate_email_verification_link()`
- Optional SMTP integration sends verification emails directly

### 7.2 Google OAuth 2.0

- Full OAuth 2.0 authorization code flow
- Builds the Google consent URL via `build_google_oauth_url()`
- Exchanges auth code for tokens via `exchange_code_for_tokens()`
- Verifies ID tokens with `google.oauth2.id_token`
- Auto-creates Firebase user if first login

### 7.3 Guest Mode

- Allows exploration without an account
- Creates a temporary "Navigator" learning path with a welcome message
- Data is not persisted to Firebase

### User Profile

Each user has a Firestore profile (`users/{uid}`) containing:

| Field | Description |
|-------|------------|
| `email` | User's email address |
| `nickname` | Display name (2-20 alphanumeric characters) |
| `full_name` | Optional full name |
| `bio` | Optional biography |
| `contact` | Optional contact info |
| `avatar_path` | URL to uploaded avatar (stored in Firebase Storage) |
| `tutor_persona` | Selected AI personality (5 options) |
| `model_selection_mode` | AI routing behavior (`Auto` or `Manual`) |
| `manual_model_choice` | Fixed model ID used in Manual mode |
| `timezone` | User timezone |
| `preferred_language` | Preferred UI language |

### Tutor Personas

Users can select from 5 AI personality modes:

1. **Friendly Encourager** — Warm, supportive tone
2. **Strict Professor** — Rigorous, academic approach
3. **Socratic Questioner** — Asks probing questions
4. **Concise Technician** — Direct, no-nonsense answers
5. **Creative Storyteller** — Uses narratives and analogies

---

## 8. Multi-Model AI System

EduAI uses **OpenRouter** as a unified gateway to 6 specialized AI models:

| Model Key | Model ID | Specialization |
|-----------|---------|----------------|
| `deepseek` | `deepseek/deepseek-r1-0528:free` | General tutoring & Reasoning (default) |
| `arcee` | `arcee-ai/trinity-large-preview:free` | Programming, tech & coding |
| `nous` | `nousresearch/hermes-3-llama-3.1-405b:free` | Roleplay & agentic scenarios |
| `blackforest` | `black-forest-labs/flux.2-klein-4b` | Image generation |
| `nemotron` | `nvidia/nemotron-nano-12b-v2-vl:free` | Textbooks, diagrams, charts & video lectures |
| `qwen_vl` | `qwen/qwen3-vl-30b-a3b-thinking` | Math/science tutoring & visual comprehension |

### Auto-Routing (`_auto_route()`)

The system automatically selects the best model by scanning the user's prompt for keywords:

- **Code keywords** (`python`, `javascript`, `debug`, `algorithm`, etc.) → `arcee`
- **Visual/document keywords** (`diagram`, `chart`, `textbook`, `image`, `video`, `lecture`, etc.) → `nemotron`
- **Science/visual keywords** (`physics`, `chemistry`, `biology`, `formula`, `interactive`, etc.) → `qwen_vl`
- **Reasoning keywords** (`solve`, `calculate`, `math`, `proof`, etc.) → `deepseek`
- **Roleplay keywords** (`act as`, `simulate`, `feynman`, etc.) → `nous`
- **No match** → `deepseek` (general fallback)

### Selection Mode (Settings)

Users can toggle between two selection behaviors in the **Settings** tab:

1. **Auto Mode (Default):** Uses the `_auto_route()` logic above.
2. **Manual Mode:** Use a fixed model for all general queries. The user selects a specific model (e.g., `arcee` or `nous`) that will be used instead of auto-routing.

*Note: Special features like Vision or Feynman Board always use their specialized models regardless of this global setting.*

### API Architecture

```python
# Unified call function
_call_openrouter(messages, model_hint=None, is_json=False, temperature=0.7)
```

- All models are accessed via OpenAI-compatible chat completions API
- JSON mode supported via `response_format: {"type": "json_object"}`
- Cached client initialization with `@st.cache_resource`

---

## 9. Core Features

### 9.1 Home Chat

The primary interaction surface — a conversational AI tutor with rich controls.

**Key capabilities:**
- Free-form Q&A with emotional intelligence adaptation
- **Response Style Selector:** Default, Simple Explanation, Code Example, Real-world Analogy
- **Multilingual Controls:** Choose from 15 languages; AI responds in the selected language
- **Quick Style Buttons:** One-click switching between Simple, Code, and Analogy modes
- **Context-Aware Greeting:** Time-based greeting with session statistics and study tips
- **Gamification Bar:** Visual XP progress, level indicator
- **Streak Tracker:** Daily study streak with 28-day heatmap
- Integrated Voice Input, Accessibility Controls, and Pomodoro Timer

### 9.2 Learning Paths

Structured learning journeys with topic progression and persistent chat history.

**Path creation methods:**
1. **Manual Path** — User types a custom path name
2. **AI-Generated Path** — User provides a learning goal; AI generates 5-7 sequential topics
3. **Guided Onboarding** — Interactive AI interview determines interests and creates a personalized path

**Path data structure (per path in Firestore):**
```json
{
  "chat_history": [
    {"role": "user", "content": "...", "timestamp": 1234567890},
    {"role": "assistant", "content": "...", "timestamp": 1234567891}
  ],
  "current_topic": "Variables and Data Types",
  "topics": ["Introduction", "Variables and Data Types", "Control Flow", ...]
}
```

**Standard View** features:
- Chat-based tutoring scoped to the active path/topic
- Topic navigation with previous/next controls
- In-path quiz generation
- Doubt-clearing mode
- Certification recommendations
- Feedback system (thumbs up/down)

**Project View** — alternative mode for project-based paths with structured AI guidance.

### 9.3 Live Vision Solver

Camera-based problem solving using AI vision capabilities.

- Uses the browser camera via `st.camera_input()`
- Images are encoded as base64 and sent to the AI (DeepSeek model)
- Supports math problems, diagrams, code snippets, and written questions
- Returns step-by-step solutions with explanations

### 9.4 Feynman Board

Implementation of the Feynman Learning Technique — the user teaches a concept to the AI.

- The AI acts as a **curious, slightly confused student** (using the NousHermes model)
- Asks probing clarifying questions to test depth of understanding
- Maintains conversation history in Gemini-compatible format
- Helps identify gaps in comprehension through Socratic questioning

### 9.5 Social Impact & Accessibility

Five specialized sub-modes designed for rural inclusion and ethical AI:

#### Rural Analogy Engine
Translates complex technical concepts (e.g., Blockchain, Cloud Computing) into analogies based on Indian village life, agriculture, farming, and local markets.

#### Bias-Free Unity Chat
A multi-layered bias elimination system for sensitive topics:
- **Sensitivity Classification:** Automatically classifies queries as LOW/MEDIUM/HIGH
- **7-Rule Neutrality Framework:** Ensures equal respect for all communities
- **Structured Response:** Context → Key Facts → Multiple Perspectives → Unity Note
- **Transparency Panel:** Shows how the answer was generated (no word censorship)

#### Community Problem Solver
Takes real-world local issues (e.g., water shortage, crop pests) and generates 3 practical, low-cost, DIY solutions using locally available resources.

#### Low-Bandwidth / SMS Simulator
Generates ultra-compressed 160-character educational responses — demonstrates accessibility for feature phones without smartphones or internet.

Visual simulation of a Nokia 1100 phone screen with the SMS message.

#### Multi-Channel Lesson Pack
Generates the same lesson in 5 parallel formats for maximum reach:

| Channel | Format | Constraints |
|---------|--------|-------------|
| **Smartphone** | Rich text with key points, examples, mini-quiz | Full markdown |
| **SMS** | 4-6 messages | ≤ 160 characters each |
| **Voice/IVR** | 6-10 voice prompts | ≤ 90 characters each |
| **Printable** | One-pager with bullets, do/don't lists | Plain text |
| **Trust Card** | Certainty level, assumptions, verification keywords | Transparency metadata |

Includes JSON and TXT download options.

### 9.6 Career Path Finder

AI-powered career counseling with personalized path generation.

**Input form:**
- Interests, current skills, education level
- Location type (rural village → metro city)
- Aspirations, learning budget

**Output:**
- 3 personalized career paths with: title, description, skills gap, recommended courses, starter project, estimated time to job-readiness, entry-level salary range
- **Skills Gap Visualization:** Interactive Plotly bar chart (green/yellow/red) showing proficiency vs. requirements

### 9.7 Textbook Summarizer

Converts textbook content into structured study materials.

**Input:** Paste text or upload `.txt`/`.md` files (truncated to 12,000 characters)

**Output formats:**
- Bullet-point summary (15 max bullets)
- Flashcards (Q&A pairs)
- Exam answer notes (6-10 mark format)
- Mind map outline (hierarchical indentation)
- All formats combined

All outputs are downloadable as markdown files.

### 9.8 Collaborative Problem Solver

Structured 5-stage brainstorming process for real-world community problems:

1. **Define** — Articulate the problem clearly
2. **Research** — Gather context and background
3. **Ideate** — Generate creative solutions
4. **Prototype** — Design a prototype plan
5. **Plan** — Create an actionable implementation plan

Each stage involves AI-guided conversation with stage-specific prompts.

### 9.9 Peer Learning Groups

AI-simulated peer learning environment (demo mode):
- Generates AI personas representing diverse student perspectives
- Simulates group discussion dynamics
- Designed for future expansion to real multi-user collaboration

### 9.10 Spaced Repetition System (SRS)

Algorithm-based review scheduling for long-term retention.

- **Review Queue:** Firestore collection `review_queue` with due dates
- **Quality Rating:** User rates recall quality after each review
- **SM-2 Algorithm:** Adjusts review intervals based on performance
- **Dashboard:** Shows count of items due for review
- **Fallback Query:** Handles missing Firestore indexes gracefully with client-side filtering

### 9.11 Knowledge Graph

Interactive visualization of the user's learning network.

- **Primary renderer:** `streamlit-agraph` — interactive force-directed graph
- **Fallback renderer:** Plotly-based circular layout when agraph is unavailable
- Central "My Brain" node connected to learning path nodes, which connect to topic sub-nodes
- Node selection navigates to the corresponding learning path

### 9.12 Dashboard & Analytics

Comprehensive analytics view with multiple components:

- **Stats Header:** Level, XP, Badge count, Path count (4-column metric display)
- **Badge Gallery:** Styled badge chips with interactive filtering
- **Activity Pie Chart:** Message distribution across learning paths (Plotly donut chart)
- **Daily Activity Bar Chart:** Activity volume over time
- **Progress Report Generator:** AI-generated downloadable report with sections for executive summary, strengths, areas for growth, engagement analysis, and recommendations
- **SRS Dashboard:** Items due for review
- **Quick Start Navigator:** Quick topic exploration

---

## 10. Gamification System

### XP (Experience Points)

```
XP = (total_messages × 5) + (total_paths × 50) + (badge_count × 25)
```

### Level Thresholds

| Level | XP Required |
|-------|-------------|
| 1 | 0 |
| 2 | 50 |
| 3 | 150 |
| 4 | 300 |
| 5 | 500 |
| 6 | 800 |
| 7 | 1,200 |
| 8 | 1,800 |
| 9 | 2,500 |
| 10 | 3,500 |

### Badges

| Badge | Criteria |
|-------|---------|
| Explorer | ≥ 1 learning path |
| First Steps | ≥ 5 messages |
| Active Learner | ≥ 20 messages |
| Knowledge Seeker | ≥ 50 messages |
| Dedicated Scholar | ≥ 100 messages |
| Multi-Path Explorer | ≥ 3 paths |
| Pathfinder | ≥ 5 paths |
| Quiz Taker | ≥ 1 quiz attempt |
| Quizzer | ≥ 3 quiz attempts |
| Quiz Champion | ≥ 10 quiz attempts |
| Feynman Teacher | Used Feynman Board |
| Visual Learner | Used Vision Solver |
| Social Impact Hero | Used Social Impact tab |
| Career Explorer | Used Career Path |
| Speed Reader | Used Summarizer |
| Community Builder | Used Collaborative Solver |

---

## 11. Adaptive & Intelligent Features

### Emotional Intelligence (`detect_emotion_and_adapt()`)

Real-time keyword-based detection of user emotional state:

| Emotion | Trigger Keywords | AI Adaptation |
|---------|-----------------|---------------|
| **Frustration** | "confused", "stuck", "can't", "don't understand" | Patient, empathetic tone; break into smaller steps |
| **Anxiety** | "exam", "test tomorrow", "scared", "deadline" | Calm reassurance; focus on key points only |
| **Success** | "got it", "makes sense", "thanks" | Acknowledge progress; offer harder challenge |
| **Boredom** | "boring", "too easy", "skip" | Increase difficulty; real-world challenges |

### Context-Aware Greeting (`render_context_aware_greeting()`)

Adapts greeting and study tips based on time of day:

| Time Range | Greeting | Study Tip |
|-----------|---------|-----------|
| 00:00–05:00 | "Burning the midnight oil" | Audio-based lessons recommended |
| 05:00–12:00 | "Good morning" | Complex problem-solving |
| 12:00–17:00 | "Good afternoon" | Quick quiz to stay sharp |
| 17:00–21:00 | "Good evening" | Review and revision |
| 21:00–24:00 | "Late night session" | Short sessions, micro-lessons |

### Adaptive Preferences (`get_adaptive_preferences()`)

Learns preferred teaching style and persona from user feedback (thumbs up/down) stored in Firestore, then auto-applies the most positively-rated style.

### Onboarding Flow

New users experience a guided onboarding:
1. **Welcome dialog** — Choose between AI Guidance or Self Exploration
2. **AI Guidance mode** — Interactive chat interview to determine interests, skill level, and goals
3. **Path Generation** — AI creates a personalized learning path based on the conversation
4. **Accept or Refine** — User can accept the path or request modifications

---

## 12. Accessibility & Inclusivity

### Multilingual Support (15 Languages)

English, Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Urdu, Odia, Punjabi, French, Spanish, Arabic

- **Language Selector:** Dropdown in the Home tab
- **AI Prompt Injection:** Prefixes prompts with language-specific instructions
- **Translate Button:** Re-generates any AI response in the selected language

### Font Size Control

4 levels: Small (13px), Normal (15px), Large (18px), Extra Large (22px)

### High Contrast Mode

Toggles black background with white text and borders for improved readability.

### Text-to-Speech

Browser-based TTS using the Web Speech API:
- Supports locale-specific voices (e.g., `en-IN`, `hi-IN`, `ta-IN`)
- Adjustable rate (default 0.9×)
- Paste any text and click "Read Aloud"

### Voice Input

Browser-based speech recognition using the Web Speech API:
- Default language: `en-IN`
- Recognized text is copied to clipboard for easy pasting
- Visual feedback with button color change during listening

### Pomodoro Timer

Browser-based focus timer:
- Configurable work (5–60 min) and break (1–30 min) intervals
- Visual progress bar
- Audio notification (Web Audio API beep) on phase transitions
- Pause/Resume toggle

---

## 13. UI/UX Design

### Design System

- **Font:** Inter (Google Fonts) — 300-700 weights
- **Color Palette:** Dark theme inspired by GitHub/VS Code
  - Background: `#0d1117`
  - Text: `#c9d1d9`
  - Primary action: `#238636` (green buttons)
  - Accent: `#58a6ff` (blue highlights)
  - Secondary: `#30363d` (borders/dividers)
  - Sidebar: `#010409`
- **UI Components:** Glass-card morphism (`rgba(22,27,34,0.8)`)
- **Loading Screen:** Animated SVG brain with liquid-fill animation and "Booting Cognitive Core..." text

### Responsive Design

- Glass cards reduce padding on screens < 992px
- Buttons go full-width on mobile
- Sidebar hides on screens < 600px

### Sidebar Layout (3 Tabs)

1. **👤 Profile** — User header, profile manager, badges, verification status
2. **🧠 Paths** — Learning path list, manual/AI path creation
3. **🛠️ Tools** — Quick actions (Home, Learn, Quiz, Resources, Review), recent activity feed

---

## 14. Database Schema

### Firestore Collections

#### `users/{uid}`
User profile and preferences.

#### `learning_paths/{uid}`
Document containing all learning paths as top-level fields. Each field is a path name with value:
```json
{
  "chat_history": [...],
  "current_topic": "string",
  "topics": ["string", ...],
  "tags": ["string", ...],
  "path_type": "standard" | "project"
}
```

#### `quiz_attempts/{auto_id}`
Individual quiz attempt records:
```json
{
  "user_id": "uid",
  "path_name": "string",
  "topic": "string",
  "score": 3,
  "total": 5,
  "timestamp": "SERVER_TIMESTAMP"
}
```

#### `user_feedback/{auto_id}`
Feedback on AI responses:
```json
{
  "user_id": "uid",
  "path_name": "string",
  "topic": "string",
  "feedback": "good" | "bad",
  "response": "string",
  "style": "string",
  "persona": "string",
  "timestamp": "SERVER_TIMESTAMP"
}
```

#### `review_queue/{auto_id}`
Spaced repetition review items:
```json
{
  "user_id": "uid",
  "topic": "string",
  "due_date": "timestamp",
  "interval": 1,
  "ease_factor": 2.5,
  "repetitions": 0
}
```

---

## 15. API Reference — Key Functions

### AI Functions

| Function | Description |
|----------|------------|
| `_pick_model(hint)` | Selects AI model from the 5 available based on task hint |
| `_call_openrouter(messages, model_hint, is_json, temperature)` | Unified OpenRouter chat completion call |
| `_auto_route(prompt)` | Keyword-based auto-detection of best model for a prompt |
| `generate_ai_response(prompt, is_json, model_hint)` | High-level wrapper with spinner UI |
| `generate_guidance_response(prompt_text, stream, is_json)` | AI call specifically for onboarding guidance chat |

### Auth Functions

| Function | Description |
|----------|------------|
| `login_user(email, password)` | Firebase Auth login with session state update |
| `signup_user(email, password, nickname)` | Create user with optional verification email |
| `build_google_oauth_url()` | Generate Google OAuth consent URL |
| `exchange_code_for_tokens(code)` | Exchange OAuth auth code for tokens |
| `verify_id_token_and_get_userinfo(id_token_str)` | Verify Google ID token and extract claims |

### Data Functions

| Function | Description |
|----------|------------|
| `get_user_paths(uid)` | Fetch all learning paths from Firestore |
| `save_learning_path(uid, path_name, path_data)` | Persist a learning path with merge |
| `save_feedback(uid, path_name, topic, feedback, response)` | Store user feedback on AI responses |
| `load_session_data(uid)` | Load/initialize full session from Firestore |
| `compute_badges(uid, paths)` | Calculate earned badges and XP |
| `save_avatar_file(uid, uploaded_file)` | Process and save avatar image |
| `fetch_review_items_with_fallback(uid, only_due, limit)` | SRS review queue with index fallback |

### Rendering Functions

| Function | Description |
|----------|------------|
| `render_dashboard(paths, search_query, uid)` | Full analytics dashboard with charts |
| `render_knowledge_graph(paths)` | Interactive knowledge visualization |
| `render_standard_view(uid, path_name, path_data)` | Chat/quiz view for a learning path |
| `render_project_view(uid, path_name, path_data)` | Project-based learning view |
| `render_srs_view(uid)` | Spaced repetition review session |
| `render_vision_tab()` | Camera-based vision solver |
| `render_feynman_tab()` | Feynman technique teaching board |
| `render_social_impact_tab()` | 5-mode social impact suite |
| `render_career_path_tab()` | Career path finder with skills analysis |
| `render_summarizer_tab()` | Textbook summarizer |
| `render_collaborative_problem_tab()` | 5-stage brainstorming solver |
| `render_peer_learning_tab()` | Simulated peer learning groups |
| `render_context_aware_greeting()` | Time-based greeting component |
| `render_streak_tracker()` | Study streak with heatmap |
| `render_accessibility_controls()` | Font, contrast, TTS settings |
| `render_progress_report(paths, uid)` | AI-generated downloadable report |
| `render_pomodoro_timer()` | Browser-based focus timer |
| `render_voice_input_component()` | Web Speech API voice input |
| `render_multilingual_controls()` | Language selector dropdown |

### Utility Functions

| Function | Description |
|----------|------------|
| `safe_rerun()` | Version-compatible Streamlit rerun |
| `maybe_dialog(title)` | Cross-version dialog/modal context manager |
| `parse_quiz_data(quiz_text)` | Parse JSON quiz from AI response |
| `parse_topic_list(topic_list_text)` | Parse JSON topic list from AI response |
| `parse_multi_quiz(quiz_text)` | Parse multi-question quiz arrays |
| `detect_emotion_and_adapt(user_text)` | Emotional state detection from text |
| `sanitize_session_messages()` | Remove injected CSS/HTML from stored messages |
| `validate_nickname(nick)` | Validate nickname format (2-20 chars) |
| `send_email(smtp_cfg, to_email, subject, body)` | SMTP email sender |

---

## 16. Deployment & Running

### Local Development

```bash
streamlit run app.py
```

Default URL: `http://localhost:8501`

### Environment Requirements

- Python 3.10+
- `firebase_credentials.json` in the project root
- `.streamlit/secrets.toml` with at least `OPENROUTER_API_KEY`

### Production Considerations

- Set `FIREBASE_STORAGE_BUCKET` for avatar uploads
- Configure Google OAuth `redirect_uri` to match your deployment URL
- Consider using Streamlit Cloud, Railway, or Render for hosting
- Firebase security rules should restrict access to authenticated users

---

## 17. Utility Scripts

### `check_models.py`

A standalone diagnostic script for verifying Google Gemini model availability (used during the project's earlier Google AI era).

**Usage:**
```bash
python check_models.py
```

**What it does:**
1. Prompts for a Google API key
2. Lists all available generative models
3. Filters models supporting `generateContent`
4. Provides guidance on which model name to use

> **Note:** This script references the Google Generative AI SDK, which the main app no longer uses (migrated to OpenRouter). It remains as a historical debugging tool.

---

## 18. Security Considerations

| Area | Implementation |
|------|---------------|
| **Secrets** | All API keys stored in `.streamlit/secrets.toml` (gitignored) |
| **Firebase credentials** | Service account JSON kept in project root (should be gitignored) |
| **Password handling** | Delegated entirely to Firebase Auth (never stored/processed locally) |
| **XSS Prevention** | `html.escape()` used on user content before HTML rendering |
| **CSS Injection** | `sanitize_session_messages()` detects and removes injected CSS/HTML |
| **Input Validation** | Nickname validation via regex; text truncation for AI prompts |
| **OAuth Security** | State parameter used in Google OAuth flow |
| **Data Isolation** | All Firestore queries scoped to `user_id` field |

### Recommendations

1. Add `firebase_credentials.json` and `.streamlit/secrets.toml` to `.gitignore`
2. Implement Firebase security rules to enforce per-user data access
3. Add rate limiting for AI API calls
4. Consider implementing CSRF protection for the OAuth callback
5. Regularly rotate the OpenRouter API key

---

*This documentation was generated on February 14, 2026, by analyzing the complete EduAI project source code (v10.0).*
