from stages import AIStage
from ai_engine import generate_ai_reply, GeminiClient

# -----------------------------
# TOGGLE
# -----------------------------
USE_REAL_GEMINI = True   # change to False if needed


summary = (
    "User feels tired.\n"
    "Context is mental overload.\n"
    "Pattern shows overthinking."
)

user_message = "I feel lost and tired of thinking so much."
stage = AIStage.LISTENING.value


if USE_REAL_GEMINI:
    gemini_client = GeminiClient()
else:
    class MockGemini:
        def generate(self, prompt):
            return "That sounds exhausting. It feels like your mind hasn’t had much rest."
    gemini_client = MockGemini()


reply = generate_ai_reply(
    gemini_client=gemini_client,
    stage=stage,
    summary=summary,
    user_message=user_message
)

print("\nAI REPLY:\n", reply)

from voice_signals import (
    VoiceSignals,
    VoicePace,
    VoiceVolume,
    VoicePauses,
    VoiceClarity,
)
from voice_to_stage import decide_stage_from_voice

voice_signals = VoiceSignals(
    pace=VoicePace.SLOW,
    volume=VoiceVolume.VERY_SOFT,
    pauses=VoicePauses.FREQUENT,
    clarity=VoiceClarity.BROKEN,
    breathy=True,
)

stage = decide_stage_from_voice(voice_signals)

voice_context = (
    "- pace: slow\n"
    "- volume: very soft\n"
    "- pauses: frequent\n"
    "- clarity: broken\n"
)

reply = generate_ai_reply(
    gemini_client=gemini_client,
    stage=stage.value,
    summary=summary,
    user_message=user_message,
    voice_context=voice_context
)
