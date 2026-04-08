import os
from dotenv import load_dotenv
from groq import Groq
from bot.memory import extract_facts, format_memory_str

# Load .env values before creating Groq client.
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are a suspect who secretly stole an expensive car yesterday at 3 PM with two friends. Your parents don’t know. Act like a real person: stay calm, lie convincingly, avoid traps, and protect your story. Be consistent with details (names, timeline) and don’t easily confess. Keep replies short and natural, occasionally using emojis."
)


def _trim_history(history: list, max_messages: int = 6) -> list:
    """Keep only the last N messages to save tokens."""
    return history[-max_messages:] if len(history) > max_messages else history


def _convert_to_model_format(history: list) -> list:
    """Convert compact storage format to role/content format for API."""
    model_history = []

    for item in history:
        if not isinstance(item, dict):
            continue

        # Handle compact format: {"user": "..."} or {"assistant": "..."}
        if "user" in item:
            model_history.append({"role": "user", "content": item["user"]})
        elif "assistant" in item:
            model_history.append({"role": "assistant", "content": item["assistant"]})
        # Handle legacy role/content format for backward compatibility
        elif item.get("role") in {"user", "assistant"}:
            model_history.append({"role": item["role"], "content": item.get("content", "")})

    return model_history


def get_response(user_input: str, history: list, user_memory: dict = None) -> tuple:
    """
    Get response from Groq API with token-efficient history management.
    
    Args:
        user_input: User message
        history: Chat history in compact format
        user_memory: User facts dict (updated in real-time)
        
    Returns:
        Tuple of (bot_reply, updated_memory)
    """
    if user_memory is None:
        user_memory = {}

    # Update memory with facts from current input
    user_memory = extract_facts(user_input, user_memory)

    # Trim history to last 6 messages
    trimmed_history = _trim_history(history, max_messages=6)

    # Convert compact format to role/content format
    model_history = _convert_to_model_format(trimmed_history)

    # Build messages for API
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"Tracked facts about suspect: {format_memory_str(user_memory)}"
        }
    ]

    # Add conversation history
    messages.extend(model_history)

    # Add current user message
    messages.append({"role": "user", "content": user_input})

    # Call Groq API
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    bot_reply = completion.choices[0].message.content
    print(f"[Bot Response] {bot_reply}")

    return bot_reply, user_memory
