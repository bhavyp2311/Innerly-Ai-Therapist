# import os
# from dotenv import load_dotenv
# from google import genai

# from prompts import build_response_prompt
# from validator import is_valid_response

# from stages import AIStage
# from typing_to_stage import decide_stage_from_typing
# from voice_to_stage import decide_stage_from_voice
# from summary_engine import SummaryEngine
# from typing_to_stage import decide_stage_from_typing

# load_dotenv()

# FALLBACK_MESSAGE = "I’m here with you. Please try sending that again."
# summary_engine = SummaryEngine()


# # -----------------------------
# # GEMINI CLIENT
# # -----------------------------
# class GeminiClient:
#     def __init__(self, model_name="models/gemini-flash-latest"):
#         api_key = os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not found in .env")

#         self.client = genai.Client(api_key=api_key)
#         self.model_name = model_name

#     def generate(self, prompt: str) -> str:
#         response = self.client.models.generate_content(
#             model=self.model_name,
#             contents=prompt
#         )
#         return response.text.strip()
#     def decide_final_stage(user_message, voice_signals=None):
#         """
#         Central brain for stage switching.
#         """

#     # 1️⃣ Explicit intent from typing
#         text_stage = decide_stage_from_typing(user_message)
    
#         if text_stage == AIStage.GUIDANCE:
#             return AIStage.GUIDANCE
    
#         if text_stage == AIStage.UNDERSTANDING:
#             return AIStage.UNDERSTANDING
    
#         # 2️⃣ Voice can only enforce LISTENING
#         if voice_signals is not None:
#             voice_stage = decide_stage_from_voice(voice_signals)
#             if voice_stage == AIStage.LISTENING:
#                 return AIStage.LISTENING
    
#         # 3️⃣ Use summary to unlock understanding
#         if summary_engine.has_enough_context():
#             return AIStage.UNDERSTANDING
    
#         # 4️⃣ Default
#         return AIStage.LISTENING

# # -----------------------------
# # AI REPLY GENERATOR
# # -----------------------------
# def generate_ai_reply(
#     gemini_client,
#     user_message,
#     voice_signals=None
# ):
#     # update turn count
#     summary_engine.increment_turn()

#     # decide stage internally
    

#     text_stage = decide_stage_from_typing(user_message)

#     # Explicit intent wins
#     if text_stage == AIStage.GUIDANCE:
#         stage = AIStage.GUIDANCE
    
#     elif text_stage == AIStage.UNDERSTANDING:
#         stage = AIStage.UNDERSTANDING
    
#     # Earned understanding via summary (after enough listening)
#     elif summary_engine.has_enough_context():
#         stage = AIStage.UNDERSTANDING
    
#     else:
#         stage = AIStage.LISTENING


#     # build prompt
#     prompt = build_response_prompt(
#         stage=stage,
#         summary=summary_engine.get_summary(),
#         user_message=user_message
#     )

#     try:
#         text = gemini_client.generate(prompt)

#         if not is_valid_response(text):
#             return FALLBACK_MESSAGE

#         # update summary every 2–3 turns
#         if summary_engine.should_update_summary():
#             new_summary = summary_engine.generate_summary(
#                 user_message, text
#             )
#             summary_engine.update_summary(new_summary)

#         return text

#     except Exception as e:
#         print("AI ERROR:", e)
#         return FALLBACK_MESSAGE



import os
from dotenv import load_dotenv
from google import genai

from prompts import build_response_prompt
from validator import is_valid_response
from stages import AIStage
from typing_to_stage import decide_stage_from_typing
from voice_to_stage import decide_stage_from_voice
from summary_engine import SummaryEngine

load_dotenv()

FALLBACK_MESSAGE = "I’m here with you. Please try sending that again."
summary_engine = SummaryEngine()

# -----------------------------
# GEMINI CLIENT
# -----------------------------
class GeminiClient:
    def __init__(self, model_name="models/gemini-flash-latest"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text.strip()


# -----------------------------
# STAGE DECISION (OUTSIDE CLASS)
# -----------------------------
def decide_final_stage(user_message, voice_signals=None):
    text_stage = decide_stage_from_typing(user_message)

    if text_stage == AIStage.GUIDANCE:
        return AIStage.GUIDANCE

    if text_stage == AIStage.UNDERSTANDING:
        return AIStage.UNDERSTANDING

    if voice_signals is not None:
        voice_stage = decide_stage_from_voice(voice_signals)
        if voice_stage == AIStage.LISTENING:
            return AIStage.LISTENING

    if summary_engine.has_enough_context():
        return AIStage.UNDERSTANDING

    return AIStage.LISTENING


# -----------------------------
# AI REPLY GENERATOR
# -----------------------------
def generate_ai_reply(
    gemini_client,
    user_message,
    voice_signals=None
):
    summary_engine.increment_turn()

    stage = decide_final_stage(user_message, voice_signals)

    prompt = build_response_prompt(
        stage=stage,
        summary=summary_engine.get_summary(),
        user_message=user_message
    )

    try:
        text = gemini_client.generate(prompt)

        if not is_valid_response(text):
            return FALLBACK_MESSAGE

        if summary_engine.should_update_summary():
            new_summary = summary_engine.generate_summary(
                gemini_client,
                [user_message, text]
            )
            summary_engine.update_summary(new_summary)

        return text

    except Exception as e:
        print("AI ERROR:", e)
        return FALLBACK_MESSAGE