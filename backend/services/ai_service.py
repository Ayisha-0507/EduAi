from __future__ import annotations
import json
import re
import config
from PIL import Image
from io import BytesIO
import time
import google.generativeai as genai
import httpx
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
import random
import base64
from google.genai import types
from config import settings
def generate_video(prompt: str) -> dict:
    """Generate a video using the Veo model from a text prompt."""
    api_key = os.getenv("GEMINI_API_KEY", getattr(settings, "GEMINI_API_KEY", None))
    if not api_key:
        api_key = os.getenv("GOOGLE_STUDIO_API_KEY", getattr(settings, "GOOGLE_STUDIO_API_KEY", None))
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_STUDIO_API_KEY not set in environment or settings.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/veo-3.1-generate-preview")
    response = model.generate_content([prompt])
    # The response may contain a video URL or base64, depending on API
    video_url = getattr(response, 'video_url', None) or getattr(response, 'media_url', None) or str(response)
    return {"video_url": video_url, "model_used": "models/veo-3.1-generate-preview"}
"""
EduAI Backend — AI Service
Handles all Gemini API calls and prompt engineering.
Gemini-only — no OpenRouter or multi-model routing.
"""


# ── Model Selection ────────────────────────────────────────────────────────────

def pick_model(hint: str | None = None) -> str:
    """Return the Gemini model ID from config.py, defaulting to gemini-2.5-pro."""
    if hint and hint in settings.AI_MODELS:
        return settings.AI_MODELS[hint]
    return settings.AI_MODELS["gemini-2.5-pro"]


def auto_route(prompt: str) -> str:
    """Default to gemini-2.5-pro; routing logic can be added if needed."""
    return "gemini-2.5-pro"


# ── Emotion Detection ──────────────────────────────────────────────────────────

def detect_emotion(user_text: str) -> tuple[str, str]:
    """
    Detect user's emotional state from keyword heuristics.
    Returns (emotion_name, adaptive_prompt_prefix).
    """
    text_lower = user_text.lower()

    frustration_words = [
        "i don't understand", "confused", "stuck", "lost", "frustrated",
        "hard", "difficult", "can't", "impossible", "hate", "annoying",
        "help me", "not getting",
    ]
    anxiety_words = [
        "exam", "test tomorrow", "scared", "worried", "nervous",
        "failing", "deadline", "urgent", "panic",
    ]
    success_words = [
        "got it", "understood", "makes sense", "thank you", "thanks",
        "awesome", "great", "perfect", "i see", "clear now", "finally",
    ]
    boredom_words = [
        "boring", "bored", "too easy", "already know", "skip", "next",
    ]

    if any(w in text_lower for w in frustration_words):
        return "frustration", (
            "The student seems frustrated or confused. Respond with patience and empathy. "
            "Break down the concept into smaller steps. Use an encouraging tone. "
            "Say something like 'That is a really common sticking point, let me explain it differently.'"
        )
    if any(w in text_lower for w in anxiety_words):
        return "anxiety", (
            "The student seems anxious about an upcoming exam or deadline. "
            "Respond calmly and reassuringly. Focus on the most important points only. "
            "Offer a quick revision strategy. Say 'Let us focus on the key points that matter most.'"
        )
    if any(w in text_lower for w in success_words):
        return "success", (
            "The student seems to have understood the concept. Acknowledge their progress warmly. "
            "Then challenge them with a slightly harder follow-up question to deepen understanding. "
            "Say 'Excellent progress. Now try this slightly trickier angle...'"
        )
    if any(w in text_lower for w in boredom_words):
        return "boredom", (
            "The student seems bored or unchallenged. Increase the difficulty. "
            "Offer a real-world application or a challenging problem. "
            "Say 'Let us level up. Here is a real-world challenge...'"
        )
    return "", ""


# ── Tutor Persona Prompts ──────────────────────────────────────────────────────

PERSONA_PROMPTS = {
    "Friendly Encourager": "You are a warm, supportive tutor. Use encouraging language, celebrate small wins, and make the student feel comfortable asking questions.",
    "Strict Professor": "You are a rigorous academic professor. Expect effort from the student, point out mistakes clearly, and maintain high standards. Be concise and factual.",
    "Socratic Questioner": "You are a Socratic tutor. Instead of giving answers directly, ask probing questions to guide the student toward discovering the answer themselves.",
    "Concise Technician": "You are a direct, no-nonsense tutor. Give short, precise answers. Skip pleasantries and get straight to the point. Use bullet points when possible.",
    "Creative Storyteller": "You are a creative storyteller tutor. Explain every concept through stories, analogies, and real-world narratives. Make learning feel like an adventure.",
}

RESPONSE_STYLE_PROMPTS = {
    "default": "",
    "simple": "Explain this in very simple terms, as if teaching a beginner. Use everyday language and avoid jargon.",
    "code": "Provide a practical code example to illustrate the concept. Include comments explaining each part.",
    "analogy": "Explain this using a real-world analogy that a student from any background can relate to.",
}


# ── Core Chat Call ─────────────────────────────────────────────────────────────

def _is_rate_limit_error(err: Exception) -> bool:
    """Check if an error is a rate-limit (429) error."""
    err_str = str(err).lower()
    return "429" in err_str or "rate limit" in err_str or "rate_limit" in err_str or "too many requests" in err_str

from __future__ import annotations
from google import genai # Modern SDK 2.0
from google.genai import types
import os
from config import settings

def call_ai(
    messages: list[dict], 
    model_hint: str = "gemini-2.5-pro", # Unoda fav model
    temperature: float = 0.7
) -> str | None:
    """Straightforward Gemini 2.5 Pro call without any rotations."""
    
    # 1. Setup API Key from Environment
    api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
    if not api_key:
        return "API Error: GEMINI_API_KEY is missing in environment variables."

    client = genai.Client(api_key=api_key)

    try:
        # 2. Format contents for SDK 2.0
        system_instruction = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction += msg["content"] + "\n"
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        # 3. Direct Call to Gemini 2.5 Pro
        config = types.GenerateContentConfig(
            system_instruction=system_instruction.strip() if system_instruction else None,
            temperature=temperature,
            max_output_tokens=2048
        )

        response = client.models.generate_content(
            model=model_hint,
            contents=contents,
            config=config
        )
        
        return response.text
    except Exception as e:
        return f"Gemini 2.5 Pro Error: {str(e)}"

    # 3. Handle Fallbacks & Model Selection
    primary_model = pick_model(model_hint) # Uses your gemini-2.5-pro etc.
    candidates = [primary_model]
    if hasattr(settings, "FALLBACK_MODELS"):
        for m in settings.FALLBACK_MODELS:
            if m not in candidates: candidates.append(m)

    # 4. Try Candidates
    for model_id in candidates:
        try:
            # Setup Config
            config = types.GenerateContentConfig(
                system_instruction=system_instruction.strip() if system_instruction else None,
                temperature=temperature,
                response_mime_type="application/json" if is_json else "text/plain",
                max_output_tokens=2048
            )

            response = client.models.generate_content(
                model=model_id,
                contents=formatted_contents,
                config=config
            )
            
            if response.text:
                return response.text
                
        except Exception as e:
            print(f"Failed with {model_id}: {str(e)}")
            continue # Try next fallback

    return "Sorry, all Gemini models are currently busy. Try again in a bit!"


    # Helper to fetch remote models from Google Studio if needed
    def _fetch_remote_models() -> list[str]:
        try:
            resp = httpx.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                mods = [m.get("name") or m for m in data.get("models", [])]
                return mods
        except Exception:
            pass
        return []

    # Convert OpenAI-style messages to Gemini prompt
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt += f"[System] {content}\n"
        elif role == "assistant":
            prompt += f"[AI] {content}\n"
        else:
            prompt += f"[User] {content}\n"

    last_err: Exception | None = None
    tried = set()

    # Try each candidate model with retry on rate limits
    for model_id in candidates:
        if not model_id or model_id in tried:
            continue
        tried.add(model_id)
        model = genai.GenerativeModel(model_id)
        for attempt in range(1 + settings.RATE_LIMIT_RETRIES):
            try:
                response = model.generate_content(prompt, generation_config={"temperature": temperature}, safety_settings=None)
                answer = response.text.strip() if hasattr(response, "text") else str(response)
                return answer
            except Exception as err:
                last_err = err
                if _is_rate_limit_error(err) and attempt < settings.RATE_LIMIT_RETRIES:
                    time.sleep(settings.RATE_LIMIT_DELAY * (attempt + 1))
                    continue
                # If error suggests model not found/unsupported, break to try next candidate
                e = str(err).lower()
                if "not found" in e or "not supported" in e or "404" in e or "models/" in e:
                    break
                # otherwise, stop retrying this model
                break

    # If all configured candidates failed, fetch remote models and try them
    remote_models = _fetch_remote_models()
    for model_id in remote_models:
        if not model_id or model_id in tried:
            continue
        tried.add(model_id)
        try:
            model = genai.GenerativeModel(model_id)
            for attempt in range(1 + settings.RATE_LIMIT_RETRIES):
                try:
                    response = model.generate_content(prompt, generation_config={"temperature": temperature}, safety_settings=None)
                    answer = response.text.strip() if hasattr(response, "text") else str(response)
                    return answer
                except Exception as err:
                    last_err = err
                    if _is_rate_limit_error(err) and attempt < settings.RATE_LIMIT_RETRIES:
                        time.sleep(settings.RATE_LIMIT_DELAY * (attempt + 1))
                        continue
                    break
        except Exception as err:
            last_err = err
            continue

    # If we reach here, all attempts failed
    if last_err:
        return f"API Error caught: {str(last_err)}"
    return "Failed to get response after retries."
def solve_vision(image_base64: str, prompt: str = "This is an educational problem. Solve it step-by-step and provide a clear explanation.") -> tuple[str, str]:
    """Send an image to Gemini vision model for analysis."""
    api_key = os.getenv("GEMINI_API_KEY", getattr(settings, "GEMINI_API_KEY", None))
    if not api_key:
        api_key = os.getenv("GOOGLE_STUDIO_API_KEY", getattr(settings, "GOOGLE_STUDIO_API_KEY", None))
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_STUDIO_API_KEY not set in environment or settings.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/imagen-4.0-generate-001")
    # Decode base64 image
    image_bytes = base64.b64decode(image_base64)
    # Gemini expects a PIL Image
    image = Image.open(BytesIO(image_bytes))
    # Run Gemini vision
    response = model.generate_content([
        prompt,
        image
    ])
    answer = response.text.strip() if hasattr(response, 'text') else str(response)
    return answer, "models/imagen-4.0-generate-001"


def generate_flashcards(topic: str, num_cards: int = 10) -> list[dict]:
    """Generate flashcards for a topic. Returns list of {question, answer} dicts."""
    messages = [
        {"role": "system", "content": "You are a flashcard generator. Return ONLY a JSON array of objects with 'question' and 'answer' keys. No markdown, no explanation, no code fences."},
        {"role": "user", "content": f"Generate exactly {num_cards} educational flashcards about: {topic}. Each card should test a key concept. Return as JSON array."},
    ]
    resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
    if not resp:
        # Retry without JSON mode in case model doesn't support it
        resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=False)
    if resp:
        try:
            # Strip markdown code fences if present
            cleaned = resp.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]  # remove first line
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
            data = json.loads(cleaned) if isinstance(cleaned, str) else cleaned
            if isinstance(data, list):
                return data
            # Some models wrap in a key
            for key in ["cards", "flashcards", "data"]:
                if key in data:
                    return data[key]
        except Exception:
            pass
    return []


def build_chat_messages(
    user_message: str,
    history: list[dict] | None = None,
    persona: str = "Friendly Encourager",
    response_style: str = "default",
    language: str = "English",
    topic: str | None = None,
    emotion_prefix: str = "",
) -> list[dict]:
    """Construct the messages list for the AI call, injecting persona/style/emotion."""
    system_parts = [
        "You are EduAI, an adaptive personal tutor.",
        PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["Friendly Encourager"]),
    ]
    if topic:
        system_parts.append(f"Current topic: {topic}")
    if language and language != "English":
        system_parts.append(f"Respond in {language}.")
    style_prompt = RESPONSE_STYLE_PROMPTS.get(response_style, "")
    if style_prompt:
        system_parts.append(style_prompt)
    if emotion_prefix:
        system_parts.append(emotion_prefix)

    messages = [{"role": "system", "content": " ".join(system_parts)}]

    if history:
        for msg in history[-20:]:  # last 20 messages for context window
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages


# ── Specialized Generators ─────────────────────────────────────────────────────

def generate_learning_path_topics(goal: str) -> list[str]:
    """Ask AI to generate a structured list of 5-7 learning topics for a goal."""
    messages = [
        {"role": "system", "content": "You are a curriculum designer. Return ONLY a JSON array of 5-7 topic strings for a learning path. No explanations."},
        {"role": "user", "content": f"Create a learning path for: {goal}"},
    ]
    resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
    if resp:
        try:
            data = json.loads(resp)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        return v
        except Exception:
            pass
    return [goal]


def generate_quiz(topic: str, num_questions: int = 5) -> list[dict] | None:
    """Generate quiz questions for a topic."""
    messages = [
        {
            "role": "system",
            "content": (
                f"Generate exactly {num_questions} multiple-choice quiz questions about the topic. "
                "Return ONLY a JSON array where each element has: "
                '"question" (string), "options" (array of 4 strings), "answer" (the correct option string). '
                "No markdown, no explanation."
            ),
        },
        {"role": "user", "content": f"Topic: {topic}"},
    ]
    resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
    return parse_quiz_response(resp)


def parse_quiz_response(resp: str | None) -> list[dict] | None:
    """Parse AI quiz response into a list of question dicts."""
    if not resp:
        return None
    try:
        data = json.loads(resp)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "questions" in data:
                return data["questions"]
            if all(k in data for k in ["question", "options", "answer"]):
                return [data]
    except Exception:
        try:
            match = re.search(r"```json\n(.*?)```", resp, re.DOTALL) or re.search(r"(\[.*?\])", resp, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception:
            pass
    return None


def generate_career_paths(interests: str, skills: str, education: str, location: str, aspirations: str, budget: str) -> str:
    """Generate career path recommendations."""
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
    messages = [
        {"role": "system", "content": "You are a career counselor AI."},
        {"role": "user", "content": prompt},
    ]
    return call_ai(messages, model_hint="gemini-2.5-pro") or ""


def generate_skills_gap(skills: str) -> dict | None:
    """Generate a skills gap analysis as a JSON dict."""
    messages = [
        {"role": "system", "content": "Return ONLY a JSON object with skill names as keys and proficiency 0-100 as values. No markdown."},
        {"role": "user", "content": f"Based on these current skills ({skills}), rate proficiency for 6-8 relevant career skills."},
    ]
    resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
    if resp:
        try:
            return json.loads(resp) if isinstance(resp, str) else resp
        except Exception:
            pass
    return None


SUMMARY_FORMAT_INSTRUCTIONS = {
    "Bullet-point summary": "Provide a concise bullet-point summary with key concepts, definitions, and important facts. Max 15 bullets.",
    "Flashcards (Q&A)": "Generate 8-10 flashcards as Q&A pairs. Format: Q: ... A: ...",
    "Exam answer notes": "Convert into exam-ready notes: definition, key points, example, diagram description (if applicable), conclusion. Suitable for 6-10 mark answers.",
    "Mind map outline": "Create a hierarchical mind map outline using indentation. Main topic > Sub-topics > Details.",
    "All formats": "Provide ALL of the following:\n1. Bullet-point summary (10 bullets)\n2. 5 Flashcards (Q&A)\n3. One exam answer template (6-mark format)\n4. Mind map outline",
}


def generate_summary(text: str, format_name: str) -> str:
    """Summarize text in the requested format."""
    truncated = text[:12000]
    instruction = SUMMARY_FORMAT_INSTRUCTIONS.get(format_name, SUMMARY_FORMAT_INSTRUCTIONS["Bullet-point summary"])
    messages = [
        {"role": "system", "content": "You are an educational summarizer."},
        {"role": "user", "content": f"Instructions: {instruction}\n\nTEXT TO SUMMARIZE:\n{truncated}"},
    ]
    return call_ai(messages, model_hint="gemini-2.5-pro") or ""


def generate_feynman_response(user_message: str, history: list[dict]) -> str:
    """Feynman Board: AI acts as a curious, confused student."""
    system = (
        "You are a curious but slightly confused student. The user is trying to teach you a concept. "
        "Ask probing clarifying questions to test the depth of their understanding. "
        "Pretend you don't fully understand and ask 'but why?' style questions. "
        "If they explain well, show that you're starting to understand. "
        "Keep responses short (2-4 sentences)."
    )
    messages = [{"role": "system", "content": system}]
    for msg in history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})
    return call_ai(messages, model_hint="gemini-2.5-pro") or ""


# ── Debate Arena ─────────────────────────────────────────────────────────────

def _clean_json_response(text: str) -> str:
    """Strip markdown fences and whitespace from AI JSON responses."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    return cleaned


def debate_round(
    topic: str,
    user_stance: str,
    round_number: int,
    total_rounds: int,
    user_argument: str | None,
    history: list[dict],
) -> dict:
    """
    Process one debate round. If round_number == 0 and no user_argument,
    return the AI's opening statement. Otherwise score user's argument
    and return AI's counter-argument.
    """
    ai_stance = "against" if user_stance.lower() == "for" else "for"
    is_opening = round_number == 0 and not user_argument
    is_final = round_number >= total_rounds

    if is_opening:
        # AI opening argument — no scoring
        system = (
            f"You are in a formal debate about: '{topic}'. "
            f"You argue {ai_stance.upper()} this topic. "
            f"Give a strong opening argument (3-5 sentences). "
            f"Be persuasive, cite reasoning, and set up your position. "
            f"Return ONLY a JSON object with key 'ai_argument'. No markdown."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Begin your opening argument {ai_stance} the topic: {topic}"},
        ]
        resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
        if not resp:
            resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=False)

        ai_arg = topic  # fallback
        if resp:
            try:
                data = json.loads(_clean_json_response(resp))
                ai_arg = data.get("ai_argument", resp)
            except Exception:
                ai_arg = resp

        return {
            "ai_argument": ai_arg,
            "scores": {"logic": 0, "evidence": 0, "persuasion": 0, "fallacies": [], "feedback": "Opening round — no scores yet."},
            "round_number": 0,
            "is_final": False,
        }

    # Regular round — score user argument + counter
    history_text = ""
    for h in history:
        history_text += f"\n[Round {h.get('round', '?')}]\n"
        if h.get("user"):
            history_text += f"Student ({user_stance}): {h['user']}\n"
        if h.get("ai"):
            history_text += f"AI ({ai_stance}): {h['ai']}\n"

    system = (
        f"You are a debate judge AND participant in a formal debate about: '{topic}'.\n"
        f"The student argues {user_stance.upper()}. You argue {ai_stance.upper()}.\n"
        f"This is round {round_number} of {total_rounds}.\n\n"
        f"Your task:\n"
        f"1. Score the student's latest argument on three criteria (1-10 each):\n"
        f"   - logic: How logically sound is the reasoning?\n"
        f"   - evidence: How well-supported with facts/examples?\n"
        f"   - persuasion: How convincing and well-structured?\n"
        f"2. Identify any logical fallacies (empty list if none).\n"
        f"3. Give brief feedback (1-2 sentences) on what was strong/weak.\n"
        f"4. Present YOUR counter-argument (3-5 sentences), arguing {ai_stance}.\n\n"
        f"Return ONLY a JSON object with these exact keys:\n"
        f'{{"ai_argument": "...", "logic": N, "evidence": N, "persuasion": N, '
        f'"fallacies": ["...", ...], "feedback": "..."}}\n'
        f"No markdown code fences. Just raw JSON."
    )

    messages = [{"role": "system", "content": system}]
    if history_text:
        messages.append({"role": "assistant", "content": f"Previous rounds:{history_text}"})
    messages.append({"role": "user", "content": f"Student's argument ({user_stance}): {user_argument}"})

    resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
    if not resp:
        resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=False)

    # Parse response
    result = {
        "ai_argument": "I concede this point. Please continue.",
        "scores": {"logic": 5, "evidence": 5, "persuasion": 5, "fallacies": [], "feedback": "Score unavailable."},
        "round_number": round_number,
        "is_final": is_final,
    }

    if resp:
        try:
            data = json.loads(_clean_json_response(resp))
            result["ai_argument"] = data.get("ai_argument", result["ai_argument"])
            result["scores"] = {
                "logic": min(10, max(1, int(data.get("logic", 5)))),
                "evidence": min(10, max(1, int(data.get("evidence", 5)))),
                "persuasion": min(10, max(1, int(data.get("persuasion", 5)))),
                "fallacies": data.get("fallacies", []),
                "feedback": data.get("feedback", ""),
            }
        except Exception:
            # If JSON parsing fails, use the raw text as the argument
            result["ai_argument"] = resp

    return result


def debate_final(topic: str, user_stance: str, history: list[dict]) -> dict:
    """Generate final debate summary with overall scores and winner."""
    ai_stance = "against" if user_stance.lower() == "for" else "for"

    rounds_text = ""
    for h in history:
        rounds_text += f"\n[Round {h.get('round', '?')}]\n"
        rounds_text += f"Student ({user_stance}): {h.get('user', 'N/A')}\n"
        rounds_text += f"AI ({ai_stance}): {h.get('ai', 'N/A')}\n"
        scores = h.get("scores", {})
        rounds_text += f"Scores: Logic={scores.get('logic', '?')}, Evidence={scores.get('evidence', '?')}, Persuasion={scores.get('persuasion', '?')}\n"

    system = (
        f"You are an impartial debate judge reviewing a completed debate about: '{topic}'.\n"
        f"Student argued {user_stance.upper()}, AI argued {ai_stance.upper()}.\n\n"
        f"Here are all rounds:\n{rounds_text}\n\n"
        f"Provide a final analysis. Return ONLY JSON with these keys:\n"
        f'{{"summary": "2-3 sentence overall assessment",'
        f' "logic": N, "evidence": N, "persuasion": N,'
        f' "strengths": ["strength1", "strength2", ...],'
        f' "weaknesses": ["weakness1", "weakness2", ...],'
        f' "recommendation": "What the student should study/practice to improve",'
        f' "winner": "student" or "ai" or "tie"}}\n'
        f"No markdown. Just raw JSON."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Judge this debate and provide the final verdict."},
    ]

    resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=True)
    if not resp:
        resp = call_ai(messages, model_hint="gemini-2.5-pro", is_json=False)

    # Defaults
    result = {
        "summary": "Debate completed. Both sides presented their cases.",
        "total_score": {"logic": 5, "evidence": 5, "persuasion": 5, "fallacies": [], "feedback": ""},
        "strengths": ["Participated actively"],
        "weaknesses": ["Could use more supporting evidence"],
        "recommendation": "Practice structuring arguments with clear evidence.",
        "winner": "tie",
    }

    if resp:
        try:
            data = json.loads(_clean_json_response(resp))
            result["summary"] = data.get("summary", result["summary"])
            result["total_score"] = {
                "logic": min(10, max(1, int(data.get("logic", 5)))),
                "evidence": min(10, max(1, int(data.get("evidence", 5)))),
                "persuasion": min(10, max(1, int(data.get("persuasion", 5)))),
                "fallacies": [],
                "feedback": "",
            }
            result["strengths"] = data.get("strengths", result["strengths"])
            result["weaknesses"] = data.get("weaknesses", result["weaknesses"])
            result["recommendation"] = data.get("recommendation", result["recommendation"])
            result["winner"] = data.get("winner", result["winner"])
        except Exception:
            pass

    return result
