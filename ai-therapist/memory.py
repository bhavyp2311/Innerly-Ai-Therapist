# class PatternMemory:
#     def __init__(self, max_words=120):
#         self.summary = ""
#         self.max_words = max_words

#     def update(self, user_text: str, ai_text: str):
#         # Only store signals, not filler
#         text = f"{user_text} {ai_text}"

#         # Remove very short filler turns
#         if len(text.split()) < 4:
#             return

#         combined = f"{self.summary} {text}".strip()
#         words = combined.split()

#         if len(words) > self.max_words:
#             words = words[-self.max_words:]

#         self.summary = " ".join(words)

#     def get(self) -> str:
#         return self.summary or "No clear pattern yet."

# class PatternMemory:
#     def __init__(self):
#         self.patterns = []

#     def update(self, user_text: str, ai_text: str):
#         text = user_text.lower()

#         if any(w in text for w in ["idk", "dont know", "not sure"]):
#             self._add("uncertainty about internal state")

#         if any(w in text for w in ["off", "weird", "wrong"]):
#             self._add("sense that something is wrong without a clear reason")

#         if any(w in text for w in ["overthink", "loop", "spiral", "noise"]):
#             self._add("repetitive or looping thoughts")

#         if any(w in text for w in ["tired", "exhausted", "drained"]):
#             self._add("mental fatigue")

#         if any(w in text for w in ["advice", "tell me", "just chill"]):
#             self._add("feels unheard or rushed by others")

#     def _add(self, pattern: str):
#         if pattern not in self.patterns:
#             self.patterns.append(pattern)

#     def get(self) -> str:
#         if not self.patterns:
#             return "No clear patterns yet."
#         return "Patterns noticed so far:\n- " + "\n- ".join(self.patterns)

# class PatternMemory:
#     def __init__(self):
#         self.patterns = set()
#         self.relational_states = set()
#     def get_active_pattern(self):
#         if self.patterns:
#             return list(self.patterns)[-1]
#         return None

#     def update(self, user_text: str, ai_text: str):
#         t = user_text.lower()

#         # Internal process
#         if any(w in t for w in ["idk", "dont know", "not sure"]):
#             self.patterns.add("difficulty identifying internal state")

#         if any(w in t for w in ["overthink", "loop", "spiral", "noise"]):
#             self.patterns.add("repetitive mental activity")

#         if any(w in t for w in ["tired", "exhausted", "drained"]):
#             self.patterns.add("mental fatigue")

#         # RELATIONAL EXPERIENCE (this is new)
#         if any(w in t for w in ["no one", "nobody", "alone"]):
#             self.relational_states.add("feeling alone with this")

#         if any(w in t for w in ["everyone", "they just", "people say"]):
#             self.relational_states.add("feeling misunderstood by others")

#         if any(w in t for w in ["annoyed at myself", "hate this", "why am i like this"]):
#             self.relational_states.add("self-frustration or self-criticism")

#     def get(self) -> str:
#         parts = []
#         if self.patterns:
#             parts.append("Ongoing patterns:\n- " + "\n- ".join(self.patterns))
#         if self.relational_states:
#             parts.append("Relational experience:\n- " + "\n- ".join(self.relational_states))

#         return "\n\n".join(parts) if parts else "No clear patterns yet."
#     def has_repeated_pattern(self):
#         return len(self.patterns) >= 1

#     def get_active_pattern(self):
#         if self.patterns:
#             return list(self.patterns)[-1]
#         return None






# class PatternMemory:
#     def __init__(self):
#         self.patterns = []
#         self.relational_states = []

#     def _add(self, collection, value):
#         if value not in collection:
#             collection.append(value)

#     def update(self, user_text: str, ai_text: str):
#         t = user_text.lower()

#         # Internal patterns
#         if any(w in t for w in ["idk", "dont know", "not sure"]):
#             self._add(self.patterns, "difficulty identifying internal state")

#         if any(w in t for w in ["overthink", "loop", "spiral", "noise"]):
#             self._add(self.patterns, "repetitive mental activity")

#         if any(w in t for w in ["tired", "exhausted", "drained"]):
#             self._add(self.patterns, "mental fatigue")

#         # Relational experience
#         if any(w in t for w in ["no one", "nobody", "alone"]):
#             self._add(self.relational_states, "feeling alone with this")

#         if any(w in t for w in ["everyone", "they just", "people say"]):
#             self._add(self.relational_states, "feeling misunderstood by others")

#         if any(w in t for w in ["annoyed at myself", "hate this", "why am i like this"]):
#             self._add(self.relational_states, "self-frustration or self-criticism")

#     def has_repeated_pattern(self):
#         return len(self.patterns) >= 2

#     def get_active_pattern(self):
#         if self.patterns:
#             return self.patterns[-1]
#         return None

#     def get(self) -> str:
#         parts = []
#         if self.patterns:
#             parts.append("Ongoing patterns:\n- " + "\n- ".join(self.patterns))
#         if self.relational_states:
#             parts.append("Relational experience:\n- " + "\n- ".join(self.relational_states))
#         return "\n\n".join(parts) if parts else "No clear patterns yet."



class PatternMemory:
    def __init__(self):
        self.pattern_counts = {}
        self.pattern_order = []
        self.relational_states = []
        self.context_anchor = None
        self.context_locked = False

    def _add_pattern(self, value):
        if value not in self.pattern_counts:
            self.pattern_counts[value] = 1
            self.pattern_order.append(value)
        else:
            self.pattern_counts[value] += 1

    def _add_relational(self, value):
        if value not in self.relational_states:
            self.relational_states.append(value)

    def update(self, detected_patterns: list, detected_relations: list = None):
    #     def update(self, user_text: str, ai_text: str):
    # t = user_text.lower()
        for p in detected_patterns:
            self._add_pattern(p)

        if detected_relations:
            for r in detected_relations:
                self._add_relational(r)
        # # Internal patterns
        # if any(w in t for w in ["idk", "dont know", "not sure"]):
        #     self._add_pattern("difficulty identifying internal state")

        # if any(w in t for w in ["overthink", "loop", "spiral", "noise", "again"]):
        #     self._add_pattern("repetitive mental activity")

        # if any(w in t for w in ["tired", "exhausted", "drained"]):
        #     self._add_pattern("mental fatigue")

        # Relational experience


    def has_repeated_pattern(self):
        return any(count >= 2 for count in self.pattern_counts.values())

    def get_active_pattern(self):
        if self.pattern_order:
            return self.pattern_order[-1]
        return None

    def get(self) -> str:
        parts = []
        if self.pattern_order:
            parts.append(
                "Ongoing patterns:\n- " + "\n- ".join(self.pattern_order)
            )
        if self.relational_states:
            parts.append(
                "Relational experience:\n- " + "\n- ".join(self.relational_states)
            )
        return "\n\n".join(parts) if parts else "No clear patterns yet."
