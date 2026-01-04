from enum import Enum

class PhaseRule:
    def __init__(
        self,
        max_sentences,
        allow_linking,
        allow_time_reference,
        allow_extension,
        avoid_closure
    ):
        self.max_sentences = max_sentences
        self.allow_linking = allow_linking
        self.allow_time_reference = allow_time_reference
        self.allow_extension = allow_extension
        self.avoid_closure = avoid_closure


PHASE_RULES = {
    "LISTENING": PhaseRule(
        max_sentences=8,
        allow_linking=True,
        allow_time_reference=False,
        allow_extension=True,
        avoid_closure=True
    ),
    "REFLECTING": PhaseRule(
        max_sentences=8,
        allow_linking=True,
        allow_time_reference=False,
        allow_extension=True,
        avoid_closure=True
    ),
    "CLARIFYING": PhaseRule(
        max_sentences=12,
        allow_linking=True,
        allow_time_reference=False,
        allow_extension=True,
        avoid_closure=True
    ),
    "ORIENTING": PhaseRule(
        max_sentences=16,
        allow_linking=True,
        allow_time_reference=True,
        allow_extension=True,
        avoid_closure=True
    ),
    "GUIDING": PhaseRule(
        max_sentences=25 ,
        allow_linking=True,
        allow_time_reference=True,
        allow_extension=False,
        avoid_closure=False
    ),
}
