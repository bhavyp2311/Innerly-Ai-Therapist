# This file converts STT + audio stats into VoiceSignals
# No emotions, no diagnosis — only observable measurements

from voice_signals import (
    VoiceSignals,
    VoicePace,
    VoiceVolume,
    VoicePauses,
    VoiceClarity,
)

def extract_voice_signals(
    transcript: str,
    words_per_second: float,
    average_pause_ms: int,
    avg_volume_db: float,
    sigh_count: int = 0,
    cut_sentence_ratio: float = 0.0,
) -> VoiceSignals:
    # 1️⃣ Pace
    if words_per_second < 2:
        pace = VoicePace.SLOW
    elif words_per_second > 4:
        pace = VoicePace.FAST
    else:
        pace = VoicePace.NORMAL

    # 2️⃣ Pauses
    pauses = (
        VoicePauses.FREQUENT
        if average_pause_ms > 700
        else VoicePauses.NORMAL
    )

    # 3️⃣ Volume
    volume = (
        VoiceVolume.VERY_SOFT
        if avg_volume_db < -30
        else VoiceVolume.NORMAL
    )

    # 4️⃣ Clarity
    clarity = (
        VoiceClarity.BROKEN
        if transcript.endswith("...")
        or cut_sentence_ratio > 0.4
        else VoiceClarity.CLEAR
    )

    # 5️⃣ Breathy / exhausted (heuristic)
    breathy = (
        sigh_count >= 2
        or (average_pause_ms > 700 and avg_volume_db < -30)
    )

    return VoiceSignals(
        pace=pace,
        volume=volume,
        pauses=pauses,
        clarity=clarity,
        breathy=breathy,
    )
