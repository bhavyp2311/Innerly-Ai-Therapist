# Voice signals are OBSERVABLE features only.
# These do NOT represent emotions or diagnoses.

from enum import Enum


class VoicePace(Enum):
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


class VoiceVolume(Enum):
    VERY_SOFT = "very_soft"
    NORMAL = "normal"


class VoicePauses(Enum):
    FREQUENT = "frequent"
    NORMAL = "normal"


class VoiceClarity(Enum):
    BROKEN = "broken"      # cut-off sentences, trailing
    CLEAR = "clear"


class VoiceSignals:
    def __init__(
        self,
        pace: VoicePace,
        volume: VoiceVolume,
        pauses: VoicePauses,
        clarity: VoiceClarity,
        breathy: bool,
    ):
        self.pace = pace
        self.volume = volume
        self.pauses = pauses
        self.clarity = clarity
        self.breathy = breathy
