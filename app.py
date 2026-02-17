# ─────────────────────────────────────────────────────────────────────────────
#  EduAI — Adaptive Gemini-Powered Tutoring Platform
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from gemini_rotator import GeminiRotator
import base64
import io
import os
import re
import html
import textwrap
import hashlib
import time
import json
import math
import requests
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlencode
from contextlib import contextmanager

import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

# Optional dependencies — gracefully degrade if missing
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    AGRAPH_SUPPORT = True
except Exception:
    AGRAPH_SUPPORT = False

try:
    from streamlit_ace import st_ace
    ACE_SUPPORT = True
except Exception:
    ACE_SUPPORT = False

try:
    from streamlit_cropper import st_cropper
    CROP_SUPPORT = True
except Exception:
    CROP_SUPPORT = False

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_auth_requests
except Exception:
    id_token = None
    google_auth_requests = None

def st_copy_to_clipboard(text: str, key: str = None):
    """Render a clipboard copy button via a small injected HTML snippet."""
    try:
        import uuid
        button_id = f"copy-btn-{uuid.uuid4().hex[:8]}"
        safe_text = str(text).replace("'", "\\'").replace('\n', '\\n')
        html_code = f"""
                <div style="display:flex; align-items:center;">
                    <button id="{button_id}" onclick="navigator.clipboard.writeText('{safe_text}').then(function(){{var btn=document.getElementById('{button_id}'); btn.innerText='Copied!'; setTimeout(function(){{btn.innerText='Copy';}},2000);}}, function(){{var btn=document.getElementById('{button_id}'); btn.innerText='Failed!';}})" style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; padding:4px 8px; font-size:12px; cursor:pointer;">
                        Copy
                    </button>
                </div>
        """
        components.html(html_code, height=40)
    except Exception:
        return

# ── Styling ─────────────────────────────────────────────────────────────────

def load_css():
    """Inject the global dark-theme CSS (Inter font, GitHub-style palette)."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
                font-weight: 600 !important;
                letter-spacing: -0.02em !important;
            }

            /* --- LOADING SCREEN (Refined) --- */
            .loading-container { display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; width:100vw; position:fixed; top:0; left:0; background:#0a0118; z-index:9999; font-family: 'Inter', sans-serif; transition: opacity .6s ease-out; opacity:1 }
            .cyber-brain-container { width:120px; height:120px; position:relative; filter: drop-shadow(0 0 20px rgba(100,100,255,0.3)); animation: brain-pulse 8s ease-in-out infinite }
            @keyframes brain-pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.02)} }
            .cyber-brain-svg{width:100%;height:100%}.brain-outline{fill:rgba(20,20,50,0.7);stroke:rgba(120,120,255,0.4);stroke-width:1}.brain-veins{fill:none;stroke:#7efcff;stroke-width:1.2;stroke-dasharray:1000;stroke-dashoffset:1000;animation:liquid-fill 6s ease-out forwards;opacity:0.6} @keyframes liquid-fill{to{stroke-dashoffset:0}}
            .loading-text { margin-top: 20px; font-size: 14px; color: #888; letter-spacing: 1px; text-transform: uppercase; }

            /* --- PROFESSIONAL DARK THEME --- */
            [data-testid="stAppViewContainer"]{background:#0d1117; color:#c9d1d9;}
            [data-testid="stHeader"]{background:transparent;}

            /* Glass card - refined */
            .glass-card{background: rgba(22, 27, 34, 0.8); border:1px solid rgba(48, 54, 61, 0.8); border-radius:8px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,0.2);}

            /* Sidebar */
            [data-testid="stSidebar"]{background:#010409; border-right:1px solid #30363d;}

            /* Buttons - Professional Action Style */
            .stButton>button{
                background: #238636; 
                color: #ffffff; 
                border: 1px solid rgba(240,246,252,0.1); 
                border-radius: 6px; 
                padding: 6px 16px; 
                font-weight: 500; 
                font-size: 14px;
                box-shadow: 0 1px 0 rgba(27,31,36,0.1);
                transition: all 0.2s cubic-bezier(0.3, 0, 0.5, 1);
            }
            .stButton>button:hover{
                background: #2ea043;
                border-color: #8b949e;
                transform: none;
                box-shadow: none;
            }
            .stButton>button:active{
                background: #238636;
            }
            
            /* Secondary/Ghost Buttons */
            .stButton>button[kind="secondary"] {
                background: #161b22;
                border: 1px solid #30363d;
                color: #c9d1d9;
            }

            /* Inputs - clean & flat */
            .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
                background: #0d1117; 
                border: 1px solid #30363d; 
                color: #c9d1d9; 
                border-radius: 6px; 
                padding: 8px 12px;
                font-size: 14px;
            }
            .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
                border-color: #58a6ff;
                box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
            }

            /* Chat bubbles - Copilot style */
            div[data-testid="stChatMessage"] {
                background: transparent;
                border: none;
                padding: 12px 0;
            }
            div[data-testid="stChatMessage"][data-testid="user"] {
                background: transparent;
            }

            /* Quick home link */
            .quick-home-wrapper{position:fixed; top:14px; right:20px; z-index:9999}
            .quick-home-link{
                display:inline-block; 
                background:#1f6feb; 
                color:#fff; 
                padding:6px 12px; 
                border-radius:6px; 
                font-size:13px; 
                font-weight:500; 
                text-decoration:none;
            }
            .quick-home-link:hover{background:#388bfd;}

            /* Responsive tweaks */
            @media (max-width:992px){ .glass-card{padding:16px} .stButton>button{width:100%} }
            @media (max-width:600px){ [data-testid="stSidebar"]{display:none} }
        </style>
    """, unsafe_allow_html=True)


# ── Firebase & API Initialization ──────────────────────────────────────────────────

@st.cache_resource
def initialize_firebase():
    """Connect to Firestore and return a database client."""
    try:
        if not os.path.exists("firebase_credentials.json"):
            st.error("🔥 Firebase credentials file not found!", icon="🚨")
            return None
        bucket = st.secrets.get("FIREBASE_STORAGE_BUCKET") if "FIREBASE_STORAGE_BUCKET" in st.secrets else None
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_credentials.json")
            app_options = {'storageBucket': bucket} if bucket else {}
            firebase_admin.initialize_app(cred, app_options)
        return firestore.client()
    except Exception as e:
        st.error(f"🔥 Firebase initialization failed: {e}", icon="🚨")
        return None

db = initialize_firebase()

# ── Gemini AI Configuration ─────────────────────────────────────────────────────

GEMINI_MODEL = "gemini-2.5-flash"  # Primary model

@st.cache_resource
def get_gemini_client():
    """Initialize and return a GeminiRotator instance."""
    try:
        rotator = GeminiRotator()
        return rotator
    except Exception as e:
        st.error(f"🔑 Gemini API configuration failed: {e}", icon="🚨")
        return None

client = get_gemini_client()

def _call_gemini(prompt: str, is_json: bool = False) -> str | None:
    """Send a prompt to Gemini and return the response text, or None on failure."""
    if not client:
        return None
    if is_json:
        prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No extra text, no markdown formatting."
    try:
        resp = client.generate_content(GEMINI_MODEL, prompt)
        if resp and resp.get('choices'):
            return resp['choices'][0]['message']['content']
        return None
    except Exception as e:
        st.error(f"AI error (Gemini): {e}", icon="🚨")
        return None

# ── Session State ─────────────────────────────────────────────────────────────

def init_session_state():
    if 'session' not in st.session_state:
        st.session_state['session'] = {
            'logged_in': False, 'user_info': None, 'page': 'Login',
            'learning_paths': {}, 'active_path': None,
            'loading_complete': False, 'current_quiz_data': None,
            'guest_mode': False, 'review_session_active': False,
            'badge_filter': None, 'quick_action': None,
        }

def safe_rerun():
    """Trigger a Streamlit script rerun."""
    st.rerun()


# Small compatibility helper: provide a context-manager-compatible dialog fallback.

@contextmanager
def maybe_dialog(title: str):
    """Context manager that uses st.dialog when available, otherwise a plain container."""
    # Try st.dialog first (some Streamlit builds expose a context-manager object)
    try:
        dlg = getattr(st, 'dialog', None)
        if dlg:
            try:
                cm = dlg(title)
                if hasattr(cm, '__enter__'):
                    with cm:
                        yield
                    return
            except Exception:
                # fall through to other options
                pass
    except Exception:
        pass

    # Try st.modal if available
    try:
        modal = getattr(st, 'modal', None)
        if modal:
            try:
                cm = modal(title)
                if hasattr(cm, '__enter__'):
                    with cm:
                        yield
                    return
            except Exception:
                pass
    except Exception:
        pass

    # Final fallback: a normal container (always works)
    with st.container():
        yield

# ── Authentication & Profile Helpers ───────────────────────────────────────────

def login_user(email, password):
    """Authenticate via Firebase Admin and populate session state."""
    try:
        user = auth.get_user_by_email(email)
        profile = {}
        if db:
            doc = db.collection('users').document(user.uid).get()
            if doc.exists:
                profile = doc.to_dict() or {}
        user_info = {
            'uid': user.uid, 'email': user.email,
            'nickname': profile.get('nickname') or user.display_name or '',
            'full_name': profile.get('full_name', ''), 'bio': profile.get('bio', ''),
            'contact': profile.get('contact', ''), 'avatar_path': profile.get('avatar_path', ''),
            'timezone': profile.get('timezone', ''), 'preferred_language': profile.get('preferred_language', ''),
            'tutor_persona': profile.get('tutor_persona', 'Friendly Encourager'),
            'email_verified': getattr(user, 'email_verified', False)
        }
        st.session_state.session.update({'logged_in': True, 'user_info': user_info})
        st.success("Login Successful!", icon="✅")
        safe_rerun()
    except Exception:
        st.error("Login Failed: Incorrect email or other error.", icon="🚨")

def signup_user(email, password, nickname=None):
    try:
        user_record = auth.create_user(email=email, password=password, display_name=nickname)
        if db:
            profile_ref = db.collection('users').document(user_record.uid)
            profile_ref.set({
                'email': email, 'nickname': nickname or '', 'full_name': '', 'bio': '',
                'contact': '', 'avatar_path': '', 'tutor_persona': 'Friendly Encourager'
            }, merge=True)
        try:
            link = auth.generate_email_verification_link(email)
            if link:
                sent = False
                if 'smtp' in st.secrets:
                    try:
                        body = f"Please verify your Edu AI account by clicking this link:\n\n{link}"
                        send_email(st.secrets['smtp'], email, "Verify your Edu AI account", body)
                        sent = True
                    except Exception: pass
                if sent:
                    st.success("Signup Successful! Verification email sent.", icon="✅")
                else:
                    st.success("Signup Successful! Please verify your email.", icon="✅")
                    st.markdown(f"Verification link: [{link}]({link})")
        except Exception:
            st.success("Signup Successful! Please login.", icon="✅")
    except Exception as e:
        st.error(f"Signup Failed: {e}", icon="🚨")

def validate_nickname(nick: str):
    if not nick: return True, ""
    if not re.match(r'^[A-Za-z0-9 _-]{2,20}$', nick):
        return False, "Nickname must be 2-20 characters and may include letters, numbers, spaces, - and _."
    return True, ""

def save_avatar_file(uid: str, uploaded_file) -> str:
    if not uploaded_file: return ''
    avatars_dir = Path("avatars")
    avatars_dir.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        img = Image.open(uploaded_file) if not hasattr(uploaded_file, 'convert') else uploaded_file
        img = img.convert('RGB')
        img.thumbnail((256, 256))
        filename = f"{uid}.jpg"
        file_path = avatars_dir / filename
        img.save(file_path, format='JPEG', quality=85, optimize=True)
        return upload_to_firebase_storage(str(file_path), uid) or str(file_path)
    except Exception:
        try:
            ext = Path(getattr(uploaded_file, 'name', '.png')).suffix
            filename = f"{uid}{ext}"
            file_path = avatars_dir / filename
            with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
            return upload_to_firebase_storage(str(file_path), uid) or str(file_path)
        except Exception: return ''

def upload_to_firebase_storage(local_path: str, uid: str) -> str:
    try:
        bucket = storage.bucket()
        blob = bucket.blob(f"avatars/{Path(local_path).name}")
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
    except Exception: return ''

def send_email(smtp_cfg: dict, to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg['Subject'], msg['From'], msg['To'] = subject, smtp_cfg.get('username'), to_email
    msg.set_content(body)
    server = smtplib.SMTP(smtp_cfg.get('host'), int(smtp_cfg.get('port', 587)))
    if smtp_cfg.get('use_tls', True): server.starttls()
    server.login(smtp_cfg.get('username'), smtp_cfg.get('password'))
    server.send_message(msg)
    server.quit()

def get_user_paths(uid):
    if not db: return {}
    doc = db.collection('learning_paths').document(uid).get()
    return doc.to_dict() if doc.exists else {}

def build_google_oauth_url():
    cfg = st.secrets.get('google_oauth')
    if not cfg: return None
    params = {
        'client_id': cfg.get('client_id'), 'redirect_uri': cfg.get('redirect_uri'),
        'response_type': 'code', 'scope': cfg.get('scope', 'openid email profile'),
        'access_type': 'offline', 'prompt': 'select_account', 'state': 'eduai_state'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def exchange_code_for_tokens(code: str) -> dict:
    cfg = st.secrets.get('google_oauth')
    if not cfg: return {}
    resp = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code, 'client_id': cfg.get('client_id'),
        'client_secret': cfg.get('client_secret'), 'redirect_uri': cfg.get('redirect_uri'),
        'grant_type': 'authorization_code'
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()

def verify_id_token_and_get_userinfo(id_token_str: str) -> dict:
    try:
        audience = st.secrets.get('google_oauth', {}).get('client_id')
        if id_token and google_auth_requests:
            return id_token.verify_oauth2_token(id_token_str, google_auth_requests.Request(), audience)
        else:
            return {}
    except Exception:
        return {}

def compute_badges(uid: str, paths: dict) -> list:
    badges = []
    total_msgs = sum(len(p.get('chat_history', [])) for p in paths.values())
    total_paths = len(paths)

    # Tier 1: Getting Started
    if total_paths >= 1:
        badges.append('Explorer')
    if total_msgs >= 5:
        badges.append('First Steps')

    # Tier 2: Active Learning
    if total_msgs >= 20:
        badges.append('Active Learner')
    if total_msgs >= 50:
        badges.append('Knowledge Seeker')
    if total_msgs >= 100:
        badges.append('Dedicated Scholar')
    if total_paths >= 3:
        badges.append('Multi-Path Explorer')
    if total_paths >= 5:
        badges.append('Pathfinder')

    # Tier 3: Quizzing
    if db:
        try:
            quiz_docs = list(db.collection('quiz_attempts').where(field_path='user_id', op_string='==', value=uid).stream())
            quiz_count = len(quiz_docs)
            if quiz_count >= 1:
                badges.append('Quiz Taker')
            if quiz_count >= 3:
                badges.append('Quizzer')
            if quiz_count >= 10:
                badges.append('Quiz Champion')
        except Exception:
            pass

    # Tier 4: Feature Usage (from session state)
    session = st.session_state.get('session', {})
    if session.get('used_feynman'):
        badges.append('Feynman Teacher')
    if session.get('used_vision'):
        badges.append('Visual Learner')
    if session.get('used_social_impact'):
        badges.append('Social Impact Hero')
    if session.get('used_career_path'):
        badges.append('Career Explorer')
    if session.get('used_summarizer'):
        badges.append('Speed Reader')
    if session.get('used_collab_solver'):
        badges.append('Community Builder')

    # Compute XP (experience points)
    xp = total_msgs * 5 + total_paths * 50
    xp += len(badges) * 25  # Bonus for badges
    st.session_state.session['xp'] = xp

    # Level calculation
    level = 1
    xp_thresholds = [0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500]
    for i, threshold in enumerate(xp_thresholds):
        if xp >= threshold:
            level = i + 1
    st.session_state.session['level'] = level

    return badges

def save_learning_path(uid, path_name, path_data):
    if not db: return
    db.collection('learning_paths').document(uid).set({path_name: path_data}, merge=True)
    st.toast(f"Progress saved for '{path_name}'!", icon="📈")

def save_feedback(uid, path_name, topic, feedback, response, style=None, persona=None):
    if not db: return
    data = {'user_id': uid, 'path_name': path_name, 'topic': topic, 'feedback': feedback,
              'response': response, 'timestamp': firestore.SERVER_TIMESTAMP}
    if style: data['style'] = style
    if persona: data['persona'] = persona
    db.collection('user_feedback').document().set(data)
    st.toast("Feedback submitted. Thank you!", icon="👍")

def generate_ai_response(prompt, is_json=False, model_hint=None):
    """Send a prompt to Gemini and return the response text."""
    if not client:
        return None
    with st.spinner("`🧠 Gemini is thinking...`"):
        return _call_gemini(prompt, is_json=is_json)

def parse_quiz_data(quiz_text):
    """Parse a JSON quiz response into a dict with 'question', 'options', 'answer' keys."""
    try:
        # Try direct parsing first (might be single object or list)
        quiz_json = json.loads(quiz_text)
        # Check if it's a single question object
        if isinstance(quiz_json, dict) and all(k in quiz_json for k in ["question", "options", "answer"]):
            return quiz_json # Return single dict for backward compatibility if needed
        # Check if it's a list of question objects
        elif isinstance(quiz_json, list) and all(isinstance(q, dict) and all(k in q for k in ["question", "options", "answer"]) for q in quiz_json):
             # For multi-quiz, wrap it for consistency with session state logic
             return {'questions': quiz_json} 
    except Exception:
        # If direct fails, try extracting from markdown code block
        try:
            # Look for JSON array or object within backticks
            match = re.search(r'```json\n(.*?)```', quiz_text, re.DOTALL) or re.search(r'({.*?}|\[.*?\])', quiz_text, re.DOTALL)
            if match:
                potential_json = match.group(1)
                quiz_json = json.loads(potential_json)
                # Repeat the checks from above
                if isinstance(quiz_json, dict) and all(k in quiz_json for k in ["question", "options", "answer"]):
                    return quiz_json
                elif isinstance(quiz_json, list) and all(isinstance(q, dict) and all(k in q for k in ["question", "options", "answer"]) for q in quiz_json):
                     return {'questions': quiz_json}
        except Exception:
            return None # Failed to parse in any known format
    return None # Return None if parsing fails or format is incorrect

def parse_topic_list(text: str):
    """Parse a model response into a list of topic strings."""
    if not text:
        return None
    # Try direct JSON
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list) and all(isinstance(i, str) for i in parsed):
            return [t.strip() for t in parsed if t.strip()]
    except Exception:
        pass
    # Try to extract JSON inside ```json ... ``` or ``` ... ```
    m = re.search(r'```(?:json\n)?(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            inner = m.group(1).strip()
            parsed = json.loads(inner)
            if isinstance(parsed, list) and all(isinstance(i, str) for i in parsed):
                return [t.strip() for t in parsed if t.strip()]
        except Exception:
            pass
    # Fallback: split by newlines or commas
    parts = re.split(r'[\n,]+', text)
    cleaned = [p.strip().strip("\"'") for p in parts if p.strip()]
    return cleaned if cleaned else None


# ── Guided Onboarding Chat ─────────────────────────────────────────────────────

def get_guidance_chat_history():
    if 'guidance_chat_history' not in st.session_state:
        st.session_state.guidance_chat_history = []
    return st.session_state.guidance_chat_history

def add_guidance_message(role, content):
    """Append a message to the guidance chat history."""
    get_guidance_chat_history().append({"role": role, "content": content})

def generate_guidance_response(prompt_text, stream=False, is_json=False):
    """Generate an AI response within the onboarding guidance conversation context."""
    # Build context from guidance chat history
    context_parts = []
    for msg in get_guidance_chat_history():
        role = msg["role"]
        if role == "model":
            role = "assistant"
        if role in ["user", "assistant"]:
            context_parts.append(f"{role}: {msg['content']}")
    
    full_prompt = "\n".join(context_parts) + f"\nuser: {prompt_text}"

    try:
        return _call_gemini(full_prompt, is_json=is_json)
    except Exception as e:
        st.error(f"AI Guidance error: {e}")
        return "Sorry, I encountered an error during guidance. Please try again."

def render_guidance_chat():
    """Render the multi-stage onboarding chat interface."""
    st.markdown("### Your AI Guide")
    st.markdown("Let's figure out the perfect learning path for you!")

    guidance_history = get_guidance_chat_history()

    # Display chat messages
    for message in guidance_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for user
    if st.session_state.get('awaiting_user_input', True): # Flag to prevent multiple inputs
        user_input = st.chat_input("Tell me more, or answer the question...")
        if user_input:
            add_guidance_message("user", user_input)
            st.session_state.awaiting_user_input = False # User has input, await AI
            st.rerun() # Rerun to process AI response
    else: # If awaiting AI response
        st.session_state.awaiting_user_input = True # Reset for next turn
        
        # Determine next AI action based on current stage
        current_stage = st.session_state.get('guidance_stage', 'start_questions')
        
        if current_stage == 'start_questions':
            # Initial questions
            if len(guidance_history) == 0 or guidance_history[-1]["role"] == "user":
                ai_prompt = (
                    "You are an expert learning path generator. Your goal is to deeply understand the user's aspirations, "
                    "current skills, interests, and preferred learning style to craft a highly personalized learning path. "
                    "Start by asking about their main learning goals or what they envision themselves doing in 3-5 years. "
                    "Also, ask about their current skill level in that area. Keep the conversation engaging and ask one main question at a time."
                )
                ai_response = generate_guidance_response(ai_prompt)
                add_guidance_message("model", ai_response)
                st.session_state.guidance_stage = 'collecting_info'
                st.rerun() # Rerun to show AI's question

        elif current_stage == 'collecting_info':
            # AI continues asking questions based on previous user input
            last_user_msg = guidance_history[-1]["content"] if guidance_history and guidance_history[-1]["role"] == "user" else ""
            
            ai_prompt = (
                f"The user just said: '{last_user_msg}'. "
                f"Based on our previous conversation and their goal to clarify their learning path, "
                f"ask a *relevant follow-up question* to gather more details about their interests, "
                f"experience, or preferred learning methods. "
                f"For example, you could ask about specific topics within their interest, "
                f"how they learn best (e.g., videos, reading, hands-on projects), "
                f"or if they have any existing knowledge/skills they want to leverage. "
                f"You can also ask a simple MCQ to gauge their preference. "
                f"Be conversational and encourage detail, aiming for a blueprint of their ideal future self. "
                f"If you feel you have enough information, respond with 'GUIDANCE_READY_TO_GENERATE' "
                f"followed by a JSON list of topics in the format: "
                f"```json\n[\"Topic 1\", \"Topic 2\", ...]\n``` "
                f"Otherwise, ask your next question."
            )
            ai_response = generate_guidance_response(ai_prompt, stream=False)
            if ai_response is None:
                ai_response = "I'm having trouble responding right now. Could you try again?"
            add_guidance_message("model", ai_response)

            if ai_response and "GUIDANCE_READY_TO_GENERATE" in ai_response:
                # Extract the path from the AI response
                topic_list_text = ai_response.split("GUIDANCE_READY_TO_GENERATE", 1)[1]
                generated_topics = parse_topic_list(topic_list_text)

                if generated_topics:
                    st.session_state.generated_guidance_topics = generated_topics
                    st.session_state.guidance_stage = 'confirm_path'
                    add_guidance_message("model", "Great! I've gathered enough information. Here's a proposed path based on our chat:")
                    for i, t in enumerate(generated_topics, 1):
                        add_guidance_message("model", f"{i}. {t}")
                    add_guidance_message("model", "Do these topics sound good? You can accept them, or ask to refine.")
                else:
                    add_guidance_message("model", "I had trouble generating the path. Let's try again. What else can you tell me?")
                    st.session_state.guidance_stage = 'collecting_info' # Stay in collecting info
            st.rerun()
            
        elif current_stage == 'confirm_path':
            # This stage is managed by buttons, so no chat_input needed here, but we check user_input for 'refine'
            last_user_msg = guidance_history[-1]["content"] if guidance_history and guidance_history[-1]["role"] == "user" else ""
            if "refine" in last_user_msg.lower():
                add_guidance_message("model", "Okay, how would you like to refine the path? Tell me what changes you'd like.")
                st.session_state.guidance_stage = 'collecting_info' # Go back to collecting info
                st.rerun()

def make_message(role: str, content: str, **kwargs) -> dict:
    message = {'role': role, 'content': content, 'timestamp': int(time.time())}
    if kwargs: message.update(kwargs)
    return message

def parse_multi_quiz(quiz_text):
    try: return json.loads(quiz_text)
    except Exception:
        try:
            match = re.search(r'```json\n(\[.*\])\n```', quiz_text, re.DOTALL) or re.search(r'(\[.*\])', quiz_text, re.DOTALL)
            if match: return json.loads(match.group(1))
        except Exception: return None
    return None

# ── Message Sanitization ──────────────────────────────────────────────────────

def _looks_like_css_block(text: str) -> bool:
    if not isinstance(text, str):
        return False
    low = text.lower()
    # Patterns that indicate the unwanted dialog CSS snippet or emotion hashed classes
    checks = ["st-emotion-cache", "dialog specific styles", "/* --- dialog", ".st-emotion-cache-", "<style", "<div", "<svg", "<path"]
    if any(c in low for c in checks):
        return True
    # Also treat any text that looks like raw HTML tags as suspicious
    try:
        if re.search(r'<\/?\w+[^>]*>', text):
            return True
    except Exception:
        pass
    return False


def sanitize_session_messages():
    """Remove any stored messages in session state that look like injected CSS or code blocks.
    This only updates in-memory session_state so it is safe and non-destructive to the DB.
    """
    try:
        ss = st.session_state.session
    except Exception:
        return

    # Home chat
    if isinstance(ss.get('home_chat'), list):
        ss['home_chat'] = [m for m in ss['home_chat'] if not _looks_like_css_block(m.get('content', ''))]

    # Guidance chat (stored in top-level session_state keys)
    if isinstance(st.session_state.get('guidance_chat_history'), list):
        st.session_state.guidance_chat_history = [m for m in st.session_state.guidance_chat_history if not _looks_like_css_block(m.get('content', ''))]

    # Learning paths: sanitize each path's chat_history
    lp = ss.get('learning_paths') or {}
    if isinstance(lp, dict):
        for pname, pdata in list(lp.items()):
            if isinstance(pdata, dict) and isinstance(pdata.get('chat_history'), list):
                cleaned = [m for m in pdata['chat_history'] if not _looks_like_css_block(m.get('content', ''))]
                ss['learning_paths'][pname]['chat_history'] = cleaned

    # Optionally clear any top-level debugging dumps that may contain code
    for key in list(ss.keys()):
        if key.startswith('debug_') or key.startswith('_raw_'):
            try:
                del ss[key]
            except Exception:
                pass

# ── Firestore Query Helpers ─────────────────────────────────────────────────────

def fetch_review_items_with_fallback(uid: str, only_due=True, limit=500):
    """
    Try to fetch review items using the indexed composite query first.
    If Firestore raises an index-required error, present the console index link
    to the user and fall back to querying only by `user_id` and client-side
    filtering on `due_date` (safer, slower).
    """
    if not db:
        return []
    try:
        if only_due:
            # Use keyword arguments to avoid positional-argument deprecation warnings from the Firestore client
            items = list(db.collection('review_queue').where(field_path='user_id', op_string='==', value=uid).where(field_path='due_date', op_string='<=', value=datetime.now()).stream())
        else:
            items = list(db.collection('review_queue').where(field_path='user_id', op_string='==', value=uid).stream())
        return items
    except Exception as e:
        msg = str(e)
        # Firestore returns a helpful URL to create the missing index — capture and show it
        idx_url = None
        m = re.search(r'(https?://console\.firebase\.google\.com[^\s]+)', msg)
        if m:
            idx_url = m.group(1)
        # Use an info call with inline link to avoid cluttering the UI
        if idx_url:
            st.info(f"Firestore requires a composite index for this query. You can create it here: {idx_url}")
        else:
            st.info("Firestore returned an index-required error. Falling back to a safe client-side filter. Creating the index will improve performance.")

        # Fallback: query only by user_id (single-field) and filter due_date client-side
        try:
            docs = list(db.collection('review_queue').where(field_path='user_id', op_string='==', value=uid).limit(limit).stream())
            filtered = []
            now = datetime.now()
            for d in docs:
                data = d.to_dict() or {}
                due = data.get('due_date')
                try:
                    if isinstance(due, datetime):
                        if not only_due or due <= now:
                            filtered.append(d)
                    elif isinstance(due, dict) and '_seconds' in due:
                        # sometimes Firestore serializes timestamps as map with _seconds
                        due_dt = datetime.fromtimestamp(due['_seconds'])
                        if not only_due or due_dt <= now:
                            filtered.append(d)
                    elif isinstance(due, str):
                        try:
                            due_dt = datetime.fromisoformat(due)
                            if not only_due or due_dt <= now:
                                filtered.append(d)
                        except Exception:
                            # ignore unparsable strings
                            pass
                except Exception:
                    # In case of unexpected shapes, ignore the item
                    continue
            return filtered
        except Exception as ex:
            st.error(f"Failed to apply fallback Firestore fetch: {ex}")
            return []

# ── Feature Tabs ──────────────────────────────────────────────────────────────

def render_dashboard(paths: dict, search_query: str = "", uid: str = ""):
    st.header("🎓 Your Learning Dashboard")
    st.markdown("---")
    if not paths:
        st.info("Your dashboard is waiting! Start a new learning path to see your progress.")
        return

    # Filter paths based on search
    if search_query:
        filtered_paths = {k: v for k, v in paths.items() if search_query.lower() in k.lower() or search_query.lower() in v.get('current_topic', '').lower()}
    else:
        filtered_paths = paths

    # Apply badge filter if present
    badge_filter = st.session_state.session.get('badge_filter')
    if badge_filter:
        # Prefer explicit tags on paths
        tag_key = badge_filter.lower().split()[0] if badge_filter else None
        tagged = {k: v for k, v in filtered_paths.items() if tag_key and tag_key in [t.lower() for t in v.get('tags', [])]}
        if tagged:
            filtered_paths = tagged
        else:
            # fallback heuristics for Quizzer
            if badge_filter == 'Quizzer':
                quiz_paths = set()
                for pname, pdata in filtered_paths.items():
                    if any(('quiz' in (m.get('content') or '').lower()) for m in pdata.get('chat_history', [])):
                        quiz_paths.add(pname)
                if db:
                    try:
                        attempts = list(db.collection('quiz_attempts').where(field_path='user_id', op_string='==', value=uid).stream())
                        for a in attempts:
                            d = a.to_dict() or {}
                            if d.get('path_name'): quiz_paths.add(d.get('path_name'))
                    except Exception:
                        pass
                filtered_paths = {k: v for k, v in filtered_paths.items() if k in quiz_paths}
            else:
                filtered_paths = dict(filtered_paths)

    all_messages = [{'path': name, 'role': msg.get('role'), 'timestamp': msg.get('timestamp', 0)}
                    for name, data in filtered_paths.items() for msg in data.get('chat_history', [])]
    if not all_messages:
        st.info("No activity yet. Interact with the AI to populate your dashboard.")
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Paths", len(filtered_paths))
    with col2:
        st.metric("Total Messages", len(all_messages))
    with col3:
        st.metric("Badges Earned", len(st.session_state.session.get('cached_badges') or compute_badges(uid, paths)))

    col1, col2 = st.columns(2)
    # Build a DataFrame from the collected messages and ensure we have a 'date' column for plotting
    try:
        df = pd.DataFrame(all_messages)
        if not df.empty:
            # Normalize/convert timestamp to int and create a date column (UTC seconds -> date)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce').fillna(0).astype(int)
                df['date'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce').dt.date
            else:
                df['date'] = pd.NaT
        else:
            df = pd.DataFrame(columns=['path', 'role', 'timestamp', 'date'])
    except Exception:
        df = pd.DataFrame(columns=['path', 'role', 'timestamp', 'date'])

    with col1:
        if df.empty or df['path'].dropna().empty:
            st.info("No path activity to display.")
        else:
            path_counts = df['path'].value_counts().reset_index()
            path_counts.columns = ['path', 'message_count']
            fig_pie = go.Figure(data=[go.Pie(labels=path_counts['path'], values=path_counts['message_count'], hole=.4,
                                             marker_colors=['#a275e3', '#c9a7ff', '#6a4fa8', '#8b6fcf'], textinfo='percent+label')])
            fig_pie.update_layout(title_text='Activity by Path', showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)', font_color='#e1e1ff')
            st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        if df.empty or df['date'].dropna().empty:
            st.info("No daily activity to display.")
        else:
            activity_by_day = df['date'].value_counts().sort_index().reset_index()
            activity_by_day.columns = ['date', 'count']
            fig_bar = go.Figure(data=[go.Bar(x=activity_by_day['date'], y=activity_by_day['count'], marker_color='#a275e3')])
            fig_bar.update_layout(title_text='Daily Learning Activity', xaxis_title='Date', yaxis_title='Interactions',
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e1e1ff',
                                  xaxis=dict(gridcolor='rgba(255,255,255,0.1)'), yaxis=dict(gridcolor='rgba(255,255,255,0.1)'))
            st.plotly_chart(fig_bar, use_container_width=True)

def render_knowledge_graph(paths: dict):
    # Try to render using the streamlit_agraph component. If the component's
    # frontend build file(s) are missing (seen on some installs / Windows envs),
    # fall back to a lightweight Plotly-based graph and provide a selectbox so
    # the rest of the app can still receive a "clicked" node id.
    try:
        nodes = [Node(id="root", label="My Brain", size=25, shape="dot", color="#a275e3")]
        edges = []
        for name, data in paths.items():
            nodes.append(Node(id=name, label=name, size=15, color="#c9a7ff"))
            edges.append(Edge(source="root", target=name, length=200))
            topic = data.get('current_topic', 'Introduction')
            if topic != "Introduction":
                nodes.append(Node(id=f"{name}_{topic}", label=topic, size=10, color="#ffffff"))
                edges.append(Edge(source=name, target=f"{name}_{topic}", length=100))
        config = Config(width=300, height=300, directed=False, physics=True, hierarchical=False,
                        nodeHighlightBehavior=True, highlightColor="#f59e0b", collapsible=True,
                        node={'labelProperty':'label'}, link={'labelProperty': 'label', 'renderLabel': False})
        st.header("My Knowledge Graph")
        return agraph(nodes=nodes, edges=edges, config=config)
    except Exception:
        # Frontend component missing or other error — show a helpful warning and fallback
        st.warning("Knowledge graph component not available; using lightweight fallback visualization.")
        # Build a simple circular layout for nodes
        node_ids = ["root"] + list(paths.keys())
        labels = ["My Brain"] + list(paths.keys())
        n = len(node_ids)
        positions = {}
        for i, nid in enumerate(node_ids):
            angle = (2 * math.pi * i) / max(1, n)
            radius = 1.0 if nid == "root" else 2.0
            positions[nid] = (radius * math.cos(angle), radius * math.sin(angle))

        # Create edge traces
        edge_x = []
        edge_y = []
        for name in paths.keys():
            x0, y0 = positions["root"]
            x1, y1 = positions[name]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines')

        node_x = []
        node_y = []
        for nid in node_ids:
            x, y = positions[nid]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text', text=labels,
            textposition='bottom center', hoverinfo='text', marker=dict(size=18, color=['#a275e3'] + ['#c9a7ff'] * (len(node_ids)-1))
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.header("My Knowledge Graph (fallback)")
        st.plotly_chart(fig, use_container_width=True)

        # Provide a selectbox so the caller can react to a chosen node
        chosen = st.selectbox("Jump to node:", options=[None] + node_ids, format_func=lambda x: "(none)" if x is None else x)
        return chosen

def get_adaptive_preferences(uid: str) -> dict:
    prefs = {'style': 'Simple Explanation', 'persona': 'Friendly Encourager'}
    if not db:
        return prefs
    try:
        docs = db.collection('user_feedback').where(field_path='user_id', op_string='==', value=uid).where(field_path='feedback', op_string='==', value='good').stream()
        style_counts, persona_counts = {}, {}
        for doc in docs:
            data = doc.to_dict() or {}
            if 'style' in data:
                style_counts[data['style']] = style_counts.get(data['style'], 0) + 1
            if 'persona' in data:
                persona_counts[data['persona']] = persona_counts.get(data['persona'], 0) + 1
        if style_counts:
            prefs['style'] = max(style_counts, key=lambda k: style_counts[k])
        if persona_counts:
            prefs['persona'] = max(persona_counts, key=lambda k: persona_counts[k])
    except Exception:
        pass
    return prefs

def render_srs_dashboard(uid):
    if not db: return
    try:
        due_reviews = fetch_review_items_with_fallback(uid, only_due=True)
        if due_reviews:
            st.markdown("---")
            st.header("🧠 Spaced Repetition Review")
            st.info(f"You have **{len(due_reviews)}** items due for review.")
            if st.button("Start Review Session", type="primary", use_container_width=True):
                st.session_state.session.update({'review_session_active': True, 'active_path': None})
                safe_rerun()
    except Exception as e:
        st.error(f"Could not fetch review items: {e}")

def render_srs_view(uid):
    st.title("🧠 Review Session")
    # Use the resilient fetch helper which will fall back to client-side filtering if index is missing
    due_items = fetch_review_items_with_fallback(uid, only_due=True, limit=1)
    if due_items is None:
        st.error("Failed to fetch review item.")
        if st.button("End Review"):
            st.session_state.session['review_session_active'] = False
            safe_rerun()
        st.stop()

    if not due_items:
        st.success("🎉 All done! You've completed your review session for now.")
        st.balloons()
        st.session_state.session['review_session_active'] = False
        if st.button("Back to Dashboard"):
            safe_rerun()
        st.stop()

    review_doc = due_items[0]
    review_data = review_doc.to_dict()
    q_data = review_data.get('question_data', {})
    st.header(f"Reviewing from Path: *{review_data.get('path_name')}*")
    st.subheader(f"Topic: *{review_data.get('topic')}*")
    st.markdown("---")
    st.subheader(q_data.get('question'))

    with st.form(key=f"srs_form_{review_doc.id}"):
        user_answer = st.radio("Your Answer:", q_data.get('options', []))
        if st.form_submit_button("Check Answer"):
            is_correct = (user_answer.strip() == q_data.get('answer', '').strip())
            st.success(f"**Correct!** The answer was: {q_data.get('answer')}") if is_correct else st.error(f"**Not quite.** The correct answer was: {q_data.get('answer')}")
            st.markdown("---"); st.write("How difficult did you find this question?")
            
            def update_review_item(quality):
                ef = review_data.get('ease_factor', 2.5)
                inter = review_data.get('interval', 1)
                if quality < 3: inter = 1
                else:
                    if inter == 1: inter = 6
                    else: inter = round(inter * ef)
                ef += (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
                if ef < 1.3: ef = 1.3
                try:
                    review_doc.reference.update({'due_date': datetime.now() + timedelta(days=inter), 'interval': inter, 'ease_factor': ef})
                    st.toast(f"Next review in {inter} days.")
                    time.sleep(1)
                    safe_rerun()
                except Exception as e:
                    st.error(f"Failed to update review item: {e}")

            c1, c2, c3 = st.columns(3)
            if c1.button("Easy"): update_review_item(5)
            if c2.button("Good"): update_review_item(4)
            if c3.button("Hard"): update_review_item(3 if is_correct else 2)

def render_standard_view(uid, active_path_name, path_data):
    chat_history = path_data.get('chat_history', [])
    current_topic = path_data.get('current_topic', "No topic selected")
    st.markdown(f"🏠 **Home** > 📚 **{active_path_name}** > 🎯 **{current_topic}**")
    st.title(f"📚 Path: {active_path_name}")

    if st.session_state.session.get('current_quiz_data'):
        quiz_state = st.session_state.session['current_quiz_data']
        questions: list = list(quiz_state.get('questions') or [])
        st.header(f"Quiz on: {current_topic}")
        with st.form(key='multi_quiz_form'):
            user_answers: list[str] = [str(st.radio(f"Q{i+1}: {q.get('question')}", q.get('options', []), key=f"mq_{i}")) for i, q in enumerate(questions)]
            if st.form_submit_button("Submit Quiz", use_container_width=True, type="primary"):
                correct_count: int = 0
                incorrect_qs: list = []
                for i, q in enumerate(questions):
                    if str(user_answers[i]).strip() == str(q.get('answer')).strip():
                        correct_count += 1  # type: ignore[operator]
                    else:
                        incorrect_qs.append(q)
                num_q: int = len(questions)
                score: int = int((correct_count / num_q) * 100) if num_q > 0 else 0  # type: ignore[operator]
                st.success(f"You scored {score}% ({correct_count}/{num_q})")
                if db and incorrect_qs:
                    for q_data in incorrect_qs:
                        try:
                            db.collection('review_queue').document().set({
                                'user_id': uid, 'path_name': active_path_name, 'topic': current_topic,
                                'question_data': q_data, 'due_date': datetime.now() + timedelta(days=1),
                                'interval': 1, 'ease_factor': 2.5, 'created_at': firestore.SERVER_TIMESTAMP
                            })
                        except Exception as e: st.warning(f"Could not add to review queue: {e}")
                    st.info(f"{len(incorrect_qs)} questions added to your review queue for tomorrow!")
                if db:
                    try:
                        db.collection('quiz_attempts').document().set({
                            'user_id': uid, 'path_name': active_path_name, 'topic': current_topic,
                            'questions': questions, 'answers': user_answers, 'score': score,
                            'timestamp': firestore.SERVER_TIMESTAMP
                        })
                    except Exception: pass
                st.session_state.session['current_quiz_data'] = None
                safe_rerun()
    else:
        with st.container(border=True):
            st.header("🎯 Define Your Learning Goal")
            topic = st.text_input("What topic do you want to master today?", value=current_topic if current_topic != "Introduction" else "", key="topic_input")
            prefs = get_adaptive_preferences(uid)
            adaptive_style = f"Adaptive ({prefs['style']})"
            adaptive_persona = f"Adaptive ({prefs['persona']})"
            c1, c2 = st.columns(2)
            lang = c1.selectbox("Tutor Language:", ["English", "Tamil", "Hindi", "Spanish", "French"])
            styles = ["Simple Explanation", "Real-world Analogy", "Code Example"]
            if prefs['style'] not in styles: styles.insert(0, adaptive_style)
            style_choice = c2.radio("Style:", styles, horizontal=True)
            personas = ["Friendly Encourager", "Strict Professor", "Socratic Questioner", "Concise Technician", "Creative Storyteller"]
            if prefs['persona'] not in personas: personas.insert(0, adaptive_persona)
            persona_choice = st.selectbox("Tutor Persona:", personas)
            style = prefs['style'] if style_choice == adaptive_style else style_choice
            persona = prefs['persona'] if persona_choice == adaptive_persona else persona_choice

            st.header("🚀 Take Action")
            c1, c2, c3, c4, c5 = st.columns(5)
            if c1.button("Learn", use_container_width=True, type="primary"):
                if topic:
                    path_data['current_topic'] = topic
                    chat_history.append(make_message("user", f"Explain '{topic}' to me."))
                    prompt = f"As an AI tutor with the persona of a '{persona}', please explain the topic '{topic}' in {lang} using the '{style}' method."
                    resp = generate_ai_response(prompt)
                    if resp:
                        chat_history.append(make_message("assistant", resp, generation_params={'style': style, 'persona': persona, 'lang': lang}))
                        save_learning_path(uid, active_path_name, path_data)
                        safe_rerun()
            if c2.button("Take Quiz", use_container_width=True):
                if topic:
                    path_data['current_topic'] = topic
                    prompt = f"""You are a strict quiz master with the persona of a '{persona}'. Create a 3-question multiple choice quiz for '{topic}'. Respond ONLY with a JSON array of objects: [{'{'}"question": "...", "options": ["..."], "answer": "..."{'}'}, ...]"""
                    resp = generate_ai_response(prompt, is_json=True)
                    if resp and (quiz_list := parse_multi_quiz(resp)):
                        st.session_state.session['current_quiz_data'] = {'questions': quiz_list}
                        safe_rerun()
                    else: st.error("AI returned an invalid quiz format. Please try again.")
            if c3.button("Find Resources", use_container_width=True):
                if topic:
                    chat_history.append(make_message("user", f"Find resources for '{topic}'."))
                    prompt = f"As an AI tutor with the persona of a '{persona}', please suggest 3 high-quality online resources in {lang} for a student learning about '{topic}'."
                    resp = generate_ai_response(prompt)
                    if resp:
                        chat_history.append(make_message("assistant", resp))
                        save_learning_path(uid, active_path_name, path_data)
                        safe_rerun()
            if c4.button("Find Certs", use_container_width=True):
                if topic:
                    chat_history.append(make_message("user", f"Find certifications for '{topic}'."))
                    prompt = f"As an AI tutor with the persona of a '{persona}', please list 2-3 professional certifications in {lang} related to '{topic}'."
                    resp = generate_ai_response(prompt)
                    if resp:
                        chat_history.append(make_message("assistant", resp))
                        save_learning_path(uid, active_path_name, path_data)
                        safe_rerun()
            if c5.button("Next Topic?", use_container_width=True):
                prompt = f"I am learning about '{active_path_name}'. I just learned about '{current_topic}'. As an AI tutor with the persona of a '{persona}', what is the single most logical topic I should learn next in {lang}? Respond with only the topic name."
                if next_topic := generate_ai_response(prompt): st.success(f"AI Suggests: **{next_topic}**")

        with st.container(border=True, height=500):
            for i, message in enumerate(chat_history):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message["role"] == "assistant":
                        c1, c2, c3 = st.columns([1, 1, 10])
                        key = f"{active_path_name}_{i}"
                        style_used = message.get('generation_params', {}).get('style')
                        persona_used = message.get('generation_params', {}).get('persona')
                        if c1.button("👍", key=f"up_{key}"): save_feedback(uid, active_path_name, current_topic, "good", message['content'], style=style_used, persona=persona_used)
                        if c2.button("👎", key=f"down_{key}"): save_feedback(uid, active_path_name, current_topic, "bad", message['content'], style=style_used, persona=persona_used)
                        st_copy_to_clipboard(message["content"], key=f"copy_{key}")

        if prompt := st.chat_input(f"Ask a follow-up question about '{current_topic}'..."):
            chat_history.append(make_message("user", prompt))
            full_prompt = f"As an AI tutor with the persona of a '{persona}', please answer my follow-up question in {lang} regarding the topic '{current_topic}': {prompt}"
            if resp := generate_ai_response(full_prompt):
                chat_history.append(make_message("assistant", resp))
                save_learning_path(uid, active_path_name, path_data)
                safe_rerun()

def render_project_view(uid, active_path_name, path_data):
    st.markdown(f"🏠 **Home** > 🛠️ **{active_path_name}** > Step {path_data.get('current_step_index', 0) + 1}")
    st.title(f"🛠️ Project: {active_path_name}")
    if not path_data.get('project_goal'):
        with st.form("project_goal_form"):
            st.header("Define Your Project Goal")
            goal_text = st.text_area("What do you want to build?", placeholder="e.g., A Python app that fetches the weather for a city using an API.")
            if st.form_submit_button("Set Goal & Generate Steps") and goal_text:
                path_data['project_goal'] = goal_text
                prompt = f"""A user wants to build: '{goal_text}'. Break this into 5-7 logical steps. For each, provide a 'title' and 'description'. Respond ONLY with a JSON array of objects."""
                if (resp := generate_ai_response(prompt, is_json=True)) and (steps := parse_multi_quiz(resp)):
                    path_data.update({'project_steps': steps, 'current_step_index': 0})
                    save_learning_path(uid, active_path_name, path_data)
                    safe_rerun()
                else: st.error("Failed to generate project steps. Please try again.")
        st.stop()

    st.header("Project Goal"); st.success(path_data.get('project_goal')); st.markdown("---")
    steps = path_data.get('project_steps', [])
    if not steps: st.warning("No steps generated yet."); st.stop()
    
    current_step_index = path_data.get('current_step_index', 0)
    st.sidebar.header("Project Steps")
    step_titles = [f"Step {i+1}: {s['title']}" for i, s in enumerate(steps)]
    chosen_step_title = st.sidebar.radio("Navigate Steps", step_titles, index=current_step_index)
    if (new_index := step_titles.index(chosen_step_title)) != current_step_index:
        path_data['current_step_index'] = new_index
        save_learning_path(uid, active_path_name, path_data)
        safe_rerun()

    current_step_data = steps[current_step_index]
    st.header(f"Step {current_step_index + 1}: {current_step_data['title']}")
    st.info(current_step_data['description'])

    code_key = f"code_{current_step_index}"
    user_code = st.text_area("Your Code for this Step:", value=path_data.get('user_code_per_step', {}).get(code_key, ""), height=300, key=f"editor_{code_key}") if not ACE_SUPPORT else st_ace(value=path_data.get('user_code_per_step', {}).get(code_key, ""), language='python', theme='monokai', key=f"editor_{code_key}", height=300)
    path_data.setdefault('user_code_per_step', {})[code_key] = user_code
    save_learning_path(uid, active_path_name, path_data)

    c1, c2, c3 = st.columns(3)
    def add_project_chat(user_msg, ai_prompt):
        resp = generate_ai_response(ai_prompt)
        if resp:
            path_data['chat_history'].append(make_message("user", user_msg))
            path_data['chat_history'].append(make_message("assistant", resp))
            save_learning_path(uid, active_path_name, path_data)
            safe_rerun()
    
    if c1.button("Check My Code", use_container_width=True, type="primary"):
        prompt = f"Project: '{path_data['project_goal']}'. Step: '{current_step_data['title']}'. Code:\n```python\n{user_code}\n```\nReview the code for this step. Be constructive and encouraging."
        add_project_chat("Please check my code for the current step.", prompt)
    if c2.button("I'm Stuck, Give Me a Hint", use_container_width=True):
        prompt = f"Project: '{path_data['project_goal']}'. Step: '{current_step_data['title']}'. Give a small, helpful hint. Don't give the full answer."
        add_project_chat("I'm stuck, can I have a hint?", prompt)
    if c3.button("Show Me an Example", use_container_width=True):
        prompt = f"Project: '{path_data['project_goal']}'. Step: '{current_step_data['title']}'. Provide a clear, complete code example for this step."
        add_project_chat("Can you show me an example for this step?", prompt)

    st.markdown("---"); st.header("Tutor Chat")
    with st.container(border=True, height=400):
        for i, message in enumerate(reversed(path_data.get('chat_history', []))):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


def render_vision_tab():
    st.header("Live Vision Solver")
    st.markdown("Snap a photo of a math problem, diagram, or code snippet. The AI will analyze and solve it!")

    img_file = st.camera_input("Take a photo")

    if img_file:
        from PIL import Image
        image = Image.open(img_file)
        st.image(image, caption="Captured Image", width=300)

        if st.button("Solve & Explain", type="primary"):
            if not client:
                st.error("AI model not available.")
                return

            with st.spinner("Analyzing visual data..."):
                try:
                    # For now, use text-based analysis via Gemini
                    # (Image vision requires the google.generativeai SDK directly)
                    st.info("Vision analysis: Describe the problem in the Home Chat for AI assistance.")
                    prompt = "The user has uploaded an educational image/problem. Please explain that you can help them if they describe the problem in text form, and offer to solve any math/science/educational problem they describe."
                    resp = _call_gemini(prompt)
                    if resp:
                        st.markdown("### AI Response")
                        st.write(resp)
                except Exception as e:
                    st.error(f"Vision analysis failed: {e}")

def _feynman_history_to_prompt(history: list) -> str:
    """Convert the Feynman chat history into a single text prompt."""
    parts = []
    for msg in history:
        content = msg['parts'][0] if isinstance(msg['parts'], list) else msg['parts']
        role = "AI Student" if msg['role'] == 'model' else "Teacher"
        parts.append(f"{role}: {content}")
    return "\n".join(parts)


def render_feynman_tab():
    st.header("The Feynman Board")
    st.markdown("*> \"The best way to verify you know something is to try and teach it.\"*")
    st.info("In this mode, **YOU** are the teacher. Explain a concept to the AI. It will act as a curious student and ask questions to test your depth of understanding.")

    if 'feynman_topic' not in st.session_state:
        st.session_state['feynman_topic'] = ''
    if 'feynman_history' not in st.session_state:
        st.session_state['feynman_history'] = []

    topic = st.text_input("What topic are you teaching today?", value=st.session_state['feynman_topic'], placeholder="e.g. Quantum Entanglement, The Water Cycle...", key="feynman_topic_input")

    if topic != st.session_state['feynman_topic']:
        st.session_state['feynman_topic'] = topic
        st.session_state['feynman_history'] = []

        init_prompt = f"I want to teach you about '{topic}'. Act as a curious, slightly confused student. Ask clarifying questions to test my understanding. Don't just say 'good job' or lecture me. Probe for details. Start by asking me to explain the basic concept."

        try:
            resp = _call_gemini(init_prompt)
            if resp:
                st.session_state['feynman_history'].append({'role': 'user', 'parts': [init_prompt]})
                st.session_state['feynman_history'].append({'role': 'model', 'parts': [resp]})
        except Exception as e:
            st.error(f"AI Connection Error: {e}")

    for msg in st.session_state['feynman_history']:
        content = msg['parts'][0] if isinstance(msg['parts'], list) else msg['parts']

        if "Act as a curious" in content:
            continue

        role = "student" if msg['role'] == 'model' else "teacher"
        with st.chat_message(role, avatar=None):
            st.write(content)

    if user_input := st.chat_input(f"Explain {topic or 'concept'}..."):
        st.session_state['feynman_history'].append({'role': 'user', 'parts': [user_input]})
        with st.chat_message("teacher", avatar=None):
            st.write(user_input)

        with st.spinner("Student is thinking..."):
            try:
                history_prompt = _feynman_history_to_prompt(st.session_state['feynman_history'])
                reply = _call_gemini(history_prompt)
                if reply:
                    st.session_state['feynman_history'].append({'role': 'model', 'parts': [reply]})
                    with st.chat_message("student", avatar=None):
                        st.write(reply)
            except Exception as e:
                st.error(f"Student got confused (Error): {e}")

def render_social_impact_tab():
    st.header("Social Impact & Accessibility")
    st.markdown("Features designed for rural inclusion, ethical AI, and offline capabilities.")

    def _safe_json_list(text: str):
        if not text:
            return None
        try:
            parsed = json.loads(text)
            return parsed
        except Exception:
            # Try extracting JSON from code fences
            try:
                m = re.search(r'```(?:json\n)?(.*?)```', text, re.DOTALL | re.IGNORECASE)
                if m:
                    return json.loads(m.group(1).strip())
            except Exception:
                pass
        return None

    def _enforce_sms(messages, limit=160, max_messages=6):
        if not messages:
            return []
        cleaned = []
        for m in messages:
            s = str(m).replace("\n", " ").strip()
            # hard enforce the 160-char constraint
            if len(s) > limit:
                s = s[: max(0, limit - 1)].rstrip() + "…"
            if s:
                cleaned.append(s)
            if len(cleaned) >= max_messages:
                break
        return cleaned
    
    impact_mode = st.radio("Select Mode:", 
        ["Rural Analogy Engine", "Bias-Free Unity Chat", "Community Problem Solver", "Low-Bandwidth / SMS Simulator", "Multi-Channel Lesson Pack"],
        horizontal=True
    )
    
    st.markdown("---")

    if impact_mode == "Rural Analogy Engine":
        st.subheader("Localized Analogy Engine")
        st.info("Translates complex technical concepts into simple analogies based on village life, agriculture, and local business.")
        
        topic = st.text_input("Enter a complex topic (e.g., Blockchain, AI, Cloud Computing):")
        if topic and st.button("Generate Rural Analogy"):
             with st.spinner("Translating to village context..."):
                prompt = f"Explain the concept of '{topic}' using simple analogies related to Indian village life, agriculture, farming, or local markets. Avoid technical jargon. Make it relatable to someone in a rural community."
                response = generate_ai_response(prompt)
                if response:
                    st.success(response)
                    
    elif impact_mode == "Bias-Free Unity Chat":
        st.subheader("Bias-Free Unity Filter")
        st.markdown(
            "A multi-layered guardrail system that ensures AI responses are factual, inclusive, and free from religious, caste, or political bias. "
            "Unlike crude word-replacement filters, this uses **prompt-level ethical framing** — the AI sees the full query but is instructed to respond through a neutrality lens."
        )

        query = st.text_input("Ask a question about history, society, or politics:", key="unity_query")

        # Bias sensitivity classification
        UNITY_SYSTEM_PROMPT = (
            "You are an educational AI with a strict neutrality policy.\n"
            "RULES:\n"
            "1. Present all religious, ethnic, and caste groups with equal respect.\n"
            "2. Use factual, cited information only. If uncertain, say 'This is debated among scholars.'\n"
            "3. When describing historical conflicts, focus on causes, consequences, and resolution — never assign blame to a community.\n"
            "4. Highlight shared contributions: science, art, trade, language that communities built together.\n"
            "5. Never use stereotypes or generalizations about any demographic.\n"
            "6. If the question is intentionally provocative, reframe it as a constructive educational query.\n"
            "7. End with a 'Unity Note' — one sentence about what different communities share in this context.\n"
        )

        if query and st.button("Get Neutral Answer", key="unity_btn"):
            with st.spinner("Applying ethical guardrails..."):
                # Step 1: Classify sensitivity
                classify_prompt = (
                    f"Classify the following query into one of: LOW, MEDIUM, HIGH sensitivity "
                    f"based on whether it touches religion, caste, politics, or communal topics. "
                    f"Respond with ONLY one word: LOW, MEDIUM, or HIGH.\n\nQuery: {query}"
                )
                sensitivity = (generate_ai_response(classify_prompt) or "MEDIUM").strip().upper()
                if sensitivity not in ("LOW", "MEDIUM", "HIGH"):
                    sensitivity = "MEDIUM"

                # Step 2: Generate response with guardrails
                full_prompt = (
                    f"{UNITY_SYSTEM_PROMPT}\n"
                    f"Sensitivity level: {sensitivity}\n"
                    f"User query: {query}\n\n"
                    f"Provide a balanced, fact-based educational answer. "
                    f"Structure your response as:\n"
                    f"**Context**: (2-3 sentences of neutral background)\n"
                    f"**Key Facts**: (3-4 bullet points)\n"
                    f"**Multiple Perspectives**: (if applicable, present 2+ viewpoints fairly)\n"
                    f"**Unity Note**: (1 sentence highlighting shared values)\n"
                )
                response = generate_ai_response(full_prompt)

                if response:
                    # Sensitivity indicator
                    colors = {"LOW": "#238636", "MEDIUM": "#d29922", "HIGH": "#da3633"}
                    labels = {"LOW": "Low sensitivity", "MEDIUM": "Moderate sensitivity", "HIGH": "High sensitivity"}
                    st.markdown(
                        f"<div style='display:inline-block; padding:4px 12px; border-radius:12px; "
                        f"background:{colors.get(sensitivity, '#555')}; color:#fff; font-size:12px; "
                        f"font-weight:500; margin-bottom:12px;'>"
                        f"{labels.get(sensitivity, 'Unknown')}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(response)

                    # Transparency panel
                    with st.expander("Transparency: How this answer was generated"):
                        st.markdown(
                            "- **Word replacement**: None. The full query was sent to the AI without censorship.\n"
                            "- **Guardrail method**: Prompt-level ethical framing with 7 neutrality rules.\n"
                            f"- **Sensitivity classification**: {sensitivity}\n"
                            "- **Bias check**: The AI was instructed to present multiple perspectives and avoid stereotypes.\n"
                            "- **Limitation**: AI-generated content should be verified with authoritative sources."
                        )
                    
    elif impact_mode == "Community Problem Solver":
        st.subheader("Community Problem Solver")
        st.info("Input real local issues. The AI designs practical, low-cost tech solutions.")
        
        problem = st.text_area("Describe the local problem (e.g., Water shortage in summer, Crop pests):")
        if problem and st.button("Find Solution"):
            with st.spinner("Engineering low-cost solutions..."):
                prompt = f"The user is from a rural community facing this issue: '{problem}'. Propose 3 practical, low-cost technical solutions using locally available resources. Focus on engineering, simple science, or DIY methods. Format as a clear list."
                response = generate_ai_response(prompt)
                if response:
                    st.markdown(response)
    
    elif impact_mode == "Low-Bandwidth / SMS Simulator":
        st.subheader("Low-Bandwidth / SMS Simulator")
        st.markdown("Demonstrates offline accessibility by generating ultra-short, 160-character educational responses. This proves the AI can reach remote users who don't have internet access or smartphones.")
        
        sms_query = st.text_input("Enter educational query (for SMS generation):")
        if sms_query and st.button("Generate SMS"):
            with st.spinner("Compressing knowledge for low bandwidth..."):
                prompt = f"Explain '{sms_query}' in strictly less than 160 characters. Use abbreviations if necessary. Format it as a raw SMS text. Do not include quotes."
                response = generate_ai_response(prompt)
                if response:
                    # Visual simulation of an old phone screen or terminal
                    st.markdown(f"""
                    <div style="border: 4px solid #333; border-radius: 12px; padding: 15px; background-color: #89CFF0; color: #000; font-family: 'Courier New', monospace; width: 320px; box-shadow: 5px 5px 15px rgba(0,0,0,0.5);">
                        <div style="font-size: 10px; border-bottom: 1px solid #000; margin-bottom: 8px; color: #333; display:flex; justify-content:space-between;">
                            <span>📶 NOKIA 1100</span><span>🔋 98%</span>
                        </div>
                        <div style="font-size: 14px; font-weight: bold; line-height: 1.2;">
                            MSG: {response}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"Network: 2G | Char count: {len(response)} / 160")

    elif impact_mode == "Multi-Channel Lesson Pack":
        st.subheader("Multi-Channel Lesson Pack")
        st.markdown(
            "Generate the same lesson in formats that work across devices: smartphone, SMS/feature phone, voice/IVR script, and printable one-pager. "
            "This is designed for rural reach while still looking premium for international evaluation."
        )

        col_a, col_b = st.columns([3, 2])
        with col_a:
            pack_topic = st.text_input("Topic", placeholder="e.g., What is IoT?", key="pack_topic")
        with col_b:
            pack_level = st.selectbox("Reading level", ["Grade 6", "Grade 8", "Grade 10", "Undergraduate"], index=2, key="pack_level")

        pack_lang = st.selectbox(
            "Language",
            ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"],
            index=0,
            key="pack_lang",
        )
        include_rural_analogy = st.checkbox("Include rural analogy", value=True, key="pack_rural_analogy")

        if st.button("Generate Lesson Pack", type="primary", key="gen_pack_btn"):
            if not pack_topic:
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Generating multi-channel pack..."):
                    analogy_line = "Include one rural-life analogy." if include_rural_analogy else "Do not use rural analogies unless necessary."

                    json_schema = {
                        "smartphone": {
                            "title": "",
                            "summary": "",
                            "key_points": [""],
                            "example": "",
                            "mini_quiz": [{"q": "", "a": ""}],
                        },
                        "sms": [""],
                        "ivr": [""],
                        "printable": {
                            "headline": "",
                            "bullets": [""],
                            "do": [""],
                            "dont": [""],
                        },
                        "trust_card": {
                            "certainty": "",
                            "assumptions": [""],
                            "verification_keywords": [""],
                            "safety_notes": [""],
                            "inclusion_notes": [""],
                        },
                    }

                    prompt = (
                        f"Create a multi-channel learning pack for the topic: {pack_topic}. "
                        f"Target reading level: {pack_level}. Language: {pack_lang}. {analogy_line} "
                        "Return ONLY valid JSON matching this schema exactly (no markdown, no extra keys, no emojis):\n"
                        + json.dumps(json_schema)
                        + "\nConstraints:\n"
                        "- sms: 4 to 6 messages, each <= 160 characters, plain text, numbered like '1/5 ...'\n"
                        "- ivr: 6 to 10 short voice lines, each <= 90 characters (for voice prompts)\n"
                        "- printable: concise bullets, no emojis\n"
                        "- trust_card: be neutral, bias-aware, and practical; certainty must be one of: Low, Medium, High\n"
                    )

                    resp = generate_ai_response(prompt, is_json=True)
                    pack = _safe_json_list(resp)
                    if not isinstance(pack, dict):
                        st.error("Failed to generate a valid pack. Please try again.")
                        return

                    sms_msgs = _enforce_sms(pack.get("sms") or [])
                    ivr_lines = pack.get("ivr") or []
                    smartphone = pack.get("smartphone") or {}
                    printable = pack.get("printable") or {}
                    trust_card = pack.get("trust_card") or {}

                    st.markdown("---")
                    t1, t2, t3, t4, t5 = st.tabs(["Smartphone", "SMS", "Voice/IVR", "Printable", "Trust Card"])

                    with t1:
                        st.markdown(f"### {smartphone.get('title') or 'Lesson'}")
                        if smartphone.get("summary"):
                            st.write(smartphone.get("summary"))
                        if smartphone.get("key_points"):
                            st.markdown("**Key points**")
                            for p in list(smartphone.get("key_points") or [])[:6]:  # type: ignore[index]
                                st.write(f"- {p}")
                        if smartphone.get("example"):
                            st.markdown("**Example**")
                            st.write(smartphone.get("example"))
                        if smartphone.get("mini_quiz"):
                            st.markdown("**Mini check**")
                            for qa in list(smartphone.get("mini_quiz") or [])[:3]:  # type: ignore[index]
                                st.write(f"Q: {qa.get('q','')}")
                                st.caption(f"A: {qa.get('a','')}")

                    with t2:
                        st.markdown("### SMS Sequence")
                        if not sms_msgs:
                            st.info("No SMS messages generated.")
                        else:
                            for m in sms_msgs:
                                st.code(m, language="text")
                            st.caption("Each message is constrained to 160 characters.")

                    with t3:
                        st.markdown("### Voice / IVR Script")
                        if not ivr_lines:
                            st.info("No IVR lines generated.")
                        else:
                            ivr_list: list = list(ivr_lines[:12])  # type: ignore[index]
                            for i, line in enumerate(ivr_list, 1):
                                st.write(f"{i}. {str(line).strip()}")
                            st.caption("Short lines for IVR / phone call delivery.")

                    with t4:
                        st.markdown("### Printable One-Pager")
                        st.markdown(f"**{printable.get('headline') or pack_topic}**")
                        for b in list(printable.get("bullets") or [])[:10]:  # type: ignore[index]
                            st.write(f"- {b}")
                        col_do, col_dont = st.columns(2)
                        with col_do:
                            st.markdown("**Do**")
                            for d in list(printable.get("do") or [])[:6]:  # type: ignore[index]
                                st.write(f"- {d}")
                        with col_dont:
                            st.markdown("**Don't**")
                            for d in list(printable.get("dont") or [])[:6]:  # type: ignore[index]
                                st.write(f"- {d}")

                    with t5:
                        st.markdown("### Trust & Safety Card")
                        st.caption("A transparent summary of uncertainty, assumptions, and verification prompts.")

                        certainty: str = str(trust_card.get("certainty") or "").strip() or "Medium"
                        st.markdown(f"**Certainty:** {certainty}")

                        assumptions = trust_card.get("assumptions") or []
                        if assumptions:
                            st.markdown("**Assumptions**")
                            for a in list(assumptions)[:8]:  # type: ignore[index]
                                st.write(f"- {a}")

                        vk = trust_card.get("verification_keywords") or []
                        if vk:
                            st.markdown("**Verification keywords**")
                            vk_items: list[str] = [str(x).strip() for x in vk if str(x).strip()][:12]
                            st.write(", ".join(vk_items))

                        safety = trust_card.get("safety_notes") or []
                        if safety:
                            st.markdown("**Safety notes**")
                            for s in list(safety)[:8]:  # type: ignore[index]
                                st.write(f"- {s}")

                        incl = trust_card.get("inclusion_notes") or []
                        if incl:
                            st.markdown("**Inclusion notes**")
                            for s in list(incl)[:8]:  # type: ignore[index]
                                st.write(f"- {s}")

                    # Downloads
                    pack_out = {
                        **pack,
                        "sms": sms_msgs,
                    }
                    pack_json = json.dumps(pack_out, ensure_ascii=False, indent=2)
                    pack_txt = (
                        f"TOPIC: {pack_topic}\nLEVEL: {pack_level}\nLANG: {pack_lang}\n\n"
                        f"SMARTPHONE TITLE: {smartphone.get('title','')}\n"
                        f"SUMMARY: {smartphone.get('summary','')}\n\n"
                        "SMS:\n" + "\n".join(sms_msgs) + "\n\n"
                        "IVR:\n" + "\n".join([str(x).strip() for x in ivr_lines]) + "\n\n"
                        "PRINTABLE:\n" + "\n".join(["- " + str(x).strip() for x in (printable.get('bullets') or [])]) + "\n\n"
                        "TRUST CARD:\n"
                        + f"Certainty: {certainty}\n"
                        + "Assumptions:\n" + "\n".join(["- " + str(x).strip() for x in (trust_card.get('assumptions') or [])]) + "\n"
                        + "Verification keywords: " + ", ".join([str(x).strip() for x in (trust_card.get('verification_keywords') or [])]) + "\n"
                        + "Safety notes:\n" + "\n".join(["- " + str(x).strip() for x in (trust_card.get('safety_notes') or [])]) + "\n"
                    )

                    cdl1, cdl2 = st.columns(2)
                    with cdl1:
                        st.download_button(
                            "Download JSON Pack",
                            data=pack_json.encode("utf-8"),
                            file_name=f"lesson_pack_{re.sub(r'[^a-zA-Z0-9]+', '_', pack_topic)[:40]}.json",
                            mime="application/json",
                            key="dl_pack_json",
                        )
                    with cdl2:
                        st.download_button(
                            "Download TXT Pack",
                            data=pack_txt.encode("utf-8"),
                            file_name=f"lesson_pack_{re.sub(r'[^a-zA-Z0-9]+', '_', pack_topic)[:40]}.txt",
                            mime="text/plain",
                            key="dl_pack_txt",
                        )

def render_career_path_tab():
    """AI-Powered Career Path Finder with skills gap analysis."""
    st.header("Career Path Finder")
    st.markdown(
        "Answer a few questions about your skills and interests. "
        "The AI will generate personalized career paths, required skills, "
        "recommended courses, and project ideas."
    )

    with st.form("career_form"):
        col1, col2 = st.columns(2)
        with col1:
            interests = st.text_input("Your interests", placeholder="e.g., coding, design, farming, healthcare")
            education = st.selectbox("Education level", ["Below 10th", "10th Pass", "12th Pass", "Diploma", "Undergraduate", "Postgraduate"])
        with col2:
            skills = st.text_input("Current skills", placeholder="e.g., Python, MS Excel, welding, tailoring")
            location = st.selectbox("Location type", ["Rural village", "Small town", "City", "Metro city"])

        aspirations = st.text_area("What do you dream of becoming?", placeholder="e.g., I want to build apps, I want to start a small business, I want to help my community...")
        budget = st.selectbox("Learning budget", ["Free resources only", "Under 500 INR/month", "Under 2000 INR/month", "No constraint"])
        submitted = st.form_submit_button("Generate Career Paths")

    if submitted:
        if not interests and not aspirations:
            st.warning("Please fill in at least your interests or aspirations.")
            return
        with st.spinner("Analyzing career landscape..."):
            prompt = (
                f"You are a career counselor AI for students from diverse backgrounds.\n"
                f"Student profile:\n"
                f"- Interests: {interests}\n"
                f"- Current skills: {skills}\n"
                f"- Education: {education}\n"
                f"- Location: {location}\n"
                f"- Aspirations: {aspirations}\n"
                f"- Budget: {budget}\n\n"
                f"Generate exactly 3 career paths. For each path provide:\n"
                f"1. Career title and 1-line description\n"
                f"2. Skills gap: what they need to learn (max 5 skills)\n"
                f"3. Recommended free/low-cost courses or resources (max 3)\n"
                f"4. A starter project they can build to prove competence\n"
                f"5. Estimated time to job-readiness\n"
                f"6. Salary range (entry-level in India)\n\n"
                f"Format clearly with markdown headers for each career path."
            )
            resp = generate_ai_response(prompt)
            if resp:
                st.markdown(resp)

                # Skills gap visualization
                with st.expander("Skills Gap Analysis"):
                    gap_prompt = (
                        f"Based on this student's current skills ({skills}) and the career paths you suggested, "
                        f"return ONLY a JSON object with keys being skill names and values being proficiency from 0-100 "
                        f"where 0 means 'needs to learn from scratch' and 100 means 'already proficient'. "
                        f"Include 6-8 skills total."
                    )
                    gap_resp = generate_ai_response(gap_prompt, is_json=True)
                    if gap_resp:
                        try:
                            gap_data = json.loads(gap_resp) if isinstance(gap_resp, str) else gap_resp
                            if isinstance(gap_data, dict):
                                skills_list = list(gap_data.keys())
                                values = [int(v) for v in gap_data.values()]
                                fig = go.Figure(data=[go.Bar(
                                    x=skills_list, y=values,
                                    marker_color=['#238636' if v >= 60 else '#d29922' if v >= 30 else '#da3633' for v in values]
                                )])
                                fig.update_layout(
                                    title="Your Skills vs Requirements",
                                    yaxis_title="Proficiency %", yaxis_range=[0, 100],
                                    template="plotly_dark", height=350,
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass


def render_summarizer_tab():
    """AI-Powered Textbook Summarizer with multiple output formats."""
    st.header("Textbook Summarizer")
    st.markdown("Paste a chapter or upload a text file. The AI will extract key concepts, generate bullet-point summaries, flashcards, and exam notes.")

    input_method = st.radio("Input method:", ["Paste text", "Upload file"], horizontal=True, key="sum_input_method")

    raw_text = ""
    if input_method == "Paste text":
        raw_text = st.text_area("Paste your textbook content here:", height=200, key="sum_paste")
    else:
        uploaded = st.file_uploader("Upload a .txt or .md file", type=["txt", "md"], key="sum_upload")
        if uploaded:
            raw_text = uploaded.read().decode("utf-8", errors="ignore")
            st.caption(f"Loaded {len(raw_text)} characters from {uploaded.name}")

    if not raw_text:
        return

    output_format = st.selectbox("Output format:", ["Bullet-point summary", "Flashcards (Q&A)", "Exam answer notes", "Mind map outline", "All formats"], key="sum_format")

    if st.button("Summarize", type="primary", key="sum_btn"):
        # Truncate very long texts to avoid token limits
        truncated = raw_text[:12000]
        if len(raw_text) > 12000:
            st.caption(f"Text truncated to 12,000 characters (original: {len(raw_text):,})")

        with st.spinner("Summarizing..."):
            format_instructions = {
                "Bullet-point summary": "Provide a concise bullet-point summary with key concepts, definitions, and important facts. Max 15 bullets.",
                "Flashcards (Q&A)": "Generate 8-10 flashcards as Q&A pairs. Format: Q: ... A: ...",
                "Exam answer notes": "Convert into exam-ready notes: definition, key points, example, diagram description (if applicable), conclusion. Suitable for 6-10 mark answers.",
                "Mind map outline": "Create a hierarchical mind map outline using indentation. Main topic > Sub-topics > Details.",
                "All formats": "Provide ALL of the following:\n1. Bullet-point summary (10 bullets)\n2. 5 Flashcards (Q&A)\n3. One exam answer template (6-mark format)\n4. Mind map outline",
            }
            prompt = (
                f"You are an educational summarizer.\n"
                f"Instructions: {format_instructions.get(output_format, '')}\n\n"
                f"TEXT TO SUMMARIZE:\n{truncated}"
            )
            resp = generate_ai_response(prompt)
            if resp:
                st.markdown(resp)
                st.download_button(
                    "Download summary",
                    data=resp.encode("utf-8"),
                    file_name="summary.md",
                    mime="text/markdown",
                    key="dl_summary",
                )


def render_voice_input_component():
    """Render a browser-based voice input button using Web Speech API."""
    components.html("""
    <div id="voice-container" style="margin:8px 0;">
        <button id="voice-btn" onclick="startVoice()" style="
            background:#238636; color:#fff; border:1px solid rgba(240,246,252,0.1);
            border-radius:6px; padding:8px 18px; font-size:14px; font-weight:500;
            cursor:pointer; font-family:'Inter',sans-serif;
        ">Hold to Speak</button>
        <span id="voice-status" style="color:#8b949e; font-size:13px; margin-left:10px;"></span>
        <input type="hidden" id="voice-result" value="" />
    </div>
    <script>
    let recognition = null;
    function startVoice() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            document.getElementById('voice-status').innerText = 'Voice not supported in this browser.';
            return;
        }
        if (recognition) { recognition.stop(); recognition = null; return; }
        recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        const btn = document.getElementById('voice-btn');
        const status = document.getElementById('voice-status');
        btn.innerText = 'Listening...';
        btn.style.background = '#da3633';
        status.innerText = 'Speak now...';
        recognition.start();
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            status.innerText = 'Heard: ' + transcript;
            btn.innerText = 'Hold to Speak';
            btn.style.background = '#238636';
            // Send to Streamlit via query params trick
            const url = new URL(window.parent.location);
            url.searchParams.set('voice_input', transcript);
            window.parent.history.replaceState({}, '', url);
            // Also copy to clipboard for easy paste
            navigator.clipboard.writeText(transcript).catch(()=>{});
            recognition = null;
        };
        recognition.onerror = function(event) {
            status.innerText = 'Error: ' + event.error;
            btn.innerText = 'Hold to Speak';
            btn.style.background = '#238636';
            recognition = null;
        };
        recognition.onend = function() {
            btn.innerText = 'Hold to Speak';
            btn.style.background = '#238636';
        };
    }
    </script>
    """, height=60)


def render_context_aware_greeting():
    """Show a context-aware adaptive greeting based on time of day and session history."""
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
        tip = "Keep sessions short. Try the SMS Simulator for quick micro-lessons."

    # Count session stats
    paths = st.session_state.session.get('learning_paths', {})
    total_msgs = sum(len(p.get('chat_history', [])) for p in paths.values())

    user_name = (st.session_state.session.get('user_info') or {}).get('nickname', '')
    display_name = f", {user_name}" if user_name else ""

    st.markdown(
        f"<div style='padding:16px 20px; background:rgba(22,27,34,0.8); border:1px solid #30363d; "
        f"border-radius:8px; margin-bottom:16px;'>"
        f"<div style='font-size:20px; font-weight:600; color:#c9d1d9;'>{greeting}{display_name}</div>"
        f"<div style='font-size:13px; color:#8b949e; margin-top:4px;'>{tip}</div>"
        f"<div style='font-size:12px; color:#58a6ff; margin-top:8px;'>"
        f"{len(paths)} paths  ·  {total_msgs} messages  ·  {now.strftime('%A, %b %d')}"
        f"</div></div>",
        unsafe_allow_html=True,
    )


def detect_emotion_and_adapt(user_text: str) -> str:
    """Detect user's emotional state from their text and return an adaptive prompt prefix.
    Uses keyword heuristics for speed (no extra API call), with AI fallback for ambiguous cases.
    """
    text_lower = user_text.lower()

    # Fast keyword-based detection
    frustration_words = ["i don't understand", "confused", "stuck", "lost", "frustrated", "hard", "difficult", "can't", "impossible", "hate", "annoying", "help me", "not getting"]
    success_words = ["got it", "understood", "makes sense", "thank you", "thanks", "awesome", "great", "perfect", "i see", "clear now", "finally"]
    anxiety_words = ["exam", "test tomorrow", "scared", "worried", "nervous", "failing", "deadline", "urgent", "panic"]
    boredom_words = ["boring", "bored", "too easy", "already know", "skip", "next"]

    if any(w in text_lower for w in frustration_words):
        return (
            "The student seems frustrated or confused. Respond with patience and empathy. "
            "Break down the concept into smaller steps. Use an encouraging tone. "
            "Say something like 'That is a really common sticking point, let me explain it differently.' "
        )
    elif any(w in text_lower for w in anxiety_words):
        return (
            "The student seems anxious about an upcoming exam or deadline. "
            "Respond calmly and reassuringly. Focus on the most important points only. "
            "Offer a quick revision strategy. Say 'Let us focus on the key points that matter most.' "
        )
    elif any(w in text_lower for w in success_words):
        return (
            "The student seems to have understood the concept. Acknowledge their progress warmly. "
            "Then challenge them with a slightly harder follow-up question to deepen understanding. "
            "Say 'Excellent progress. Now try this slightly trickier angle...' "
        )
    elif any(w in text_lower for w in boredom_words):
        return (
            "The student seems bored or unchallenged. Increase the difficulty. "
            "Offer a real-world application or a challenging problem. "
            "Say 'Let us level up. Here is a real-world challenge...' "
        )
    return ""  # Neutral — no emotional adaptation needed


def render_collaborative_problem_tab():
    """Collaborative Problem-Solving Mode with structured brainstorming."""
    st.header("Collaborative Problem Solver")
    st.markdown(
        "Submit a real-world problem from your community. The AI will guide you through "
        "a structured brainstorming process: define, research, ideate, prototype, and plan."
    )

    if 'collab_stage' not in st.session_state:
        st.session_state['collab_stage'] = 'define'
    if 'collab_history' not in st.session_state:
        st.session_state['collab_history'] = []
    if 'collab_problem' not in st.session_state:
        st.session_state['collab_problem'] = ''

    stages = ['define', 'research', 'ideate', 'prototype', 'plan']
    stage_labels = {
        'define': 'Define the Problem',
        'research': 'Research & Context',
        'ideate': 'Generate Solutions',
        'prototype': 'Prototype Plan',
        'plan': 'Action Plan',
    }

    # Progress bar
    current_idx = stages.index(st.session_state['collab_stage'])
    st.progress((current_idx + 1) / len(stages), text=f"Stage {current_idx + 1}/5: {stage_labels[st.session_state['collab_stage']]}")

    if st.session_state['collab_stage'] == 'define':
        problem = st.text_area("Describe the problem your community faces:", key="collab_problem_input")
        if st.button("Analyze Problem", key="collab_define_btn") and problem:
            st.session_state['collab_problem'] = problem
            with st.spinner("Understanding the problem..."):
                prompt = (
                    f"A student from a rural/underserved community describes this problem: '{problem}'. "
                    f"As a facilitator:\n"
                    f"1. Restate the problem clearly in 2 sentences\n"
                    f"2. Identify the root cause (not just symptoms)\n"
                    f"3. List who is affected and how\n"
                    f"4. Ask 2 clarifying questions to understand better"
                )
                resp = generate_ai_response(prompt)
                if resp:
                    st.session_state['collab_history'].append(('define', resp))
                    st.session_state['collab_stage'] = 'research'
                    safe_rerun()

    elif st.session_state['collab_stage'] == 'research':
        if st.session_state['collab_history']:
            st.markdown(st.session_state['collab_history'][-1][1])
        if st.button("Research Solutions", key="collab_research_btn"):
            with st.spinner("Researching existing solutions..."):
                prompt = (
                    f"Problem: {st.session_state['collab_problem']}\n"
                    f"Research phase: Find 3-4 existing solutions to similar problems worldwide. "
                    f"For each: what was tried, did it work, what can we learn. "
                    f"Focus on low-cost, locally implementable approaches."
                )
                resp = generate_ai_response(prompt)
                if resp:
                    st.session_state['collab_history'].append(('research', resp))
                    st.session_state['collab_stage'] = 'ideate'
                    safe_rerun()

    elif st.session_state['collab_stage'] == 'ideate':
        if st.session_state['collab_history']:
            st.markdown(st.session_state['collab_history'][-1][1])
        user_ideas = st.text_area("Add your own solution ideas (optional):", key="collab_user_ideas")
        if st.button("Generate Combined Solutions", key="collab_ideate_btn"):
            with st.spinner("Brainstorming solutions..."):
                prompt = (
                    f"Problem: {st.session_state['collab_problem']}\n"
                    f"Student's ideas: {user_ideas or 'None provided'}\n"
                    f"Generate 4 creative, practical solutions. For each:\n"
                    f"- Name and 1-line description\n"
                    f"- Materials needed (locally available)\n"
                    f"- Estimated cost\n"
                    f"- Difficulty level (Easy/Medium/Hard)\n"
                    f"Rank them by feasibility."
                )
                resp = generate_ai_response(prompt)
                if resp:
                    st.session_state['collab_history'].append(('ideate', resp))
                    st.session_state['collab_stage'] = 'prototype'
                    safe_rerun()

    elif st.session_state['collab_stage'] == 'prototype':
        if st.session_state['collab_history']:
            st.markdown(st.session_state['collab_history'][-1][1])
        chosen = st.text_input("Which solution do you want to prototype? (type the name or number):", key="collab_chosen")
        if st.button("Create Prototype Plan", key="collab_proto_btn") and chosen:
            with st.spinner("Designing prototype..."):
                prompt = (
                    f"Problem: {st.session_state['collab_problem']}\n"
                    f"Chosen solution: {chosen}\n"
                    f"Create a simple prototype plan:\n"
                    f"1. Materials list with quantities\n"
                    f"2. Step-by-step build instructions (max 8 steps)\n"
                    f"3. How to test if it works\n"
                    f"4. Safety considerations\n"
                    f"Keep it achievable for a student with basic tools."
                )
                resp = generate_ai_response(prompt)
                if resp:
                    st.session_state['collab_history'].append(('prototype', resp))
                    st.session_state['collab_stage'] = 'plan'
                    safe_rerun()

    elif st.session_state['collab_stage'] == 'plan':
        if st.session_state['collab_history']:
            st.markdown(st.session_state['collab_history'][-1][1])
        if st.button("Generate Final Action Plan", key="collab_plan_btn"):
            with st.spinner("Creating action plan..."):
                prompt = (
                    f"Problem: {st.session_state['collab_problem']}\n"
                    f"Create a final action plan:\n"
                    f"- Week 1-2: Preparation tasks\n"
                    f"- Week 3-4: Build and test\n"
                    f"- Week 5-6: Deploy and gather feedback\n"
                    f"- Ongoing: Maintenance and improvement\n"
                    f"Include who to involve (school, panchayat, NGO, etc.) and how to present results."
                )
                resp = generate_ai_response(prompt)
                if resp:
                    st.session_state['collab_history'].append(('plan', resp))
                    st.markdown(resp)
                    # Compile full report
                    full_report = "\n\n---\n\n".join([f"## {stage_labels.get(s, s)}\n\n{content}" for s, content in st.session_state['collab_history']])
                    st.download_button(
                        "Download Full Project Report",
                        data=full_report.encode("utf-8"),
                        file_name="community_project_report.md",
                        mime="text/markdown",
                        key="dl_collab_report",
                    )

        if st.button("Start New Problem", key="collab_reset_btn"):
            st.session_state['collab_stage'] = 'define'
            st.session_state['collab_history'] = []
            st.session_state['collab_problem'] = ''
            safe_rerun()


def render_peer_learning_tab():
    """AI-Powered Peer Learning Groups — simulated for demo."""
    st.header("Peer Learning Groups")
    st.markdown(
        "In production, this feature clusters students by interests and creates collaborative groups. "
        "For this demo, the AI simulates a study group discussion on your chosen topic."
    )

    topic = st.text_input("What topic should the study group discuss?", key="peer_topic")
    group_size = st.slider("Simulated group size", 3, 6, 4, key="peer_size")

    if topic and st.button("Start Group Discussion", key="peer_btn"):
        with st.spinner("Simulating peer discussion..."):
            prompt = (
                f"Simulate a study group discussion between {group_size} students (with diverse backgrounds: "
                f"rural, urban, different skill levels) about '{topic}'. "
                f"Each student should:\n"
                f"1. Ask a unique question or share a perspective\n"
                f"2. Another student answers or builds on it\n"
                f"Show the natural flow of collaborative learning. "
                f"End with a facilitator summary of key insights.\n"
                f"Format each student's contribution with their name and background in bold."
            )
            resp = generate_ai_response(prompt)
            if resp:
                st.markdown(resp)

                with st.expander("What your group would learn together"):
                    takeaway_prompt = f"Based on a group discussion about '{topic}', list 5 key takeaways that students would gain from peer-to-peer learning vs solo study."
                    tr = generate_ai_response(takeaway_prompt)
                    if tr:
                        st.markdown(tr)


SUPPORTED_LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam",
    "Bengali", "Marathi", "Gujarati", "Urdu", "Odia", "Punjabi",
    "French", "Spanish", "Arabic"
]


def render_multilingual_controls():
    """Render language selector and translate-on-fly button.  Returns the chosen language."""
    lang = st.session_state.session.get('ui_language', 'English')
    chosen = st.selectbox(
        "Response language",
        SUPPORTED_LANGUAGES,
        index=SUPPORTED_LANGUAGES.index(lang) if lang in SUPPORTED_LANGUAGES else 0,
        key="lang_selector",
    )
    st.session_state.session['ui_language'] = chosen
    return chosen


def get_language_instruction() -> str:
    """Return a prompt prefix that tells the AI to respond in the user's chosen language."""
    lang = st.session_state.session.get('ui_language', 'English')
    if lang and lang != 'English':
        return f"IMPORTANT: Respond entirely in {lang}. Use {lang} script/characters. "
    return ""


def render_translate_button(text: str, key_suffix: str = ""):
    """Show a Translate button that re-generates the given text in the user's language."""
    lang = st.session_state.session.get('ui_language', 'English')
    if lang == 'English':
        return
    if st.button(f"Translate to {lang}", key=f"translate_{key_suffix}"):
        with st.spinner(f"Translating to {lang}..."):
            prompt = (
                f"Translate the following educational text to {lang}. "
                f"Preserve all formatting, headers, bullet points, and code blocks. "
                f"Only translate the natural language parts.\n\n{text[:6000]}"
            )
            resp = generate_ai_response(prompt)
            if resp:
                st.markdown(resp)


def render_streak_tracker():
    """Display a study streak tracker with visual calendar heatmap."""
    session = st.session_state.session
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Initialize streak data
    if 'streak_data' not in session:
        session['streak_data'] = {'dates': [], 'current_streak': 0, 'best_streak': 0}

    streak = session['streak_data']
    dates = streak.get('dates', [])

    # Record today's visit (once per day)
    if today_str not in dates:
        dates.append(today_str)
        # Recalculate current streak
        sorted_dates: list[str] = sorted(set(dates), reverse=True)
        current: int = 0
        for i, d in enumerate(sorted_dates):
            expected: str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            if d == expected:
                current += 1
            else:
                break
        streak['current_streak'] = current
        streak['best_streak'] = max(int(streak.get('best_streak', 0)), current)
        streak['dates'] = list(sorted_dates[:90])  # Keep last 90 days  # type: ignore[index]

    current_streak = streak.get('current_streak', 0)
    best_streak = streak.get('best_streak', 0)
    total_days = len(set(dates))

    # Streak display
    streak_color = '#238636' if current_streak >= 3 else '#d29922' if current_streak >= 1 else '#8b949e'
    st.markdown(
        f"<div style='display:flex; gap:24px; align-items:center; padding:12px 16px; "
        f"background:rgba(22,27,34,0.8); border:1px solid #30363d; border-radius:8px; margin-bottom:12px;'>"
        f"<div style='text-align:center;'>"
        f"<div style='font-size:28px; font-weight:700; color:{streak_color};'>{current_streak}</div>"
        f"<div style='font-size:11px; color:#8b949e;'>Day Streak</div></div>"
        f"<div style='text-align:center;'>"
        f"<div style='font-size:28px; font-weight:700; color:#58a6ff;'>{best_streak}</div>"
        f"<div style='font-size:11px; color:#8b949e;'>Best Streak</div></div>"
        f"<div style='text-align:center;'>"
        f"<div style='font-size:28px; font-weight:700; color:#c9d1d9;'>{total_days}</div>"
        f"<div style='font-size:11px; color:#8b949e;'>Total Days</div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Mini heatmap: last 28 days
    with st.expander("Activity heatmap (last 28 days)"):
        date_set = set(dates)
        cells = []
        for i in range(27, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            active = d in date_set
            color = '#238636' if active else '#161b22'
            border = '#30363d'
            cells.append(
                f"<div title='{d}' style='width:14px;height:14px;background:{color};"
                f"border:1px solid {border};border-radius:2px;'></div>"
            )
        row_html = "".join(cells)
        st.markdown(
            f"<div style='display:flex;flex-wrap:wrap;gap:3px;'>{row_html}</div>"
            f"<div style='font-size:11px;color:#8b949e;margin-top:6px;'>Green = active day</div>",
            unsafe_allow_html=True,
        )


def render_accessibility_controls():
    """Render accessibility settings: font size, contrast mode, text-to-speech."""
    with st.expander("Accessibility Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            font_size = st.select_slider(
                "Font size",
                options=["Small", "Normal", "Large", "Extra Large"],
                value=st.session_state.session.get('font_size', 'Normal'),
                key="acc_font_size",
            )
            st.session_state.session['font_size'] = font_size

        with col2:
            high_contrast = st.checkbox(
                "High contrast mode",
                value=st.session_state.session.get('high_contrast', False),
                key="acc_high_contrast",
            )
            st.session_state.session['high_contrast'] = high_contrast

        # Apply font size via injected CSS
        size_map = {"Small": "13px", "Normal": "15px", "Large": "18px", "Extra Large": "22px"}
        chosen_size = size_map.get(font_size, "15px")
        contrast_bg = "#000000" if high_contrast else ""
        contrast_text = "#ffffff" if high_contrast else ""
        contrast_border = "#ffffff" if high_contrast else ""

        inject_css = "<style>"
        inject_css += f"[data-testid='stAppViewContainer'] {{ font-size: {chosen_size} !important; }}"
        inject_css += f"p, li, span, div {{ font-size: {chosen_size} !important; }}"
        if high_contrast:
            inject_css += (
                f"[data-testid='stAppViewContainer'] {{ background: {contrast_bg} !important; color: {contrast_text} !important; }}"
                f".glass-card {{ background: #111 !important; border-color: {contrast_border} !important; }}"
                f"[data-testid='stSidebar'] {{ background: #000 !important; border-color: {contrast_border} !important; }}"
            )
        inject_css += "</style>"
        st.markdown(inject_css, unsafe_allow_html=True)

        # Text-to-Speech (browser-based)
        st.markdown("**Text-to-Speech**")
        tts_text = st.text_area("Paste text to hear it spoken:", height=80, key="tts_input")
        tts_lang_map = {
            "English": "en-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN",
            "Kannada": "kn-IN", "Malayalam": "ml-IN", "Bengali": "bn-IN", "Marathi": "mr-IN",
            "Gujarati": "gu-IN", "French": "fr-FR", "Spanish": "es-ES", "Arabic": "ar-SA",
        }
        ui_lang = st.session_state.session.get('ui_language', 'English')
        tts_lang = tts_lang_map.get(ui_lang, "en-IN")
        if st.button("Read Aloud", key="tts_btn") and tts_text:
            safe_text = tts_text.replace("'", "\\'").replace("\n", " ")[:1000]
            components.html(
                f"""<script>
                var u = new SpeechSynthesisUtterance('{safe_text}');
                u.lang = '{tts_lang}'; u.rate = 0.9;
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(u);
                </script><p style="color:#8b949e;font-size:12px;">Speaking...</p>""",
                height=30,
            )


def render_progress_report(paths: dict, uid: str):
    """Generate a downloadable AI-powered progress report."""
    st.subheader("Progress Report Generator")
    st.markdown("Generate a comprehensive progress report suitable for parents, teachers, or self-review.")

    if st.button("Generate Report", key="gen_report_btn", type="primary"):
        with st.spinner("Analyzing your learning journey..."):
            # Gather stats
            total_paths = len(paths)
            total_msgs = sum(len(p.get('chat_history', [])) for p in paths.values())
            topics = [p.get('current_topic', name) for name, p in paths.items()]
            badges = st.session_state.session.get('cached_badges') or compute_badges(uid, paths)
            xp = st.session_state.session.get('xp', 0)
            level = st.session_state.session.get('level', 1)
            streak = st.session_state.session.get('streak_data', {})
            current_streak = streak.get('current_streak', 0)
            best_streak = streak.get('best_streak', 0)
            total_days = len(set(streak.get('dates', [])))
            nickname = (st.session_state.session.get('user_info') or st.session_state.session.get('profile') or {}).get('nickname', 'Student')

            prompt = (
                f"Generate a professional, encouraging student progress report.\n\n"
                f"Student: {nickname}\n"
                f"Date: {datetime.now().strftime('%B %d, %Y')}\n\n"
                f"Stats:\n"
                f"- Learning paths explored: {total_paths}\n"
                f"- Topics studied: {', '.join(topics[:10])}\n"
                f"- Total interactions: {total_msgs}\n"
                f"- Level: {level} | XP: {xp}\n"
                f"- Badges earned: {', '.join(badges) if badges else 'None yet'}\n"
                f"- Study streak: {current_streak} days (best: {best_streak})\n"
                f"- Total active days: {total_days}\n\n"
                f"Include these sections:\n"
                f"1. Executive Summary (2-3 sentences)\n"
                f"2. Strengths Observed\n"
                f"3. Areas for Growth\n"
                f"4. Topics Covered (brief summary)\n"
                f"5. Engagement & Consistency\n"
                f"6. Recommendations for Next Steps\n"
                f"7. Note to Parents/Teachers\n\n"
                f"Use a warm, professional tone. Format with clear markdown headers."
            )
            resp = generate_ai_response(prompt)
            if resp:
                st.markdown(resp)

                # Build downloadable report
                report_header = (
                    f"# EduAI Progress Report\n"
                    f"**Student:** {nickname}  \n"
                    f"**Date:** {datetime.now().strftime('%B %d, %Y')}  \n"
                    f"**Level:** {level} | **XP:** {xp}  \n"
                    f"**Badges:** {', '.join(badges)}  \n"
                    f"**Study Streak:** {current_streak} days  \n\n---\n\n"
                )
                full_report = report_header + resp
                st.download_button(
                    "Download Report",
                    data=full_report.encode("utf-8"),
                    file_name=f"EduAI_Report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    key="dl_progress_report",
                )


def render_pomodoro_timer():
    """Browser-based Pomodoro study timer with sound notification."""
    with st.expander("Pomodoro Study Timer", expanded=False):
        st.markdown("Focus for 25 minutes, then take a 5-minute break. Repeat.")
        col1, col2, col3 = st.columns(3)
        with col1:
            work_mins = st.number_input("Work (min)", min_value=5, max_value=60, value=25, key="pomo_work")
        with col2:
            break_mins = st.number_input("Break (min)", min_value=1, max_value=30, value=5, key="pomo_break")
        with col3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            start = st.button("Start Timer", key="pomo_start_btn")

        if start:
            components.html(f"""
            <div id="pomo" style="font-family:'Inter',sans-serif;text-align:center;padding:16px;">
                <div id="pomo-label" style="color:#8b949e;font-size:13px;text-transform:uppercase;letter-spacing:1px;">Work Session</div>
                <div id="pomo-time" style="font-size:48px;font-weight:700;color:#58a6ff;margin:8px 0;">
                    {work_mins:02d}:00
                </div>
                <div id="pomo-bar-bg" style="width:100%;background:#21262d;border-radius:4px;height:6px;margin:8px 0;">
                    <div id="pomo-bar" style="width:100%;height:100%;background:#238636;border-radius:4px;transition:width 1s linear;"></div>
                </div>
                <button id="pomo-toggle" onclick="togglePomo()" style="
                    background:#da3633;color:#fff;border:none;border-radius:6px;
                    padding:6px 20px;font-size:14px;cursor:pointer;font-family:'Inter',sans-serif;
                ">Pause</button>
            </div>
            <script>
            (function(){{
                let workSec = {work_mins} * 60;
                let breakSec = {break_mins} * 60;
                let totalSec = workSec;
                let remaining = totalSec;
                let isWork = true;
                let paused = false;
                let timer = null;

                function fmt(s) {{
                    let m = Math.floor(s / 60);
                    let sec = s % 60;
                    return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
                }}

                function tick() {{
                    if (paused) return;
                    remaining--;
                    document.getElementById('pomo-time').innerText = fmt(remaining);
                    let pct = (remaining / totalSec) * 100;
                    document.getElementById('pomo-bar').style.width = pct + '%';
                    if (remaining <= 0) {{
                        clearInterval(timer);
                        // play beep
                        try {{
                            let ctx = new (window.AudioContext || window.webkitAudioContext)();
                            let osc = ctx.createOscillator();
                            osc.frequency.value = isWork ? 800 : 600;
                            osc.connect(ctx.destination);
                            osc.start(); setTimeout(()=>osc.stop(), 500);
                        }} catch(e) {{}}
                        if (isWork) {{
                            isWork = false;
                            totalSec = breakSec;
                            remaining = breakSec;
                            document.getElementById('pomo-label').innerText = 'Break Time';
                            document.getElementById('pomo-bar').style.background = '#d29922';
                        }} else {{
                            isWork = true;
                            totalSec = workSec;
                            remaining = workSec;
                            document.getElementById('pomo-label').innerText = 'Work Session';
                            document.getElementById('pomo-bar').style.background = '#238636';
                        }}
                        timer = setInterval(tick, 1000);
                    }}
                }}

                timer = setInterval(tick, 1000);

                window.togglePomo = function() {{
                    paused = !paused;
                    document.getElementById('pomo-toggle').innerText = paused ? 'Resume' : 'Pause';
                    document.getElementById('pomo-toggle').style.background = paused ? '#238636' : '#da3633';
                }};
            }})();
            </script>
            """, height=180)


# ── Main Application ──────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="EduAI", page_icon="🧠", layout="wide")
    init_session_state()
    load_css()

    if not st.session_state.session.get('loading_complete', False):
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
            <div class="loading-container">
                <div class="cyber-brain-container">
                    <svg class="cyber-brain-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                        <defs><linearGradient id="liquid-gradient" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color: #a275e3; stop-opacity: 1" /><stop offset="100%" style="stop-color: #ffffff; stop-opacity: 1" /></linearGradient></defs>
                        <path class="brain-outline" d="M50,5 C25,5 25,30 25,30 C10,30 10,50 10,50 C10,75 25,75 25,75 C25,95 50,95 50,95 C75,95 75,75 75,75 C90,75 90,50 90,50 C90,30 75,30 75,30 C75,5 50,5 50,5 Z"></path>
                        <path class="brain-veins" d="M50,5 C50,20 35,20 35,35 S50,50 50,50 S65,50 65,65 S50,80 50,80"></path><path class="brain-veins" d="M50,95 C50,80 35,80 35,65 S50,50 50,50 S65,50 65,35 S50,20 50,20"></path><path class="brain-veins" d="M25,30 C35,30 35,40 40,50 S60,60 60,70 S75,75 75,75"></path><path class="brain-veins" d="M10,50 C20,55 30,60 40,60 S60,55 70,50 S90,50 90,50"></path>
                    </svg>
                </div>
                <div class="loading-text">Booting Cognitive Core...</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.session['loading_complete'] = True
        safe_rerun()

    # If Firebase or the AI client failed to initialize, show warnings but allow the
    # login/guest UI to render so users can still access basic flows or see helpful messages.
    if not db or not client:
        if not db:
            st.warning("Firebase initialization failed or credentials missing. Some features (saving, avatars, quizzes) will be unavailable.")
        if not client:
            st.warning("AI model failed to initialize. Core generative features will be disabled until configured.")

    if not st.session_state.session['logged_in']:
        st.title("Welcome to Edu AI 🧠")
        with st.container(border=True):
            email = st.text_input("Email", key="email_input")
            password = st.text_input("Password", type="password", key="password_input")
            nickname = st.text_input("Nickname (optional)", key="nickname_input")
            c1, c2 = st.columns(2)
            if c1.button("Login", use_container_width=True, type="primary"):
                if email and password: login_user(email, password)
            if c2.button("Signup", use_container_width=True):
                if email and password: signup_user(email, password, nickname)
            if st.button("Navigate as Guest", use_container_width=True, key="navigate_guest_btn"):
                st.session_state.session['guest_mode'] = True
                if "Navigator" not in st.session_state.session['learning_paths']:
                    st.session_state.session['learning_paths']["Navigator"] = {'chat_history': [make_message("assistant", "Welcome! Ask anything.")], 'current_topic': 'Navigator'}
                st.session_state.session['active_path'] = "Navigator"
                safe_rerun()
            if (oauth_url := build_google_oauth_url()):
                st.link_button("Sign in with Google", oauth_url, use_container_width=True)
            if 'code' in st.query_params and oauth_url:
                try:
                    code_param = st.query_params.get('code', '')
                    tokens = exchange_code_for_tokens(code_param)
                    if idt := tokens.get('id_token'):
                        info = verify_id_token_and_get_userinfo(idt)
                        if info and info.get('email'):
                            g_email = info.get('email')
                            try: uid = auth.get_user_by_email(g_email).uid
                            except Exception: uid = auth.create_user(email=g_email, display_name=info.get('name')).uid
                            if db: db.collection('users').document(uid).set({'email': g_email, 'nickname': info.get('name'), 'avatar_path': info.get('picture'), 'tutor_persona': 'Friendly Encourager'}, merge=True)
                            st.session_state.session.update({'logged_in': True, 'user_info': {'uid': uid, 'email': g_email, 'nickname': info.get('name'), 'avatar_path': info.get('picture'), 'email_verified': info.get('email_verified', False), 'tutor_persona': 'Friendly Encourager'}})
                            st.query_params.clear(); st.success('Signed in with Google!'); safe_rerun()
                except Exception as e: st.error(f'Google OAuth failed: {e}')
    else: # User is logged in
        uid = st.session_state.session['user_info']['uid']
        st.session_state.session['learning_paths'] = get_user_paths(uid)
        user_info = st.session_state.session['user_info']

        # Compute badges once per render and cache them
        st.session_state.session['cached_badges'] = compute_badges(uid, st.session_state.session['learning_paths'])

        # Sanitize any stored messages that accidentally contain raw CSS/code so they don't render
        try:
            sanitize_session_messages()
        except Exception:
            pass

        # Onboarding flow
        if not st.session_state.session.get('onboarding_complete', False):
            # Initialize guidance chat history if it's the first time for this session
            if 'guidance_chat_history' not in st.session_state:
                st.session_state.guidance_chat_history = []
                add_guidance_message("model", 
                                     "Welcome to Edu AI! I can help you find your perfect learning path. "
                                     "Would you like my guidance, or do you prefer to explore on your own?")
                st.session_state.guidance_stage = 'initial_choice'
            
            # Display the onboarding dialog (use compatibility wrapper)
            with maybe_dialog("Your Learning Journey Starts Here"):
                st.markdown("### Welcome to Edu AI!")
                st.markdown("Would you like me to help you find your ideal learning path, or do you prefer to explore the features yourself?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Get AI Guidance", use_container_width=True, key="get_ai_guidance_dialog"):
                        st.session_state.session['guidance_choice'] = 'guided'
                        # Keep onboarding_complete as False to ensure dialog stays open for chat
                        st.session_state.guidance_stage = 'start_questions'
                        safe_rerun()
                with col2:
                    if st.button("Explore Myself", use_container_width=True, key="explore_myself_dialog"):
                        st.session_state.session['guidance_choice'] = 'self_explore'
                        st.session_state.session['onboarding_complete'] = True
                        st.success("Welcome! You can always generate paths from the sidebar.")
                        time.sleep(1)
                        safe_rerun()
                
                if st.session_state.session.get('guidance_choice') == 'guided':
                    st.markdown("---")
                    render_guidance_chat() # Render the guidance chat here
                    
                    if st.session_state.get('guidance_stage') == 'confirm_path' and st.session_state.get('generated_guidance_topics'):
                        st.markdown("---")
                        st.markdown("**Your Proposed Path:**")
                        for i, t in enumerate(st.session_state.generated_guidance_topics, 1):
                            st.write(f"- {t}")
                        
                        col_accept, col_refine = st.columns(2)
                        with col_accept:
                            if st.button("Accept Path & Start Learning", use_container_width=True, key="accept_guidance_path_dialog"):
                                ai_goal_for_name = st.session_state.guidance_chat_history[1]["content"] if len(st.session_state.guidance_chat_history) > 1 else "AI Guided Path"
                                base_name = ai_goal_for_name[:30].strip() or "AI Guided Path"
                                final_name = base_name
                                idx = 1
                                while final_name in st.session_state.session.get('learning_paths', {}):
                                    final_name = f"{base_name} ({idx})"
                                    idx += 1

                                new_path_data = {
                                    'chat_history': [], 
                                    'current_topic': st.session_state.generated_guidance_topics[0] if st.session_state.generated_guidance_topics else "Introduction",
                                    'topics': st.session_state.generated_guidance_topics
                                }
                                if uid and db:
                                    save_learning_path(uid, final_name, new_path_data)
                                st.session_state.session.setdefault('learning_paths', {})[final_name] = new_path_data
                                
                                st.session_state.session['onboarding_complete'] = True
                                st.session_state.guidance_choice = None
                                st.success(f"Path '{final_name}' created! Redirecting...")
                                time.sleep(1)
                                safe_rerun()
                        with col_refine:
                            if st.button("Refine Path", use_container_width=True, key="refine_guidance_path_dialog"):
                                add_guidance_message("user", "I'd like to refine the path.")
                                st.session_state.guidance_stage = 'collecting_info'
                                safe_rerun()
                st.stop()

        paths = st.session_state.session['learning_paths']
        
        # Quick Home anchor link
        try:
            if st.session_state.session.get('loading_complete', False):
                # Anchor link adds ?home=1 to the URL when clicked. We detect that below and act.
                st.markdown("<div class='quick-home-wrapper'><a href='?home=1' class='quick-home-link'>🏠 Home</a></div>", unsafe_allow_html=True)
                # If the user clicked the quick-home link, handle it and clear the query param
                q = st.query_params
                if 'home' in q:
                    st.session_state.session['active_path'] = None
                    st.session_state.session['current_quiz_data'] = None
                    st.session_state.session['page'] = 'Home'
                    # Clear query params to avoid repeat handling
                    try:
                        st.query_params.clear()
                    except Exception:
                        pass
                    safe_rerun()
        except Exception:
            pass

        def _safe_key(s: str) -> str:
            """Generate a stable widget key from an arbitrary string."""
            h = hashlib.sha1(s.encode('utf-8')).hexdigest()[:8]
            safe = re.sub(r'[^0-9a-zA-Z_-]', '_', s)[:20]
            return f"{safe}_{h}"

        # Response style prompts — shared across sidebar tools and home chat
        style_instructions = {
            'Default': '',
            'Simple explanation': 'Please give a concise, beginner-friendly explanation suitable for someone new to the topic.',
            'Code example': 'Provide a concise, runnable code example in Python (when applicable). Wrap code in triple backticks.',
            'Real-world analogy': 'Explain the concept using a clear real-world analogy that maps to the technical idea.',
        }

        with st.sidebar:
            tab_profile, tab_paths, tab_tools = st.tabs(["👤 Profile", "🧠 Paths", "🛠️ Tools"])

            with tab_profile:
                # Sanitize displayed profile fields
                raw_user_title = user_info.get('nickname') or user_info.get('email')
                raw_persona = user_info.get('tutor_persona', '')
                user_title = re.sub(r'<[^>]+>', '', str(raw_user_title or '')).strip()
                persona_short = re.sub(r'<[^>]+>', '', str(raw_persona or '')).strip()
                avatar_html = ""
                if avatar_path := user_info.get('avatar_path'):
                    avatar_html = f"<img src='{avatar_path}' width='48' style='border-radius:8px; margin-right:8px;'/>"
                header_html = textwrap.dedent(f"""
                <div style='display:flex; align-items:center; gap:10px;'>
                    {avatar_html}
                    <div style='line-height:1.0'>
                        <div style='font-weight:700; font-size:16px'>{user_title}</div>
                        <div style='font-size:12px; color:#cfcfe8'>{persona_short}</div>
                    </div>
                </div>
                """)
                header_html = header_html.lstrip('\n')
                try:
                    components.html(header_html, height=72)
                except Exception:
                    st.markdown(header_html, unsafe_allow_html=True)

                # Profile Manager
                with st.expander("Manage Profile", expanded=False):
                    current_nick = user_info.get('nickname', '')
                    new_nick = st.text_input("Nickname", value=current_nick, key="nick_input")
                    if CROP_SUPPORT:
                        if uploaded_file := st.file_uploader("Choose image to crop", type=["png", "jpg", "jpeg"], key="crop_upload"):
                            try:
                                cropped_img = st_cropper(uploaded_file, realtime_update=False, box_color="#0000FF")
                                if saved_path := save_avatar_file(uid, cropped_img):
                                    if db: db.collection('users').document(uid).set({'avatar_path': saved_path}, merge=True)
                                    st.session_state.session['user_info']['avatar_path'] = saved_path
                                    st.success("Avatar updated.")
                            except Exception as e: st.error(f"Cropper failed: {e}")
                    else:
                        if uploaded_avatar := st.file_uploader("Upload avatar", type=["png", "jpg", "jpeg"], key="avatar_upload"):
                            if saved_path := save_avatar_file(uid, uploaded_avatar):
                                if db: db.collection('users').document(uid).set({'avatar_path': saved_path}, merge=True)
                                st.session_state.session['user_info']['avatar_path'] = saved_path
                                st.success("Avatar updated.")
                    
                    personas = ["Friendly Encourager", "Strict Professor", "Socratic Questioner", "Concise Technician", "Creative Storyteller"]
                    current_persona = user_info.get('tutor_persona', personas[0])
                    new_persona = st.selectbox("Tutor Persona:", personas, index=personas.index(current_persona) if current_persona in personas else 0, key="persona_select")
                    
                    if st.button("Save Profile", key="save_profile_btn"):
                        valid, msg = validate_nickname(new_nick)
                        if not valid: st.error(msg)
                        else:
                            try: auth.update_user(uid, display_name=new_nick)
                            except Exception: st.warning("Could not update Auth display name.")
                            if db:
                                try:
                                    db.collection('users').document(uid).set({'nickname': new_nick, 'tutor_persona': new_persona}, merge=True)
                                    st.session_state.session['user_info'].update({'nickname': new_nick, 'tutor_persona': new_persona})
                                    st.success("Profile updated.")
                                except Exception: st.error("Failed to save profile.")
                    
                    if not user_info.get('email_verified'):
                        if st.button("Resend verification email", key="resend_verif_btn"):
                            try:
                                link = auth.generate_email_verification_link(user_info.get('email'))
                                st.success("Verification link generated."); st.markdown(f"[{link}]({link})")
                            except Exception as e: st.error(f"Failed to generate link: {e}")

                # Badges and verification
                # Use cached badges to avoid redundant Firestore queries
                if 'cached_badges' not in st.session_state.session:
                    st.session_state.session['cached_badges'] = compute_badges(uid, paths)
                if badges := st.session_state.session['cached_badges']:
                    badge_styles = {
                        'Explorer': {'color': '#6a4fa8', 'emoji': '🧭'},
                        'Active Learner': {'color': '#a275e3', 'emoji': '🔥'},
                        'Quizzer': {'color': '#16a34a', 'emoji': '📝'}
                    }
                    cols = st.columns(len(badges)) if badges else []
                    for i, b in enumerate(badges):
                        style = badge_styles.get(b, {'color': '#2b2340', 'emoji': '🏅'})
                        key = f"badge_{b}"
                        label = f"{style['emoji']} {b}"
                        if cols:
                            if cols[i].button(label, key=key):
                                current = st.session_state.session.get('badge_filter')
                                if current == b:
                                    st.session_state.session['badge_filter'] = None
                                else:
                                    st.session_state.session['badge_filter'] = b
                                safe_rerun()
                            else:
                                chip_html = f"<div style='display:inline-block; margin:2px 4px; background:{style['color']}; color:#fff; padding:6px 10px; border-radius:999px; font-size:12px;'>{label}</div>"
                                st.markdown(chip_html, unsafe_allow_html=True)
                verified = user_info.get('email_verified', False)
                st.markdown(f"<div style='margin-top:6px'><span class='status-badge {'status-verified' if verified else 'status-unverified'}'>{'✅ Verified' if verified else '⚠️ Unverified'}</span></div>", unsafe_allow_html=True)
                if st.button("↻ Refresh verification", key="refresh_verif_btn"):
                    try:
                        st.session_state.session['user_info']['email_verified'] = auth.get_user(uid).email_verified
                        safe_rerun()
                    except Exception: st.error("Failed to refresh status.")

               

            with tab_paths:
                st.header("My Learning Paths")
                paths = st.session_state.session.get('learning_paths', {})

                # Display existing paths as safe-keyed buttons
                for path_name in sorted(paths.keys()):
                    key = _safe_key(f"path_btn::{path_name}")
                    if st.button(path_name, use_container_width=True, key=key):
                        st.session_state.session['active_path'] = path_name
                        st.session_state.session['current_quiz_data'] = None
                        st.session_state.session['page'] = 'Home'
                        st.rerun()

                st.markdown("---")

                # Manual path creation
                with st.form("new_path_form"):
                    new_path_name = st.text_input("New Manual Path Name (e.g., Python Basics)").strip()
                    submitted_manual = st.form_submit_button("Create Manual Path")
                    if submitted_manual:
                        if not new_path_name:
                            st.warning("Please enter a valid path name.")
                        elif new_path_name in paths:
                            st.warning("Path name already exists.")
                        else:
                            new_path_data = {'chat_history': [], 'current_topic': "Introduction", 'topics': ["Introduction"]}
                            if uid:
                                save_learning_path(uid, new_path_name, new_path_data)
                            # Update session immediately so UI reflects change
                            st.session_state.session.setdefault('learning_paths', {})[new_path_name] = new_path_data
                            st.success(f"Path '{new_path_name}' created!")
                            st.rerun()

                st.markdown("---")

                # AI-generated path generation with preview
                with st.expander("Generate Path with AI"):
                    with st.form("ai_path_form"):
                        ai_goal = st.text_input("What is your learning goal?", placeholder="e.g., Become a Web Developer").strip()
                        submitted_ai = st.form_submit_button("Generate Path")
                        if submitted_ai:
                            if not ai_goal:
                                st.warning("Please enter a learning goal.")
                            else:
                                prompt = (
                                    f"Based on the learning goal '{ai_goal}', generate a logical learning path consisting of 5-7 distinct topic names. "
                                    "Respond ONLY with a JSON list of strings. Example: [\"HTML Basics\", \"CSS Fundamentals\", ...]"
                                )
                                topic_list_text = generate_ai_response(prompt, is_json=True)
                                topics = parse_topic_list(topic_list_text)
                                if not topics:
                                    st.error("AI failed to generate a valid list. Try a clearer goal or try again.")
                                else:
                                    st.markdown("**Generated Topics:**")
                                    for i, t in enumerate(topics, start=1):
                                        st.write(f"{i}. {t}")
                                    base_name = ai_goal[:30].strip() or "AI Path"
                                    final_name = base_name
                                    idx = 1
                                    while final_name in st.session_state.session.get('learning_paths', {}):
                                        final_name = f"{base_name} ({idx})"
                                        idx += 1
                                    # Auto-create the path (only one submit button allowed per form)
                                    new_path_data = {'chat_history': [], 'current_topic': topics[0] if topics else "Introduction", 'topics': topics}
                                    if uid:
                                        save_learning_path(uid, final_name, new_path_data)
                                    st.session_state.session.setdefault('learning_paths', {})[final_name] = new_path_data
                                    st.success(f"AI generated path '{final_name}' with {len(topics)} topics!")
                                    st.rerun()

            with tab_tools:
                # Quick Actions
                st.subheader("Quick Actions")
                qa_cols = st.columns(2)
                # Home button: immediately return to default Home Chat
                if qa_cols[0].button("Home", key="qa_home"):
                    st.session_state.session['active_path'] = None
                    st.session_state.session['page'] = 'Home'
                    # also clear quick_action to avoid accidental actions
                    st.session_state.session['quick_action'] = None
                    safe_rerun()

                if qa_cols[0].button("Learn", key="qa_learn"):
                    # Open a small dialog so Learn works from any page
                    with maybe_dialog("Quick Learn"):
                        topic = st.text_input("What topic do you want to learn?", key="dlg_quick_learn_topic")
                        if st.button("Start Quick Learn", key="dlg_start_quick_learn"):
                            if not topic:
                                st.warning("Please enter a topic.")
                            else:
                                hp_name = "Quick Learn"
                                if hp_name not in paths:
                                    paths[hp_name] = {'chat_history': [], 'current_topic': topic}
                                paths[hp_name]['chat_history'].append(make_message('user', f"Explain '{topic}' to me."))
                                sel_style = st.session_state.get('home_response_style', 'Default')
                                instr = style_instructions.get(sel_style, '')
                                prompt = f"{instr}\nExplain the topic '{topic}'."
                                if resp := generate_ai_response(prompt):
                                    paths[hp_name]['chat_history'].append(make_message('assistant', resp, generation_params={'style': sel_style}))
                                if db and uid: save_learning_path(uid, hp_name, paths[hp_name])
                                st.session_state.session['active_path'] = hp_name
                                safe_rerun()

                if qa_cols[1].button("Quiz", key="qa_quiz"):
                    with maybe_dialog("Quick Quiz"):
                        topic = st.text_input("What topic do you want to quiz on?", key="dlg_quick_quiz_topic")
                        if st.button("Generate Quiz", key="dlg_generate_quiz"):
                            if not topic:
                                st.warning("Please enter a topic.")
                            else:
                                quiz_example = '[{"question": "...", "options": ["...", "...", "..."], "answer": "..."}, ...]'
                                prompt = f"Create a 3-question multiple choice quiz for '{topic}'. Respond ONLY with a JSON array of objects. Example format: {quiz_example}"
                                if resp := generate_ai_response(prompt, is_json=True):
                                    if quiz_list := parse_multi_quiz(resp):
                                        st.session_state.session['current_quiz_data'] = {'questions': quiz_list}
                                        hp_name = "Quick Quiz"
                                        if hp_name not in paths:
                                            paths[hp_name] = {'chat_history': [], 'current_topic': topic}
                                        st.session_state.session['active_path'] = hp_name
                                        safe_rerun()
                                    else:
                                        st.error("AI returned an invalid quiz format. Please try again.")

                if qa_cols[0].button("Resources", key="qa_resources"):
                    with maybe_dialog("Quick Resources"):
                        topic = st.text_input("What topic do you want resources for?", key="dlg_quick_resources_topic")
                        if st.button("Get Resources", key="dlg_get_resources"):
                            if not topic:
                                st.warning("Please enter a topic.")
                            else:
                                sel_style = st.session_state.get('home_response_style', 'Default')
                                instr = style_instructions.get(sel_style, '')
                                prompt = f"{instr}\nSuggest 3 high-quality online resources for learning about '{topic}'."
                                if resp := generate_ai_response(prompt):
                                    st.success(resp)
                if qa_cols[1].button("Review", key="qa_review"):
                    st.session_state.session['review_session_active'] = True
                    st.session_state.session['active_path'] = None
                    st.session_state.session['page'] = 'Home'
                    safe_rerun()

                # Recent activity
                st.markdown("---")
                st.subheader("Recent Activity")
                recent_items: list[dict] = [{'path': name, 'role': msg.get('role'), 'content': msg.get('content'), 'timestamp': msg.get('timestamp', 0)}
                                for name, data in paths.items() for msg in data.get('chat_history', [])]
                sorted_recent: list[dict] = sorted(recent_items, key=lambda x: x['timestamp'], reverse=True)
                for item in sorted_recent[:5]:  # type: ignore[index]
                    ts = datetime.fromtimestamp(item['timestamp']).strftime('%b %d %H:%M') if item.get('timestamp') else ''
                    icon = '💬' if item['role'] == 'user' else '🤖'
                    snippet = html.escape((item.get('content') or '')[:70])
                    st.markdown(f"<div style='font-size:13px; color:#c9d1d9'>{icon} <strong>[{item['path']}]</strong> {snippet} <span style='color:#8b949e; font-size:11px'> {ts}</span></div>", unsafe_allow_html=True)

            # Logout at the bottom
            st.markdown("---")
            if st.button("Logout", use_container_width=True, key="logout_btn"):
                for k in ['guidance_chat_history', 'guidance_stage', 'generated_guidance_topics']:
                    st.session_state.pop(k, None)
                st.session_state.clear()
                safe_rerun()

        active_path_name = st.session_state.session.get('active_path')
        if not active_path_name:
            if st.session_state.session.get('review_session_active'):
                render_srs_view(uid)
            else:
                # Global Search
                search_query = st.text_input("🔍 Search Paths", placeholder="Search paths and topics...", key="global_search")
                st.session_state.session['search_query'] = search_query

                tab_home, tab_vision, tab_feynman, tab_social, tab_career, tab_summarizer, tab_collab, tab_peer, tab_paths_tab, tab_dashboard, tab_settings = st.tabs(["Home", "Vision", "Feynman Board", "Social Impact", "Career Path", "Summarizer", "Collaborative", "Peer Learning", "Paths", "Dashboard", "Settings"])

                with tab_vision:
                    st.session_state.session['used_vision'] = True
                    render_vision_tab()

                with tab_feynman:
                    st.session_state.session['used_feynman'] = True
                    render_feynman_tab()
                
                with tab_social:
                    st.session_state.session['used_social_impact'] = True
                    render_social_impact_tab()

                with tab_career:
                    st.session_state.session['used_career_path'] = True
                    render_career_path_tab()

                with tab_summarizer:
                    st.session_state.session['used_summarizer'] = True
                    render_summarizer_tab()

                with tab_collab:
                    st.session_state.session['used_collab_solver'] = True
                    render_collaborative_problem_tab()

                with tab_peer:
                    render_peer_learning_tab()

                with tab_home:
                    # Context-Aware Greeting
                    render_context_aware_greeting()

                    # Gamification bar
                    xp = st.session_state.session.get('xp', 0)
                    level = st.session_state.session.get('level', 1)
                    xp_thresholds = [0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500]
                    next_threshold = xp_thresholds[min(level, len(xp_thresholds) - 1)]
                    prev_threshold = xp_thresholds[min(level - 1, len(xp_thresholds) - 1)]
                    progress_pct = min(1.0, (xp - prev_threshold) / max(1, next_threshold - prev_threshold))
                    st.markdown(
                        f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'>"
                        f"<span style='color:#58a6ff; font-weight:600; font-size:14px;'>Level {level}</span>"
                        f"<div style='flex:1; background:#21262d; border-radius:4px; height:8px; overflow:hidden;'>"
                        f"<div style='width:{progress_pct*100:.0f}%; height:100%; background:linear-gradient(90deg,#238636,#58a6ff); border-radius:4px;'></div>"
                        f"</div>"
                        f"<span style='color:#8b949e; font-size:12px;'>{xp} XP</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    # Streak tracker
                    render_streak_tracker()

                    st.header("Home Chat")

                    # Accessibility controls + Voice input + Pomodoro
                    acc_col, voice_col, pomo_col = st.columns(3)
                    with acc_col:
                        render_accessibility_controls()
                    with voice_col:
                        with st.expander("Voice Input", expanded=False):
                            render_voice_input_component()
                            st.caption("Speak, then paste from clipboard.")
                    with pomo_col:
                        render_pomodoro_timer()

                    # Allow the user to select a response "style" that will be applied to AI replies
                    style_options = ["Default", "Simple explanation", "Code example", "Real-world analogy"]
                    if 'home_response_style' not in st.session_state:
                        st.session_state['home_response_style'] = 'Default'

                    col_style, col_lang, col_quick = st.columns([2, 2, 4])
                    with col_style:
                        chosen_style = st.selectbox("Response style:", style_options, index=style_options.index(st.session_state.get('home_response_style', 'Default')), key='home_style_select')
                        st.session_state['home_response_style'] = chosen_style
                    with col_lang:
                        render_multilingual_controls()
                    with col_quick:
                        b1, b2, b3 = st.columns(3)
                        if b1.button("Simple"):
                            st.session_state['home_response_style'] = 'Simple explanation'
                            chosen_style = 'Simple explanation'
                        if b2.button("Code"):
                            st.session_state['home_response_style'] = 'Code example'
                            chosen_style = 'Code example'
                        if b3.button("Analogy"):
                            st.session_state['home_response_style'] = 'Real-world analogy'
                            chosen_style = 'Real-world analogy'

                    # Transfer any sidebar tool_focus into the durable quick_action key
                    if 'tool_focus' in st.session_state:
                        try:
                            st.session_state.session['quick_action'] = st.session_state.pop('tool_focus')
                        except Exception:
                            pass

                    # Handle quick actions (respect the selected style where applicable)
                    quick_action = st.session_state.session.get('quick_action')
                    if quick_action == 'learn':
                        st.session_state.session['quick_action'] = None
                        topic = st.text_input("What topic do you want to learn?", key="quick_learn_topic")
                        if topic:
                            hp_name = "Quick Learn"
                            if hp_name not in paths:
                                paths[hp_name] = {'chat_history': [], 'current_topic': topic}
                            paths[hp_name]['chat_history'].append(make_message('user', f"Explain '{topic}' to me."))
                            sel_style = st.session_state.get('home_response_style', 'Default')
                            instr = style_instructions.get(sel_style, '')
                            prompt = f"{instr}\nExplain the topic '{topic}'."
                            if resp := generate_ai_response(prompt):
                                paths[hp_name]['chat_history'].append(make_message('assistant', resp, generation_params={'style': sel_style}))
                            if db and uid: save_learning_path(uid, hp_name, paths[hp_name])
                            st.session_state.session['active_path'] = hp_name
                            safe_rerun()
                    elif quick_action == 'quiz':
                        st.session_state.session['quick_action'] = None
                        topic = st.text_input("What topic do you want to quiz on?", key="quick_quiz_topic")
                        if topic:
                            quiz_example = '[{"question": "...", "options": ["...", "...", "..."], "answer": "..."}, ...]'
                            prompt = f"Create a 3-question multiple choice quiz for '{topic}'. Respond ONLY with a JSON array of objects. Example format: {quiz_example}"
                            if resp := generate_ai_response(prompt, is_json=True):
                                if quiz_list := parse_multi_quiz(resp):
                                    st.session_state.session['current_quiz_data'] = {'questions': quiz_list}
                                    hp_name = "Quick Quiz"
                                    if hp_name not in paths:
                                        paths[hp_name] = {'chat_history': [], 'current_topic': topic}
                                    st.session_state.session['active_path'] = hp_name
                                    safe_rerun()
                    elif quick_action == 'resources':
                        st.session_state.session['quick_action'] = None
                        topic = st.text_input("What topic do you want resources for?", key="quick_resources_topic")
                        if topic:
                            sel_style = st.session_state.get('home_response_style', 'Default')
                            instr = style_instructions.get(sel_style, '')
                            prompt = f"{instr}\nSuggest 3 high-quality online resources for learning about '{topic}'."
                            if resp := generate_ai_response(prompt):
                                st.success(resp)
                    elif quick_action == 'review':
                        st.session_state.session['quick_action'] = None
                        st.session_state.session['review_session_active'] = True
                        safe_rerun()
                    else:
                        # Normal home chat
                        if 'home_chat' not in st.session_state.session:
                            st.session_state.session['home_chat'] = []
                        home_chat = st.session_state.session['home_chat']
                        for message in home_chat:
                            with st.chat_message(message["role"]):
                                st.markdown(message["content"])

                        # Chat input area - style selection is above and will be applied to responses
                        if prompt := st.chat_input("Ask anything..."):
                            home_chat.append(make_message("user", prompt))
                            sel_style = st.session_state.get('home_response_style', 'Default')
                            instr = style_instructions.get(sel_style, '')

                            # Emotional Intelligence: detect mood and adapt response
                            emotion_prefix = detect_emotion_and_adapt(prompt)

                            # Multilingual support
                            lang_instr = get_language_instruction()

                            full_prompt = f"{lang_instr}{emotion_prefix}{instr}\nAnswer the following question concisely:\n{prompt}"
                            if resp := generate_ai_response(full_prompt):
                                home_chat.append(make_message("assistant", resp, generation_params={'style': sel_style}))
                                # Persist a short copy to the DB if available
                                if db and uid:
                                    save_learning_path(uid, 'Home Chat', {'chat_history': home_chat, 'current_topic': 'Home'})
                                safe_rerun()

                with tab_paths_tab:
                    st.header("Your Learning Paths")
                    st.markdown("---")
                    if not paths:
                        st.info("No learning paths yet. Create one from the sidebar on the left.")
                    else:
                        for pname, pdata in paths.items():
                            col1, col2, col3 = st.columns([4, 2, 4])
                            with col1:
                                st.markdown(f"**{pname}**")
                                st.caption(pdata.get('current_topic', ''))
                                if tags := pdata.get('tags'):
                                    st.write(', '.join(tags))
                            with col2:
                                if st.button("Learn", key=f"open_{pname}"):
                                    st.session_state.session['active_path'] = pname
                                    st.session_state.session['current_quiz_data'] = None
                                    safe_rerun()
                                if st.button("Quiz", key=f"quiz_{pname}"):
                                    topic = pdata.get('current_topic') or pname
                                    prompt = f"Create a 3-question multiple choice quiz for '{topic}'. Respond ONLY with a JSON array of objects: [{'question': '...', 'options': ['...'], 'answer': '...'}, ...]"
                                    if resp := generate_ai_response(prompt, is_json=True):
                                        if quiz_list := parse_multi_quiz(resp):
                                            st.session_state.session['current_quiz_data'] = {'questions': quiz_list}
                                            st.session_state.session['active_path'] = pname
                                            safe_rerun()
                            with col3:
                                if st.button("Doubt", key=f"doubt_{pname}"):
                                    pdata.setdefault('chat_history', []).append(make_message('user', 'I have a doubt. Please help.'))
                                    if db and uid: save_learning_path(uid, pname, pdata)
                                    st.session_state.session['active_path'] = pname
                                    safe_rerun()
                                if st.button("Certs", key=f"certs_{pname}"):
                                    topic = pdata.get('current_topic') or pname
                                    prompt = f"As an AI tutor, list 2-3 professional certifications or certificates relevant to '{topic}' with short notes."
                                    if resp := generate_ai_response(prompt):
                                        st.success(resp)

                with tab_dashboard:
                    # Gamification Stats Header
                    xp = st.session_state.session.get('xp', 0)
                    level = st.session_state.session.get('level', 1)
                    user_badges = st.session_state.session.get('cached_badges') or compute_badges(uid or '', paths)
                    dash_cols = st.columns(4)
                    dash_cols[0].metric("Level", level)
                    dash_cols[1].metric("XP", f"{xp:,}")
                    dash_cols[2].metric("Badges", len(user_badges))
                    dash_cols[3].metric("Paths", len(paths))

                    if user_badges:
                        badge_html = " ".join(
                            f"<span style='display:inline-block; background:#21262d; border:1px solid #30363d; "
                            f"border-radius:12px; padding:4px 12px; font-size:12px; color:#58a6ff; "
                            f"margin:2px 4px;'>{b}</span>"
                            for b in user_badges
                        )
                        st.markdown(f"<div style='margin:8px 0 16px;'>{badge_html}</div>", unsafe_allow_html=True)

                    st.markdown("---")

                    # Progress Report
                    render_progress_report(paths, uid or '')

                    st.markdown("---")
                    st.title("Select or Create a Learning Path")
                    st.info("Choose a path from the Knowledge Graph or create a new one to begin.")
                    render_dashboard(paths, search_query, uid)
                    render_srs_dashboard(uid)
                    st.markdown("---")
                    st.header("Quick Start: Ask the Navigator")
                    if homepage_topic := st.text_input("What would you like to learn today?", key="homepage_topic"):
                        hp_name = "Homepage Chat"
                        if hp_name not in paths:
                            paths[hp_name] = {'chat_history': [], 'current_topic': homepage_topic}
                        paths[hp_name]['chat_history'].append(make_message('user', homepage_topic))
                        prompt = f"Explain the topic '{homepage_topic}' simply."
                        if resp := generate_ai_response(prompt):
                            paths[hp_name]['chat_history'].append(make_message('assistant', resp))
                        if db and uid: save_learning_path(uid, hp_name, paths[hp_name])
                        st.session_state.session['active_path'] = hp_name
                        safe_rerun()

                with tab_settings:
                    st.header("Settings")
                    st.markdown("Manage app preferences and cleanup utilities.")

                    # Safe rendering toggle: when enabled we escape persisted snippets before display
                    if 'settings_safe_rendering' not in st.session_state:
                        st.session_state['settings_safe_rendering'] = True
                    st.checkbox("Enable safe rendering (escape persisted content before display)", value=st.session_state.get('settings_safe_rendering', True), key='settings_safe_rendering')

                    st.markdown("---")
                    st.subheader("AI Model")
                    st.info(f"🤖 Using **Gemini** (`{GEMINI_MODEL}`) with key rotation ({len(client.keys_data.get('keys', []))} keys available)" if client else "⚠️ Gemini client not initialized.")

                    st.markdown("---")
                    st.subheader("Cleanup Tools")

                    # In-memory sanitizer: removes suspicious HTML/CSS-like messages from session_state
                    if st.button("Run in-memory sanitizer now", key="run_inmemory_sanitizer"):
                        def _count_offenders_in_session() -> int:
                            cnt: int = 0
                            ss: dict = st.session_state.session if isinstance(st.session_state.get('session'), dict) else {}
                            # home_chat
                            for m in list(ss.get('home_chat', []) or []):
                                if _looks_like_css_block(m.get('content', '')): cnt += 1  # type: ignore[operator]
                            # guidance
                            for m in list(st.session_state.get('guidance_chat_history') or []):
                                if _looks_like_css_block(m.get('content', '')): cnt += 1  # type: ignore[operator]
                            # learning paths
                            for pname, pdata in dict(ss.get('learning_paths') or {}).items():
                                for m in list(pdata.get('chat_history', []) or []):
                                    if _looks_like_css_block(m.get('content', '')): cnt += 1  # type: ignore[operator]
                            return cnt

                        before = _count_offenders_in_session()
                        sanitize_session_messages()
                        after = _count_offenders_in_session()
                        removed = max(0, before - after)
                        st.success(f"Sanitizer completed. Removed {removed} offending message(s) from session state.")

                    # Preview persisted HTML/CSS-like content in learning_paths (reads from session and Firestore if available)
                    if st.button("Preview persisted HTML/CSS in learning paths", key="preview_persisted_offenders"):
                        preview = {}
                        # Scan session-state copy of learning_paths first
                        for pname, pdata in (st.session_state.session.get('learning_paths') or {}).items():
                            offenders = []
                            for i, m in enumerate(pdata.get('chat_history', []) or []):
                                if _looks_like_css_block(m.get('content', '')):
                                    offenders.append({'index': i, 'snippet': (m.get('content') or '')[:200]})
                            if offenders:
                                preview[pname] = offenders

                        # If Firestore is available, attempt to read the authoritative stored document for the user
                        if db:
                            try:
                                doc = db.collection('learning_paths').document(uid).get()
                                if doc.exists:
                                    lp = doc.to_dict() or {}
                                    for pname, pdata in lp.items():
                                        offenders = []
                                        for i, m in enumerate(list(pdata.get('chat_history') or [])[:50]):  # type: ignore[index]
                                            if _looks_like_css_block(m.get('content', '')):
                                                offenders.append({'index': i, 'snippet': (m.get('content') or '')[:200]})
                                        if offenders:
                                            preview.setdefault(pname, []).extend(offenders)
                            except Exception as e:
                                st.warning(f"Could not fetch persisted learning_paths: {e}")

                        if not preview:
                            st.info("No persisted HTML/CSS-like content found in learning paths.")
                        else:
                            st.markdown("**Found suspicious content in the following learning paths:**")
                            for pname, items in preview.items():
                                with st.expander(pname, expanded=False):
                                    for it in items:
                                        st.code(it.get('snippet', ''), language='html')
                            st.warning("If you see entries above, you can use the sidebar '⚠️ Cleanup stored HTML/CSS (safe)' expander to preview and purge them. Purging requires explicit confirmation.")

        else:
            path_data = paths[active_path_name]
            if path_data.get('path_type') == 'project':
                render_project_view(uid, active_path_name, path_data)
            else:
                render_standard_view(uid, active_path_name, path_data)

if __name__ == "__main__":
    main()

