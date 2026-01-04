const express = require("express");
const router = express.Router();
const axios = require("axios");
const { pool } = require("../db/db");

/**
 * INTERNAL AI ORCHESTRATION
 * NOT FOR FRONTEND / POSTMAN
 */
router.post("/respond", async (req, res) => {
  try {
    const { session_id } = req.body;

    if (!session_id) {
      return res.status(400).json({ message: "session_id required" });
    }

    // 1️⃣ Fetch all messages
    const messagesResult = await pool.query(
      `SELECT role, content
       FROM message
       WHERE session_id = $1
       ORDER BY message_id ASC`,
      [session_id]
    );

    // 2️⃣ Fetch latest summary
    const summaryResult = await pool.query(
      `SELECT summary_text
       FROM session_summary
       WHERE session_id = $1
       ORDER BY updated_at DESC
       LIMIT 1`,
      [session_id]
    );

    // 3️⃣ Fetch last process state
    const processResult = await pool.query(
      `SELECT *
       FROM therapeutic_process_state
       WHERE session_id = $1
       ORDER BY updated_at DESC
       LIMIT 1`,
      [session_id]
    );

    // 4️⃣ Send to Python AI
    const aiResponse = await axios.post(
      "http://localhost:8000/respond",
      {
        session_id,
        messages: messagesResult.rows,
        summary: summaryResult.rows[0]?.summary_text || null,
        last_process_state: processResult.rows[0] || null
      },
      { timeout: 120000 }
    );

    // 5️⃣ Return AI response to backend caller
    res.json(aiResponse.data);

  } catch (err) {
    console.error("AI respond error:", err.message);
    res.status(500).json({ message: "AI respond failed" });
  }
});

router.post("/summarize", async (req, res) => {
  try {
    const { session_id } = req.body;

    if (!session_id) {
      return res.status(400).json({ message: "session_id required" });
    }

    // 1️⃣ Fetch conversation
    const msgRes = await pool.query(
      `SELECT role, content
       FROM message
       WHERE session_id = $1
       ORDER BY created_at ASC`,
      [session_id]
    );

    const messages = msgRes.rows;

    if (messages.length < 3) {
      return res.json({ message: "Not enough messages to summarize" });
    }

    // 2️⃣ Call PYTHON summary service
    const aiRes = await axios.post("http://localhost:8000/summarize", {
      messages
    });

    const summaryText = aiRes.data.summary; // 🔥 THIS MUST EXIST

    if (!summaryText) {
      throw new Error("AI summary missing");
    }

    // 3️⃣ UPSERT into session_summary
    await pool.query(
      `
      INSERT INTO session_summary (session_id, summary_text)
      VALUES ($1, $2)
      ON CONFLICT (session_id)
      DO UPDATE SET
        summary_text = EXCLUDED.summary_text,
        updated_at = CURRENT_TIMESTAMP
      `,
      [session_id, summaryText]
    );

    res.json({
      message: "Summary updated",
      summary_text: summaryText
    });

  } catch (err) {
    console.error("SUMMARY ERROR:", err);
    res.status(500).json({ message: "Summary failed" });
  }
});



module.exports = router;
