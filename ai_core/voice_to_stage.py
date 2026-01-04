from stages import AIStage
from voice_signals import (
    VoicePace,
    VoiceVolume,
    VoicePauses,
    VoiceClarity,
    VoiceSignals,
)

def decide_stage_from_voice(signals: VoiceSignals) -> AIStage:
    """
    Decide AI stage based on VOICE SIGNALS only.
    Default is always LISTENING.
    """

    # Very tired / exhausted voice
    if (
        signals.volume == VoiceVolume.VERY_SOFT
        or signals.pace == VoicePace.SLOW
        or signals.pauses == VoicePauses.FREQUENT
        or signals.clarity == VoiceClarity.BROKEN
        or signals.breathy
    ):
        return AIStage.LISTENING

    # Clear + direct voice (still safe)
    return AIStage.LISTENING
