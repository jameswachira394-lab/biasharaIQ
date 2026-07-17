import os
import json
import logging
import pickle
from decimal import Decimal
from datetime import date, datetime

import redis
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from services.intent_classifier import classify_intent, get_intent_description
from services.context_builder import ContextBuilder
from models.models import User

# =========================
# LOGGING
# =========================

logger = logging.getLogger(__name__)

# =========================
# GEMINI CONFIGURATION
# =========================

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key)

# =========================
# REDIS CONFIGURATION
# Replace in-memory dict with Redis for:
#   - Multi-worker safety
#   - Persistence across restarts
#   - Automatic TTL-based session expiry
# =========================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=False,  # We use pickle, so raw bytes
)

SESSION_TTL_SECONDS = int(os.getenv("CHAT_SESSION_TTL", 60 * 60 * 2))  # Default: 2 hours
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 2000))
MAX_RESPONSE_LENGTH = int(os.getenv("MAX_RESPONSE_LENGTH", 5000))
SESSION_RESET_AFTER_MESSAGES = int(os.getenv("SESSION_RESET_AFTER_MESSAGES", 30))


# =========================
# SESSION STORAGE HELPERS
# =========================

def _session_key(user_id: int) -> str:
    return f"biasharaiq:chat_session:{user_id}"


def get_session(user_id: int) -> dict | None:
    """
    Retrieve a chat session from Redis.
    Returns None if session doesn't exist or can't be deserialized.

    NOTE: Gemini's chat object may not be picklable in all SDK versions.
    If you hit pickle errors, switch to storing conversation history as
    plain dicts and reconstructing the chat via client.chats.create(history=[...]).
    """
    try:
        data = redis_client.get(_session_key(user_id))
        if data is None:
            return None
        return pickle.loads(data)
    except (pickle.UnpicklingError, redis.RedisError, Exception) as e:
        logger.warning("Failed to load session for user %s: %s", user_id, e)
        return None


def save_session(user_id: int, session: dict) -> None:
    """Persist a chat session to Redis with TTL."""
    try:
        redis_client.setex(
            _session_key(user_id),
            SESSION_TTL_SECONDS,
            pickle.dumps(session),
        )
    except (pickle.PicklingError, redis.RedisError, Exception) as e:
        # Non-fatal: log and continue. The session will just reset next request.
        logger.error("Failed to save session for user %s: %s", user_id, e)


def delete_session(user_id: int) -> None:
    """Delete a chat session from Redis."""
    try:
        redis_client.delete(_session_key(user_id))
    except redis.RedisError as e:
        logger.warning("Failed to delete session for user %s: %s", user_id, e)


# =========================
# JSON SERIALIZATION HELPERS
# Handles Decimal, date, datetime to
# prevent TypeError in json.dumps
# =========================

class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def safe_json_dumps(data: dict, **kwargs) -> str:
    return json.dumps(data, cls=SafeJSONEncoder, **kwargs)


# =========================
# SYSTEM PROMPT
# =========================

def build_system_prompt() -> str:
    return """
You are BiasharaIQ AI, a financial intelligence assistant for SMEs in Kenya.

ROLE: Help business owners understand their finances and make smart decisions.

RULES:
- Analyze the provided financial metrics ONLY
- Use simple business language - no jargon
- Be concise: aim for under 200 words
- Always reference specific numbers from the data
- If data is unclear or missing, say so directly
- Use Kenyan context (KES, M-Pesa, suppliers)
- State clearly if the business is losing money
- Focus on the highest-impact actions first
- Never invent data; never modify the numbers provided
"""


# =========================
# CREATE NEW CHAT SESSION
# =========================

def create_chat_session() -> genai.chats.Chat:
    """
    Create a new chat session without pre-seeding data.
    
    Financial context will be provided per-question based on intent,
    not upfront. This reduces token usage and improves accuracy.
    """
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            temperature=0.2,  # Lower = more focused, fewer hallucinations
        ),
    )
    return chat


# =========================
# MAIN AI CHAT FUNCTION
# =========================

def chat_with_ai_agent(
    db: Session,
    user_id: int,
    business_name: str,
    user_message: str,
) -> str:
    """
    Main AI agent function using intent-based architecture.

    Flow:
    1. Classify user intent (profitability, cashflow, expenses, risk, etc.)
    2. Build focused context for that intent
    3. Add context to message
    4. Send to Gemini with strict token limits
    5. Return response

    This approach:
    - Reduces token usage by ~70%
    - Improves response accuracy (focused data)
    - Keeps API costs low
    - Provides faster responses
    """

    # ─────────────────────────────────────
    # INPUT VALIDATION
    # ─────────────────────────────────────

    user_message = user_message.strip()

    if not user_message:
        return "Please enter a message."

    if len(user_message) > MAX_MESSAGE_LENGTH:
        raise ValueError(
            f"Message too long. Please keep it under {MAX_MESSAGE_LENGTH} characters."
        )

    # ─────────────────────────────────────
    # CHECK USAGE LIMITS
    # ─────────────────────────────────────
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found.")

    now = datetime.utcnow()
    # Reset counts if it's a new month
    if user.ai_queries_reset_date is None or user.ai_queries_reset_date.month != now.month or user.ai_queries_reset_date.year != now.year:
        user.ai_queries_count = 0
        user.ai_queries_reset_date = now
        db.commit()

    limit = 100 if user.plan == 'PRO' else 10
    if user.ai_queries_count >= limit:
        return f"You have reached your AI Advisor limit for this month ({limit} queries). Please upgrade your plan for more insights."

    # ─────────────────────────────────────
    # CLASSIFY INTENT
    # ─────────────────────────────────────

    intent = classify_intent(user_message)
    intent_name = get_intent_description(intent)
    logger.info(f"[AI] User {user_id} intent: {intent_name}")

    # ─────────────────────────────────────
    # BUILD FOCUSED CONTEXT FOR INTENT
    # ─────────────────────────────────────

    builder = ContextBuilder(db, user_id, business_name)
    context_data = builder.build_for_intent(intent, user_message)

    context_text = context_data["context_text"]
    max_tokens = context_data["max_tokens"]

    # ─────────────────────────────────────
    # CREATE MESSAGE WITH CONTEXT
    # ─────────────────────────────────────

    full_message = f"{context_text}\n\n---\n\nUser question: {user_message}"

    # ─────────────────────────────────────
    # GET RESPONSE FROM GEMINI
    # ─────────────────────────────────────

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_message,
            config=types.GenerateContentConfig(
                system_instruction=build_system_prompt(),
                temperature=0.2,
                max_output_tokens=max_tokens,
            ),
        )

        # Extract and validate response
        response_text = getattr(response, "text", None) or ""
        response_text = response_text.strip()

        if not response_text:
            logger.warning("Empty response from Gemini for user %s", user_id)
            return "I couldn't generate a response. Please rephrase your question and try again."

        if len(response_text) > MAX_RESPONSE_LENGTH:
            logger.warning(
                "Response exceeded max length (%d chars) for user %s - truncating",
                len(response_text),
                user_id,
            )
            response_text = response_text[:MAX_RESPONSE_LENGTH] + "..."

        logger.info(
            f"[AI] User {user_id} ({intent_name}): {len(response_text)} char response"
        )
        
        # Increment usage count
        user.ai_queries_count += 1
        db.commit()
        
        return response_text

    except Exception as e:
        error_msg = str(e)
        logger.exception(f"[AI] Gemini error for user {user_id}: {error_msg}")

        if "429" in error_msg or "quota" in error_msg.lower():
            raise Exception("API quota exceeded. Please try again in a few moments.")
        elif "401" in error_msg or "403" in error_msg:
            raise Exception("AI service configuration error.")
        else:
            raise Exception("AI service temporarily unavailable.")