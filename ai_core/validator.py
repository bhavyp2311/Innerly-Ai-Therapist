import re

BANNED_WORDS = [
    "diagnose", "diagnosis", "disorder", "therapy",
    "clinical", "condition", "treatment", "mental illness"
]

def is_valid_response(text: str) -> bool:
    # Too long
    if len(text.split()) > 80:
        return False

    # Too many questions
    if text.count("?") > 1:
        return False

    # Lists or bullets
    if re.search(r"[\-\*\•]", text):
        return False

    # Banned words
    lower = text.lower()
    for word in BANNED_WORDS:
        if word in lower:
            return False

    # Commanding tone
    if "you should" in lower or "you must" in lower:
        return False
    if "let's" in lower or "try to" in lower:
        return False
    return True
    # No stage forcing language


