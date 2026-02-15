"""
EduAI Backend — AI Service
Handles all OpenRouter API calls, model routing, and prompt engineering.
Ported from app.py's _call_openrouter, _auto_route, detect_emotion_and_adapt.
"""

from __future__ import annotations
import json
import re
import httpx
from openai import OpenAI
from config import settings


# ── OpenRouter Client ──────────────────────────────────────────────────────────

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            http_client=httpx.Client(
                base_url=settings.OPENROUTER_BASE_URL,
                follow_redirects=True,
                timeout=httpx.Timeout(60.0, connect=10.0),
            ),
        )
    return _client


# ── Model Selection ────────────────────────────────────────────────────────────

def pick_model(hint: str | None = None) -> str:
    """Resolve a model key to its full OpenRouter model ID."""
    if hint and hint in settings.AI_MODELS:
        return settings.AI_MODELS[hint]
    return settings.AI_MODELS["deepseek"]


def auto_route(prompt: str) -> str:
    """Pick the best model key based on keyword analysis of the prompt."""
    p = prompt.lower()

    code_kw = [
        "code", "python", "javascript", "function", "debug", "programming",
        "algorithm", "api", "html", "css", "sql", "compile", "syntax",
    ]
    visual_kw = [
        "diagram", "chart", "textbook", "graph", "table", "figure",
        "image", "photo", "picture", "screenshot", "slide", "video",
        "lecture", "handwriting", "scan", "document", "pdf",
    ]
    science_visual_kw = [
        "visual", "physics", "chemistry", "biology", "science",
        "experiment", "formula", "lab", "interactive",
    ]
    reason_kw = [
        "solve", "calculate", "math", "proof", "derive", "equation",
        "reason", "logic", "quiz", "step-by-step", "analyze",
    ]
    rp_kw = [
        "act as", "roleplay", "simulate", "pretend", "character",
        "you are a", "curious student", "feynman", "group discussion",
    ]

    if any(k in p for k in code_kw):
        return "arcee"
    if any(k in p for k in visual_kw):
        return "nemotron"
    if any(k in p for k in science_visual_kw):
        return "qwen_vl"
    if any(k in p for k in reason_kw):
        return "deepseek"
    if any(k in p for k in rp_kw):
        return "nous"
    return "deepseek"


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

def call_ai(
    messages: list[dict],
    model_hint: str | None = None,
    is_json: bool = False,
    temperature: float = 0.7,
) -> str | None:
    """Send a request to OpenRouter and return the response text."""
    client = get_client()
    model_id = pick_model(model_hint)

    kwargs: dict = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1024,
    }
    if is_json:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as primary_err:
        # Try each fallback model in order
        last_err = primary_err
        for fb_model in settings.FALLBACK_MODELS:
            try:
                fb_kwargs = {**kwargs, "model": fb_model}
                # Some models don't support system messages — merge into user
                if "gemma" in fb_model:
                    fb_kwargs["messages"] = _strip_system_messages(messages)
                resp = client.chat.completions.create(**fb_kwargs)
                return resp.choices[0].message.content
            except Exception as fb_err:
                last_err = fb_err
                continue
        raise RuntimeError(
            f"AI error ({model_id}): {primary_err} | All fallbacks failed. Last: {last_err}"
        )


def _strip_system_messages(messages: list[dict]) -> list[dict]:
    """Merge system messages into the first user message for models that don't support them."""
    system_parts = []
    other = []
    for m in messages:
        if m["role"] == "system":
            system_parts.append(m["content"])
        else:
            other.append(m)
    if system_parts and other:
        prefix = "\n".join(system_parts)
        other[0] = {**other[0], "content": f"{prefix}\n\n{other[0]['content']}"}
    return other or messages


def solve_vision(image_base64: str, prompt: str = "This is an educational problem. Solve it step-by-step and provide a clear explanation.") -> tuple[str, str]:
    """Send an image to a vision model for analysis."""
    client = get_client()
    # Try nemotron VL first, then qwen_vl
    vision_models = [settings.AI_MODELS["nemotron"], settings.AI_MODELS["qwen_vl"]]
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
        ],
    }]
    last_err = None
    for model_id in vision_models:
        try:
            resp = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.5,
                max_tokens=2048,
            )
            return resp.choices[0].message.content or "No response", model_id
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Vision analysis failed: {last_err}")


def generate_flashcards(topic: str, num_cards: int = 10) -> list[dict]:
    """Generate flashcards for a topic. Returns list of {question, answer} dicts."""
    messages = [
        {"role": "system", "content": "You are a flashcard generator. Return ONLY a JSON array of objects with 'question' and 'answer' keys. No markdown, no explanation."},
        {"role": "user", "content": f"Generate exactly {num_cards} educational flashcards about: {topic}. Each card should test a key concept. Return as JSON array."},
    ]
    resp = call_ai(messages, model_hint="deepseek", is_json=True)
    if resp:
        try:
            data = json.loads(resp) if isinstance(resp, str) else resp
            if isinstance(data, list):
                return data
            # Some models wrap in a key
            for key in ["cards", "flashcards"]:
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
    resp = call_ai(messages, model_hint="deepseek", is_json=True)
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
    resp = call_ai(messages, model_hint="deepseek", is_json=True)
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
    return call_ai(messages, model_hint="deepseek") or ""


def generate_skills_gap(skills: str) -> dict | None:
    """Generate a skills gap analysis as a JSON dict."""
    messages = [
        {"role": "system", "content": "Return ONLY a JSON object with skill names as keys and proficiency 0-100 as values. No markdown."},
        {"role": "user", "content": f"Based on these current skills ({skills}), rate proficiency for 6-8 relevant career skills."},
    ]
    resp = call_ai(messages, model_hint="deepseek", is_json=True)
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
    return call_ai(messages, model_hint="deepseek") or ""


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
    return call_ai(messages, model_hint="nous") or ""
