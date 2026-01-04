# signal_extractor.py

from typing import List, Optional
from sentence_transformers import SentenceTransformer, util

class SignalExtractor:
    """
    Detects psychological signals from text using semantic similarity.
    This module ONLY detects signals. It does NOT decide behavior.
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Pattern exemplars (Level 2 semantic matching)
        self.pattern_exemplars = {
            "difficulty_identifying_internal_state": [
                "i dont know what im feeling",
                "hard to put into words",
                "cant really explain it",
                "not sure how to describe this"
            ],
            "repetitive_mental_activity": [
                "thoughts keep looping",
                "my mind doesnt stop",
                "same thoughts again and again",
                "mental noise that never shuts up"
            ],
            "mental_fatigue": [
                "mentally exhausted",
                "tired in my head",
                "brain feels drained",
                "thinking all day is exhausting"
            ]
        }

        # Precompute embeddings
        self.exemplar_embeddings = {
            k: self.model.encode(v, convert_to_tensor=True)
            for k, v in self.pattern_exemplars.items()
        }

    def detect_patterns(self, text: str, threshold: float = 0.6) -> List[str]:
        """
        Returns a list of detected pattern names.
        """
        text_embedding = self.model.encode(text, convert_to_tensor=True)
        detected = []

        for pattern, embeds in self.exemplar_embeddings.items():
            scores = util.cos_sim(text_embedding, embeds)
            if scores.max().item() >= threshold:
                detected.append(pattern)

        return detected
