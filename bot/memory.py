"""User memory extraction and management for conversation context."""

FACT_KEYWORDS = {
    "location": ["home", "house", "park", "library", "work", "office", "cafe", "store", "school"],
    "weapon": ["knife", "gun", "gun", "rope", "hammer", "crowbar", "tool", "weapon"],
    "vehicle": ["car", "truck", "bike", "motorcycle", "van", "suv", "sedan"],
    "time": ["pm", "am", "night", "morning", "afternoon", "evening", "yesterday", "today"],
    "person": ["friend", "family", "parent", "mom", "dad", "brother", "sister", "girlfriend"],
    "action": ["steal", "took", "stole", "saw", "found", "left", "went", "driving"],
}


def extract_facts(user_input: str, current_memory: dict) -> dict:
    """
    Extract facts from user input and update memory dict.
    
    Args:
        user_input: User message text
        current_memory: Existing memory dict for the user
        
    Returns:
        Updated memory dict with new facts
    """
    memory = current_memory.copy()
    text_lower = user_input.lower()
    
    for category, keywords in FACT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                if category not in memory:
                    memory[category] = []
                if keyword not in memory[category]:
                    memory[category].append(keyword)
    
    return memory


def format_memory_str(memory: dict) -> str:
    """
    Format memory dict into readable string for system prompt.
    
    Args:
        memory: User memory dict
        
    Returns:
        Formatted memory string
    """
    if not memory:
        return "No relevant facts tracked yet."
    
    facts = []
    for key, values in memory.items():
        if isinstance(values, list):
            facts.append(f"{key}: {', '.join(values)}")
        else:
            facts.append(f"{key}: {values}")
    
    return " | ".join(facts)
