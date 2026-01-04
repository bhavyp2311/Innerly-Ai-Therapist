from enum import Enum

from llm_client import LLMClient
from memory import PatternMemory
from state_tracker import StateTracker
from response_policy import Momentum
from response_policy import get_response_policy
from phase_rules import PHASE_RULES
from intention_rules import INTENTION_RULES
from scenario_memory import ScenarioMemory
from phase_prompts import PHASE_PROMPTS
from signal_extractor import SignalExtractor
from memory import PatternMemory

signal_extractor = SignalExtractor()
pattern_memory = PatternMemory()

# --------------------------------------------------
# Phase definition
# --------------------------------------------------

class Phase(Enum):
    LISTENING = "listening"
    REFLECTING = "reflecting"
    CLARIFYING = "clarifying"
    ORIENTING = "orienting"
    GUIDING = "guiding"


# --------------------------------------------------
# Global state (single-session)
# --------------------------------------------------
scenario_memory = ScenarioMemory()
state_tracker = StateTracker()
memory = PatternMemory()
llm_client = LLMClient()


current_phase = Phase.LISTENING


# --------------------------------------------------
# System prompt (STATIC — no runtime variables here)
# --------------------------------------------------

SYSTEM_PROMPT = """
Avoid reassurance and normalization phrases such as:
“it’s understandable”, “many people feel”, “remember that”, “everyone”, “this is common”.
Presence should come from staying with the experience, not from reassurance.
You are acting as a therapist-like conversational presence.
Responses do not need to start with “It sounds like” or similar constructions.
It is allowed to begin by directly acknowledging the user’s experience
using natural, varied sentence openings.
It is allowed to begin responses with phrases like:
- “You’re noticing…”
- “There’s this sense of…”
- “Lately, it feels like…”
- “From what you’re describing…”
- “What you’re carrying sounds like…”

Your role is not to solve problems, explain causes, or instruct the user.
Your role is to stay with the user’s lived experience in a grounded, steady way.
Warmth should be conveyed through specificity and attentiveness,
Gentle acknowledgment is allowed when grounded in the user’s words.
Each response should end with a single, gentle question that invites the user to continue.
The question should:
- Be directly grounded in what the user has already shared
- Invite description or noticing, not explanation or solutions
- Help clarify patterns, context, or lived experience
- Avoid "why" questions and avoid problem-solving

- Avoid instructions
- Acknowledge emotional weight by describing the experience,
  not by reassuring, validating, or evaluating it
- No metaphors or poetic language

Use plain, concrete, everyday wording.
- Reassurance is allowed only when explicitly permitted by the current phase
When asking questions, prefer questions that invite continuation
rather than explanation, causes, or solutions.
- Early responses should read like neutral observations, not interviews.


"""


# --------------------------------------------------
# Intention logic
# --------------------------------------------------

def choose_intention(state: StateTracker) -> str:
    if state.persistence == "stuck":
        return "containment"
    if state.self_frustration == "high":
        return "validation"
    if state.emotional_load == "heavy":
        return "grounding"
    if state.persistence == "repeating":
        return "linking"
    return "naming"


def choose_intention_from_phase(phase: Phase, state: StateTracker) -> str:
    base = choose_intention(state)

    if phase == Phase.LISTENING:
        return "naming"

    if phase == Phase.REFLECTING:
        return "linking" if base != "containment" else "containment"

    if phase == Phase.CLARIFYING:
        return "clarifying"

    if phase == Phase.ORIENTING:
        return "orienting"

    if phase == Phase.GUIDING:
        return "guiding"

    return base


# --------------------------------------------------
# Phase progression logic
# --------------------------------------------------

def advance_phase(state: StateTracker, memory: PatternMemory, phase: Phase) -> Phase:
    """
    Phase transitions are driven by conversational signals,
    not by perfect stability or artificial thresholds.
    """

    # LISTENING → REFLECTING
    # Trigger when the same internal process appears more than once
    if phase == Phase.LISTENING:
        if memory.has_repeated_pattern():
            return Phase.REFLECTING

    # REFLECTING → CLARIFYING
    # Trigger when repetition is clear and starting to feel burdensome
    if phase == Phase.REFLECTING:
        if state.persistence == "stuck" and state.self_frustration == "high":
            return Phase.GUIDING
        if state.persistence == "repeating":
            return Phase.CLARIFYING

    # CLARIFYING → ORIENTING
    # Trigger when duration or entrenchment appears
    if phase == Phase.CLARIFYING:
        if (
            state.turn_count >= 4
            or state.persistence == "stuck"
        ):
            return Phase.ORIENTING

    # ORIENTING → GUIDING
    # Trigger only on explicit readiness
    # ORIENTING → GUIDING
    if phase == Phase.ORIENTING:
        if state.persistence == "stuck" and state.self_frustration == "high":
            return Phase.GUIDING


    return phase



# --------------------------------------------------
# Main response function
# --------------------------------------------------

def respond(user_text: str, debug: bool = False) -> str:
    global current_phase
    # --- SIGNAL EXTRACTION (NEW) ---
    detected_patterns = signal_extractor.detect_patterns(user_text)
    pattern_memory.update(detected_patterns)

    # -----------------------------
    # 1. Update state + pattern trackers
    # -----------------------------
    state_tracker.update(user_text)
    state_tracker.update_persistence(pattern_memory)
    # -----------------------------
    # 2. Update rolling scenario memory (raw inputs)
    # -----------------------------
    scenario_memory.add_input(user_text)

    # -----------------------------
    # 3. Phase transition
    # -----------------------------
    prev_phase = current_phase
    current_phase = advance_phase(state_tracker, memory, current_phase)

    if debug:
        print(
            "[PHASE CHECK]",
            "from:", prev_phase.value,
            "to:", current_phase.value
        )

    phase_used = current_phase

    # -----------------------------
    # 4. Periodic scenario summarization (every 2 turns)
    # -----------------------------
    if state_tracker.turn_count % 2 == 0:
        scenario_memory.update_summary(
            lambda t: summarize_recent_context(t, llm_client)
        )

    # -----------------------------
    # 5. State-based stance (early exploration)
    # -----------------------------
    state_stance = ""

    if current_phase == Phase.LISTENING and (
    state_tracker.persistence == "new"
    and state_tracker.emotional_load == "light"
    and state_tracker.self_frustration == "low"
    ):
        state_stance = """
State-specific stance:
- Treat this as early exploration, not distress
- Stay descriptive and observational
- Avoid reassurance or soothing language
- Do not intensify emotional framing
- Do not push the conversation forward
"""

    # -----------------------------
    # 6. State-based HARD constraints (apply across all phases)
    # -----------------------------
    state_constraints = ""

    # Heavy emotional load
    if state_tracker.emotional_load == "heavy":
        state_constraints += """
- Avoid use metaphors, imagery, or poetic language
- Prefer open-ended phrasing over conclusions
- It is allowed to leave the response open-ended without resolving
"""

    # Stuck persistence
    if state_tracker.persistence == "stuck":
        state_constraints += """
- Avoid repeating the same reflection verbatim
- Gently shift toward orientation rather than looping
"""

    # High self-frustration (NON-NEGOTIABLE continuation)
    if state_tracker.self_frustration == "high":
        state_constraints += """
- It is allowed to acknowledge frustration or self-criticism plainly
- Do NOT minimize, dismiss, or fix the experience
- Do NOT offer advice or solutions
"""

    # -----------------------------
    # 7. Fetch scenario summary (rolling context)
    # -----------------------------
    past_scenarios = scenario_memory.get()

    scenario_block = ""
    if past_scenarios:
        scenario_block = (
            "Recent ongoing context to stay consistent with:\n- "
            + "\n- ".join(past_scenarios)
            + "\n\nUse this to maintain continuity and depth, without over-analyzing it."
        )

    # -----------------------------
    # 8. Intention + policy selection
    # -----------------------------
    intention = choose_intention_from_phase(current_phase, state_tracker)

    phase_rule = PHASE_RULES[current_phase.name]
    intention_rule = INTENTION_RULES[intention]
    policy = get_response_policy(state_tracker, current_phase)
    # Allow longer responses once context exists
    if scenario_memory.get():
        policy["allow_extension"] = True
    if len(scenario_memory.get()) >= 3:
        policy["momentum"] = Momentum.OPEN


    active_pattern = memory.get_active_pattern()
    phase_prompt = PHASE_PROMPTS[current_phase.name]
        # -----------------------------
    # 8.5 Topic enforcement (NEW)
    # -----------------------------
    topic = state_tracker.context_anchor

    topic_block = ""
    if topic:
        topic_block = f"""
Conversation topic (do not drift):
- {topic}

All responses in this phase must stay grounded in this topic.
If the user asks a general or abstract question, interpret it
through this topic unless the user explicitly shifts focus.
"""

    # -----------------------------
    # 9. Build final prompt
    # -----------------------------
    guidance_integration_block = ""

    if current_phase == Phase.GUIDING:
        guidance_integration_block = """
    Before offering guidance:
    - Briefly integrate the key pattern and the recent ongoing context
    - This integration should be 1–2 sentences
    - It should reflect what has been most persistent or heavy
    - Do not add new information
    """

    prompt = f"""
{SYSTEM_PROMPT}

Current phase:
{phase_used.value}


Stay close to this experience and avoid drifting into general explanations.

{guidance_integration_block}

The following phase stance OVERRIDES default conversational behavior:
{phase_prompt}

Cadence:
- It is allowed to develop a thought across multiple sentences.
- Do not resolve or conclude the experience prematurely.

User:
{user_text}
"""


    # -----------------------------
    # 10. Generate response
    # -----------------------------
    response = llm_client.generate(prompt).strip()

    # -----------------------------
    # 11. Update pattern memory with full turn
    # -----------------------------
    memory.update(user_text, response)
    state_tracker.update_persistence(memory)
        # ---- Debug ----
    if debug:
        print("\n[DEBUG]")
        print("PHASE:", phase_used.name)
        print("INTENTION:", intention)
        print("[DEBUG SIGNALS]", detected_patterns)
        print("[DEBUG PATTERN COUNTS]", pattern_memory.pattern_counts)
        print("ACTIVE PATTERN:", active_pattern)
        print(f"Scenario summary: {scenario_memory.get()}")
        print(state_tracker.get_state())
        print()
    return response

def summarize_recent_context(text: str, llm):
    prompt = f"""
Summarize the following recent user messages into ONE sentence.
Rules:
- Use first-person implied framing (e.g., “they describe…” is NOT allowed)
- No clinical or diagnostic language
- Describe experience as lived, not observed
- Focus on continuity over time
- Do NOT use third-person observer framing
- Write as if the experience is being described from inside


Text:
{text}

Return only the summary sentence.
"""
    return llm.generate(prompt).strip()



# from enum import Enum

# from llm_client import LLMClient
# from state_tracker import StateTracker
# from response_policy import get_response_policy
# from phase_rules import PHASE_RULES
# from intention_rules import INTENTION_RULES
# from scenario_memory import ScenarioMemory
# from phase_prompts import PHASE_PROMPTS
# from signal_extractor import SignalExtractor
# from memory import PatternMemory


# # --------------------------------------------------
# # Phase definition
# # --------------------------------------------------

# class Phase(Enum):
#     LISTENING = "listening"
#     REFLECTING = "reflecting"
#     CLARIFYING = "clarifying"
#     ORIENTING = "orienting"
#     GUIDING = "guiding"


# PHASE_MAX_TOKENS = {
#     Phase.LISTENING: 300,
#     Phase.REFLECTING: 350,
#     Phase.CLARIFYING: 400,
#     Phase.ORIENTING: 500,
#     Phase.GUIDING: 800,
# }


# # --------------------------------------------------
# # Single-session state (SINGLE SOURCE OF TRUTH)
# # --------------------------------------------------

# state_tracker = StateTracker()
# scenario_memory = ScenarioMemory()
# pattern_memory = PatternMemory()
# signal_extractor = SignalExtractor()
# llm_client = LLMClient()

# current_phase = Phase.LISTENING
# phase_turns = 0


# # --------------------------------------------------
# # SYSTEM PROMPT (STATIC ONLY)
# # --------------------------------------------------

# SYSTEM_PROMPT = """
# You are a therapist-like conversational presence.
# Stay with lived experience. Do not explain, diagnose, or instruct.
# Avoid reassurance and normalization.
# Use plain, concrete language.
# End with one gentle continuation question.

# When persistence is "stuck":
# - Prefer noticing statements over questions
# - Questions should invite grounding or narrowing, not exploration
# """


# # --------------------------------------------------
# # Intention logic
# # --------------------------------------------------

# def choose_intention(phase: Phase) -> str:
#     return {
#         Phase.LISTENING: "naming",
#         Phase.REFLECTING: "linking",
#         Phase.CLARIFYING: "clarifying",
#         Phase.ORIENTING: "orienting",
#         Phase.GUIDING: "guiding",
#     }[phase]


# # --------------------------------------------------
# # Phase progression (STRICT + SAFE)
# # --------------------------------------------------

# def advance_phase(state: StateTracker, memory: PatternMemory):
#     global current_phase, phase_turns

#     next_phase = current_phase

#     if current_phase == Phase.LISTENING:
#         if memory.has_repeated_pattern():
#             next_phase = Phase.REFLECTING

#     elif current_phase == Phase.REFLECTING:
#         if state.persistence in ("repeating", "stuck"):
#             next_phase = Phase.CLARIFYING

#     elif current_phase == Phase.CLARIFYING:
#         if phase_turns >= 2:
#             next_phase = Phase.ORIENTING

#     elif current_phase == Phase.ORIENTING:
#         if (
#             state.user_requested_guidance
#             or (
#                 state.persistence == "stuck"
#                 and memory.get_active_pattern()
#                 and memory.pattern_counts.get(memory.get_active_pattern(), 0) >= 3
#                 and state.emotional_load != "heavy"
#             )
#         ):
#             next_phase = Phase.GUIDING

#     if next_phase != current_phase:
#         phase_turns = 0
#         return next_phase

#     return current_phase


# # --------------------------------------------------
# # Main response loop
# # --------------------------------------------------

# def respond(user_text: str, debug: bool = False) -> str:
#     global current_phase, phase_turns

#     # 1. Detect patterns
#     detected_patterns = signal_extractor.detect_patterns(user_text)
#     pattern_memory.update(detected_patterns)

#     # 2. Update state
#     state_tracker.update(user_text)
#     state_tracker.update_persistence(pattern_memory)

#     # 3. Scenario memory
#     scenario_memory.add_input(user_text)
#     if state_tracker.turn_count % 2 == 0:
#         scenario_memory.update_summary(
#             lambda t: summarize_recent_context(t, llm_client)
#         )

#     # 4. Phase transition
#     prev_phase = current_phase
#     current_phase = advance_phase(state_tracker, pattern_memory)
#     phase_turns += 1

#     # 5. Intention & policy
#     intention = choose_intention(current_phase)
#     policy = get_response_policy(state_tracker, current_phase)

#     # 6. Prompt assembly
#     scenario_block = ""
#     if scenario_memory.get():
#         scenario_block = "Recent context:\n- " + "\n- ".join(scenario_memory.get())

#     persistence_block = f"""
# Interaction continuity:
# - Persistence level: {state_tracker.persistence}
# """

#     prompt = f"""
# {SYSTEM_PROMPT}
# {persistence_block}

# Current phase: {current_phase.value}
# Phase stance:
# {PHASE_PROMPTS[current_phase.name]}

# Active pattern:
# {pattern_memory.get_active_pattern()}

# {scenario_block}

# User:
# {user_text}
# """

#     # 7. Generate
#     max_tokens = PHASE_MAX_TOKENS[current_phase]
#     response = llm_client.generate(prompt, max_tokens=max_tokens).strip()

#     # 8. DEBUG OUTPUT
#     if debug:
#         print("\n===== DEBUG STATE =====")
#         print("USER TEXT:", user_text)
#         print("PHASE:", prev_phase.value, "→", current_phase.value)
#         print("PHASE TURNS:", phase_turns)
#         print("INTENTION:", intention)
#         print("PERSISTENCE:", state_tracker.persistence)
#         print("EMOTIONAL LOAD:", state_tracker.emotional_load)
#         print("SELF FRUSTRATION:", state_tracker.self_frustration)
#         print("USER ASKED GUIDANCE:", state_tracker.user_requested_guidance)
#         print("DETECTED PATTERNS:", detected_patterns)
#         print("PATTERN COUNTS:", pattern_memory.pattern_counts)
#         print("ACTIVE PATTERN:", pattern_memory.get_active_pattern())
#         print("SCENARIO MEMORY:", scenario_memory.get())
#         print("POLICY:", policy)
#         print("MAX TOKENS:", max_tokens)
#         print("=======================\n")

#     return response


# # --------------------------------------------------
# # Summarization helper
# # --------------------------------------------------

# def summarize_recent_context(text: str, llm):
#     prompt = f"""
# Summarize the following user experience into ONE sentence.
# No diagnosis. No explanation. First-person implied.

# Text:
# {text}
# """
#     return llm.generate(prompt, max_tokens=120).strip()
