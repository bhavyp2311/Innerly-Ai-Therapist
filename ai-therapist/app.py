from fastapi import FastAPI
from pydantic import BaseModel

# ✅ IMPORT YOUR CORE AI FUNCTION
from engine import respond



app = FastAPI(title="AI Therapy Engine")


# ===============================
# REQUEST SCHEMA
# ===============================
class RespondRequest(BaseModel):
    session_id: str
    messages: list
    summary: str | None = None
    last_process_state: dict | None = None


# ===============================
# AI RESPOND ENDPOINT
# ===============================
@app.post("/respond")
def ai_respond(req: RespondRequest):
    last_user_message = req.messages[-1]["content"]

    ai_text = respond(last_user_message)

    return {
        "message": ai_text
    }