import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
# model="llama-3.1-8b-instant"

class LLMClient:
    def __init__(
        self,
        model="llama-3.1-8b-instant",
        temperature=0.4,
        max_tokens=400,
    ):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY not found in environment")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical-style AI therapist."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        if not completion.choices:
            return "I'm here with you. We can stay with this for a moment."

        return completion.choices[0].message.content.strip()
