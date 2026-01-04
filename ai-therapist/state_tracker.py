# class StateTracker:
#     def __init__(self):
#         self.last_user_input = None
#         self.raw_text = ""
#         self.user_requested_guidance = False
#         self.turn_count = 0
#         self.persistence = "new"          # new | repeating | stuck
#         self.emotional_load = "light"     # light | heavy
#         self.self_frustration = "low"     # low | high

#         self._heavy_streak = 0
#         self._repeat_streak = 0

#     def update(self, user_text: str):
#         text = user_text.lower()
#         self.raw_text = text

#         # --- Persistence ---
#         if self.last_user_input:
#             if any(w in text for w in ["still", "again", "keeps", "always"]):
#                 self._repeat_streak += 1
#             else:
#                 self._repeat_streak = 0

#             if self._repeat_streak >= 2:
#                 self.persistence = "stuck"
#             elif self._repeat_streak == 1:
#                 self.persistence = "repeating"
#             else:
#                 self.persistence = "new"

#         load_score = estimate_emotional_load(text)

#         if load_score >= 2:
#             self._heavy_streak += 1
#         else:
#             self._heavy_streak = max(0, self._heavy_streak - 1)

#         self.emotional_load = "heavy" if self._heavy_streak >= 2 else "light"


#         # --- Self-directed frustration ---
#         if any(w in text for w in [
#             "annoyed at myself", "why am i like this",
#             "i hate myself", "stupid", "fed up with myself"
#         ]):
#             self.self_frustration = "high"
#         else:
#             self.self_frustration = "low"

#         # --- Explicit guidance request ---
#         guidance_triggers = [
#             "what should i do",
#             "how do i deal",
#             "help me figure out",
#             "i need advice",
#             "tell me what to do",
#             "what am i supposed to do"
#         ]
#         self.user_requested_guidance = any(t in text for t in guidance_triggers)
#         if self.persistence == "new":
#             self._repeat_streak = 0

#         self.last_user_input = text
#         self.turn_count += 1
#     def is_stable(self):
#         return (
#             self.emotional_load != "heavy"
#             and self.self_frustration != "high"
#         )

#     def get_state(self) -> str:
#         return (
#             f"Current interaction state:\n"
#             f"- persistence: {self.persistence}\n"
#             f"- emotional load: {self.emotional_load}\n"
#             f"- self-frustration: {self.self_frustration}"
#         )
# state_tracker.py

from typing import Optional


# -----------------------------
# Helper signal functions
# -----------------------------

def semantic_overlap(a: str, b: str) -> float:
    """
    Rough semantic overlap using word set similarity.
    Detects repeated meaning without relying on trigger words.
    """
    a_words = set(a.split())
    b_words = set(b.split())

    if not a_words or not b_words:
        return 0.0

    return len(a_words & b_words) / len(a_words | b_words)


def estimate_emotional_load(text: str) -> int:
    """
    Estimates emotional load based on linguistic signals,
    not explicit emotion keywords.
    """
    score = 0
    words = text.split()

    # Longer messages often indicate heavier processing
    if len(words) > 35:
        score += 1

    # Repeated emotional verbs / internal focus
    score += text.count("feel") // 2
    score += text.count("thinking") // 2

    # Somatic / mental references (non-keyword fatigue)
    somatic_markers = ["mind", "head", "body", "sleep", "chest"]
    score += sum(1 for w in somatic_markers if w in text)

    return score


def self_reference_intensity(text: str) -> int:
    """
    Detects self-frustration through inward pressure and self-reference,
    not insults or explicit self-hate.
    """
    score = 0

    # First-person density
    score += text.count("i ")

    # Modal pressure / self-directed tension
    pressure_markers = ["should", "can't", "why", "wrong", "stuck"]
    score += sum(1 for w in pressure_markers if w in text)

    return score


# -----------------------------
# State Tracker
# -----------------------------

class StateTracker:
    def __init__(self):
        self.last_user_input: Optional[str] = None
        self.raw_text = ""
        self.user_requested_guidance = False
        self.turn_count = 0
        self.context_anchor = None
        self.context_locked = False
        self.phase_turns = 0


        # Public state
        self.persistence = "new"          # new | repeating | stuck
        self.emotional_load = "light"     # light | heavy
        self.self_frustration = "low"     # low | high

        # Internal streaks
        self._heavy_streak = 0
        self._repeat_streak = 0

    def update(self, user_text: str):
        text = user_text.lower().strip()
        self.raw_text = text
        t = user_text.lower()

    # -------- TOPIC LOCK (NEW) --------
        if not self.context_locked:
            if any(w in t for w in ["work", "job", "office", "deadline", "manager"]):
                self.context_anchor = "work"
                self.context_locked = True

            elif any(w in t for w in ["college", "exam", "semester", "study"]):
                self.context_anchor = "studies"
                self.context_locked = True

            elif any(w in t for w in ["relationship", "partner", "ex", "dating"]):
                self.context_anchor = "relationships"
                self.context_locked = True

            elif any(w in t for w in ["family", "parents", "home"]):
                self.context_anchor = "family"
                self.context_locked = True
            # ---------- EXPLICIT TOPIC SHIFT ----------
        if any(w in t for w in ["actually", "another thing", "different issue"]):
            if any(w in t for w in ["health", "money", "family", "relationship"]):
                self.context_anchor = None
                self.context_locked = False    
        # -----------------------------
        # Persistence (semantic repetition)
        # -----------------------------
        # if self.last_user_input:
        #     overlap = semantic_overlap(text, self.last_user_input)

        #     if overlap > 0.2:
        #         self._repeat_streak += 1
        #     else:
        #         self._repeat_streak = 0

        # if self._repeat_streak >= 2:
        #     self.persistence = "stuck"
        # elif self._repeat_streak == 1:
        #     self.persistence = "repeating"
        # else:
        #     self.persistence = "new"

        # -----------------------------
        # Emotional load (pattern-based)
        # -----------------------------
        load_score = estimate_emotional_load(text)

        if load_score >= 2:
            self._heavy_streak += 1
        else:
            self._heavy_streak = max(0, self._heavy_streak - 1)

        self.emotional_load = "heavy" if self._heavy_streak >= 2 else "light"

        # -----------------------------
        # Self-directed frustration
        # -----------------------------
        if self_reference_intensity(text) >= 3:
            self.self_frustration = "high"
        else:
            self.self_frustration = "low"

        # -----------------------------
        # Explicit guidance request
        # -----------------------------
        guidance_markers = [
            "what should i do",
            "how do i deal",
            "help me figure",
            "tell me what to do",
            "what am i supposed to do"
        ]
        self.user_requested_guidance = any(m in text for m in guidance_markers)

        # -----------------------------
        # Final bookkeeping
        # -----------------------------
        self.last_user_input = text
        self.turn_count += 1

    def is_stable(self):
        return (
            self.emotional_load != "heavy"
            and self.self_frustration != "high"
        )

    def get_state(self) -> str:
        return (
            f"Current interaction state:\n"
            f"- persistence: {self.persistence}\n"
            f"- emotional load: {self.emotional_load}\n"
            f"- self-frustration: {self.self_frustration}"
        )
    def get_context(self):
        return self.context_anchor
    # def update_persistence(self, pattern_memory):
    #     """
    #     Monotonic persistence:
    #     new → repeating → stuck
    #     Never resets automatically.
    # """
    #     if pattern_memory.has_repeated_pattern():
    #         if self.persistence == "new":
    #             self.persistence = "repeating"
    #         elif self.persistence == "repeating":
    #             self.persistence = "stuck"
    def update_persistence(self, pattern_memory):
        if pattern_memory.has_repeated_pattern():
            if self.persistence == "new":
                self.persistence = "repeating"
            elif self.persistence == "repeating":
                self.persistence = "stuck"
    
        # NEW: escalation if same active pattern dominates
        active = pattern_memory.get_active_pattern()
        if active and pattern_memory.pattern_counts.get(active, 0) >= 3:
            self.persistence = "stuck"


