const express = require("express");
const router = express.Router();
const { pool } = require("../db/db");
const { v4: uuidv4 } = require("uuid");
const { getAIResponse } = require("../services/aiService");

/* ================= CREATE SESSION ================= */
router.post("/session", async (req, res) => {
  try {
    const { user_id } = req.body;
    const session_id = uuidv4();

    await pool.query(
      `INSERT INTO session (session_id, user_id, is_active)
       VALUES ($1, $2, true)`,
      [session_id, user_id]
    );

    res.json({ session_id });
  } catch (err) {
    res.status(500).json({ message: "Failed to create session" });
  }
});

/* ================= STORE USER MESSAGE + TITLE ================= */
router.post("/message/user", async (req, res) => {
  try {
    const { session_id, content } = req.body;
    if (!session_id || !content) {
      return res.status(400).json({ message: "Invalid payload" });
    }

    // store message
    await pool.query(
      `INSERT INTO message (message_id, session_id, role, content)
       VALUES (gen_random_uuid(), $1, 'user', $2)`,
      [session_id, content]
    );

    // set title ONLY ON FIRST MESSAGE
    await pool.query(
      `UPDATE session
       SET title = $1
       WHERE session_id = $2
         AND (title IS NULL OR title = '')`,
      [content.slice(0, 60), session_id]
    );

    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ message: "Failed to store message" });
  }
});

/* ================= AI RESPONSE ================= */
router.post("/message/ai", async (req, res) => {
  try {
    const { session_id, user_message } = req.body;

    const aiData = await getAIResponse({
      session_id,
      message: user_message
    });

    await pool.query(
      `INSERT INTO message (message_id, session_id, role, content)
       VALUES (gen_random_uuid(), $1, 'ai', $2)`,
      [session_id, aiData.message]
    );

    res.json({ ai_message: aiData.message });
  } catch (err) {
    res.status(500).json({ message: "AI failed" });
  }
});

/* ================= SESSION CONTEXT ================= */
router.get("/context/:session_id", async (req, res) => {
  const messages = await pool.query(
    `SELECT role, content FROM message
     WHERE session_id = $1 ORDER BY created_at`,
    [req.params.session_id]
  );

  res.json({ messages: messages.rows });
});

/* ================= SESSION LIST ================= */
router.get("/sessions/:userId", async (req, res) => {
  const result = await pool.query(
    `SELECT session_id, COALESCE(title, 'New Session') AS title, created_at
     FROM session
     WHERE user_id = $1
     ORDER BY created_at DESC`,
    [req.params.userId]
  );

  res.json({ sessions: result.rows });
});

module.exports = router;
