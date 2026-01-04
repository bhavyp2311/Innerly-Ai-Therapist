

import axios from "axios";

export async function getAIResponse({ session_id, message }) {
  try {
    const payload = {
      session_id,
      messages: [
        {
          role: "user",
          content: message
        }
      ],
      summary: null,
      last_process_state: null
    };

    const res = await axios.post(
      "http://localhost:8000/respond",
      payload,
      { headers: { "Content-Type": "application/json" } }
    );

    // FastAPI returns { message: "..." }
    return res.data;

  } catch (err) {
    console.error(
      "AI SERVICE ERROR:",
      err.response?.data || err.message
    );
    throw new Error("AI service failed");
  }
}


