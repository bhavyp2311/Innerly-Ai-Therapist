from stages import AIStage
from ai_engine import generate_ai_reply, GeminiClient
from summary_engine import update_summary

# -----------------------------
# SETUP
# -----------------------------
gemini = GeminiClient()
stage = AIStage.LISTENING.value

summary = "User feels neutral.\nContext is unclear.\nPattern is unknown."

conversation_log = []
recent_buffer = []   # last 2–3 messages


# -----------------------------
# SIMULATED USER INPUTS
# -----------------------------
user_messages = [
    "I feel lost lately.",
    "My head is always full of thoughts.",
    "Even small things feel tiring.",
    "I don’t really talk about this much."
]


# -----------------------------
# CHAT LOOP
# -----------------------------
for i, user_msg in enumerate(user_messages, start=1):
    print(f"\nUSER {i}: {user_msg}")

    ai_reply = generate_ai_reply(
        gemini_client=gemini,
        stage=stage,
        summary=summary,
        user_message=user_msg
    )

    print(f"AI  {i}: {ai_reply}")

    # store conversation
    conversation_log.append(f"User: {user_msg}")
    conversation_log.append(f"AI: {ai_reply}")

    recent_buffer.append(f"User: {user_msg}")
    recent_buffer.append(f"AI: {ai_reply}")

    # -----------------------------
    # UPDATE SUMMARY EVERY 2 USER MESSAGES
    # -----------------------------
    if i % 2 == 0:
        summary = update_summary(
            gemini_client=gemini,
            old_summary=summary,
            recent_messages=recent_buffer
        )
        recent_buffer = []

        print("\n--- SUMMARY UPDATED ---")
        print(summary)
