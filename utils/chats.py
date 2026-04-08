import json
import os

BASE_DIR = os.path.dirname(__file__)
FILE = os.path.join(BASE_DIR, "chats_data.json")


def _normalize_history(history):
    """Convert legacy role/content entries to compact user/assistant entries."""
    normalized = []

    for item in history:
        if not isinstance(item, dict):
            continue

        if "user" in item:
            normalized.append({"user": item["user"]})
        elif "assistant" in item:
            normalized.append({"assistant": item["assistant"]})
        elif item.get("role") == "user":
            normalized.append({"user": item.get("content", "")})
        elif item.get("role") == "assistant":
            normalized.append({"assistant": item.get("content", "")})

    return normalized


def load_data():
    """Load chat data from JSON, normalize format, and keep last 20 messages per user."""
    if not os.path.exists(FILE):
        return {}
    
    with open(FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    normalized_data = {}
    for chat_id, history in raw_data.items():
        normalized = _normalize_history(history if isinstance(history, list) else [])
        # Keep last 20 messages to balance memory and context
        normalized_data[str(chat_id)] = normalized[-20:] if len(normalized) > 20 else normalized

    return normalized_data


def save_data(data):
    """Save chat data to JSON in compact format."""
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))