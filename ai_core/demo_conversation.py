"""
DEMO SCRIPT
-----------
Simulates a real user conversation with:
- messy Gen-Z typing
- short + long messages
- stage progression
- summary updates
"""

from ai_engine import GeminiClient, generate_ai_reply
import time

# -----------------------------------
# INIT
# -----------------------------------
gemini = GeminiClient()

# Simulated user messages (REALISTIC + MESSY)
USER_MESSAGES = [
    "idk man",
    "everything feels weird lately",
    "like nothing is actually wrong but still feels off",
    "my brain just wont shut up fr",
    "24/7",
    "even when im tired",
    "then i get annoyed at myself for overthinking",
    "and then i spiral more lol",
    "i dont even talk about this much",
    "everyone just gives advice immediately",
    "like 'just chill' wow thanks",
    "so i stop talking about it",
    "but the thoughts dont stop",
    "sometimes i feel fine then suddenly nah",
    "mostly hits at night",
    "when everything slows down",
    "i overanalyze dumb stuff",
    "old convos replaying",
    "for no reason",
    "my brain is weird",
    "i get tired just thinking",
    "i just scroll till i fall asleep",
    "that makes me feel worse later",
    "i feel stuck in my head",
    "and its been like this for a while",
    # --- UNDERSTANDING should unlock here ---
    "yeah its been months i think",
    "started sometime last year maybe",
    # --- user explicitly asks ---
    "why does this keep happening to me",
    # --- later explicit guidance ---
    "what should i even do about this"
]

# -----------------------------------
# RUN CONVERSATION
# -----------------------------------
print("\n--- DEMO START ---\n")

for i, user_text in enumerate(USER_MESSAGES, start=1):
    print(f"USER {i}: {user_text}")

    ai_reply = generate_ai_reply(
        gemini_client=gemini,
        user_message=user_text,
        voice_signals=None  # text-only demo
    )

    print(f"AI   {i}: {ai_reply}\n")
    time.sleep(15)
    # Stop after guidance (as per rules)
    if "small step" in ai_reply.lower() or "you could" in ai_reply.lower():
        print("--- GUIDANCE GIVEN. CONVERSATION ENDS ---")
        break

print("\n--- DEMO END ---")
