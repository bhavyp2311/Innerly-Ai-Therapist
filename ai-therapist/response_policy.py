from enum import Enum
from phase_rules import PHASE_RULES

class Momentum(Enum):
    LOW = "low"
    MEDIUM = "medium"
    OPEN = "open"


# def get_response_policy(state, phase):
#     """
#     Controls how 'open' or 'closed' the response should feel.
#     """

#     policy = {
#         "max_sentences": 6,
#         "momentum": Momentum.MEDIUM,
#         "allow_extension": True,
#         "avoid_closure": False,
#         "sentence_style": "normal"
#     }

#     # --- Persistence effects ---
#     if state.persistence == "stuck":
#         policy["max_sentences"] = 6
#         policy["momentum"] = Momentum.LOW
#         policy["sentence_style"] = "short"

#     elif state.persistence == "repeating":
#         policy["momentum"] = Momentum.OPEN

#     # --- Emotional load ---
#     if state.emotional_load == "heavy":
#         policy["sentence_style"] = "simple"

#     # --- Phase effects ---
#     if phase.name == "LISTENING":
#         policy["allow_extension"] = False

#     if phase.name == "REFLECTING":
#         policy["allow_extension"] = True

#     if phase.name == "CLARIFYING":
#         policy["max_sentences"] = 6

#     if phase.name == "ORIENTING":
#         policy["momentum"] = Momentum.OPEN

#     if phase.name == "GUIDING":
#         policy["avoid_closure"] = False

#     return policy


def get_response_policy(state, phase):
    # Base policy from phase rules (single source of truth)
    policy = {
        "max_sentences": PHASE_RULES[phase.name].max_sentences,
        "momentum": Momentum.MEDIUM,
        "allow_extension": PHASE_RULES[phase.name].allow_extension,
        "avoid_closure": PHASE_RULES[phase.name].avoid_closure,
        "sentence_style": "normal"
    }

    # --- Persistence effects ---
    if state.persistence == "stuck":
        policy["sentence_style"] = "gentle"
        # do NOT reduce length here

    elif state.persistence == "repeating":
        policy["momentum"] = Momentum.OPEN

    # --- Emotional load ---
    if state.emotional_load == "heavy":
        policy["sentence_style"] = "gentle"
        policy["max_sentences"] += 2  # allow space, not silence

    # --- Phase-specific tuning (soft, not overriding) ---
    if phase.name == "LISTENING":
        policy["momentum"] = Momentum.MEDIUM
        # do NOT force extension here

    if phase.name == "REFLECTING":
        policy["allow_extension"] = True

    if phase.name == "ORIENTING":
        policy["momentum"] = Momentum.OPEN

    if phase.name == "GUIDING":
        policy["momentum"] = Momentum.OPEN
        policy["allow_extension"] = True
        policy["sentence_style"] = "normal"
        policy["avoid_closure"] = False

    return policy
