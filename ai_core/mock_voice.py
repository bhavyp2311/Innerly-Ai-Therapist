def extract_typing_signals(text: str):
    signals = {
        "short": len(text.split()) < 4,
        "ellipsis": "..." in text,
        "repetition": any(text.count(w) > 2 for w in text.split()),
        "lowercase_only": text.islower(),
        "emoji_only": all(not c.isalnum() for c in text),
    }
    return signals
