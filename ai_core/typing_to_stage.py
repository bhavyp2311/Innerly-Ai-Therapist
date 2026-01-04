from stages import AIStage

# -----------------------------
# EXPLICIT USER INTENT PHRASES
# -----------------------------

UNDERSTANDING_TRIGGERS = [
    # confusion / clarity seeking
    "i don't understand",
    "i dont understand",
    "i’m confused",
    "i am confused",
    "this is confusing",
    "why is this happening",
    "why does this happen",
    "what is going on",
    "what’s going on",
    "can you explain",
    "can you help me understand",
    "i don’t get it",
    "i dont get it",
    "i’m not sure why",
    "i am not sure why",
    "i don’t know why",
    "i dont know why",
    "this doesn’t make sense",
    "this does not make sense",
    "i’m stuck",
    "i am stuck",
    "i feel stuck",
    "i’m unclear",
    "i am unclear",
    "i’m lost about this",
    "i am lost about this",
    "i can’t figure this out",
    "i cant figure this out",
    "i don’t know what’s wrong",
    "i dont know what’s wrong",
    "something isn’t clear",
    "something is not clear",
    "i’m trying to understand",
    "i am trying to understand",
    "can you clarify",
    "help me make sense of this",
    "why do i feel this way",
    "why does it feel like this",
    "i don’t know what this means",
    "i dont know what this means",
    "what does this mean",
    "what am i missing",
    "i feel confused about this",
]

GUIDANCE_TRIGGERS = [
    # direct help / action seeking
    "what should i do",
    "what do i do",
    "what can i do",
    "how do i handle this",
    "how should i handle this",
    "how do i deal with this",
    "how can i deal with this",
    "tell me what to do",
    "please tell me what to do",
    "give me advice",
    "i need advice",
    "can you guide me",
    "guide me",
    "help me decide",
    "help me with this",
    "what’s the next step",
    "what is the next step",
    "what should i do next",
    "what do i do next",
    "how do i move forward",
    "how can i move forward",
    "how do i fix this",
    "how can i fix this",
    "what’s the right thing to do",
    "what is the right thing to do",
    "should i do something",
    "should i act on this",
    "tell me how to handle it",
    "give me one step",
    "just tell me one thing to do",
    "i want help",
    "i need help with this",
    "what would you do",
    "what’s your suggestion",
    "what is your suggestion",
    "can you suggest something",
    "how do i stop this",
    "how do i change this",
    "what can help me",
    "what will help me",
    "how do i get out of this",
]

# -----------------------------
# STAGE DECISION
# -----------------------------

def decide_stage_from_typing(user_text: str) -> AIStage:
    text = user_text.lower().strip()

    # Explicit guidance request ALWAYS wins
    for phrase in GUIDANCE_TRIGGERS:
        if phrase in text:
            return AIStage.GUIDANCE

    # Explicit confusion / clarity request
    for phrase in UNDERSTANDING_TRIGGERS:
        if phrase in text:
            return AIStage.UNDERSTANDING

    # Default: listening
    return AIStage.LISTENING
