const express = require("express");
const bcrypt = require("bcrypt");
const { v4: uuidv4 } = require("uuid");
const { pool } = require("../db/db");
const { createAndSendOtp } = require("../services/otpService");

const router = express.Router();

/* ================================
   REGISTER
================================ */
router.post("/register", async (req, res) => {
  const { full_name, email, mobile_no, password } = req.body;

  if (!full_name || !email || !mobile_no || !password) {
    return res.status(400).json({ message: "All fields are required" });
  }

  try {
    const exists = await pool.query(
  `SELECT email, mobile_no
   FROM users
   WHERE email = $1 OR mobile_no = $2`,
  [email.trim(), mobile_no.trim()]
);

if (exists.rowCount > 0) {
  const user = exists.rows[0];

  if (user.email === email.trim()) {
    return res.status(409).json({ message: "Email already registered" });
  }

  if (user.mobile_no === mobile_no.trim()) {
    return res.status(409).json({ message: "Mobile number already registered" });
  }
}

    const password_hash = await bcrypt.hash(password, 10);
    const user_id = uuidv4();

    await pool.query(
      `INSERT INTO users
       (user_id, full_name, email, mobile_no, password_hash, is_verified)
       VALUES ($1,$2,$3,$4,$5,false)`,
      [user_id, full_name.trim(), email.trim(), mobile_no.trim(), password_hash]
    );

    await createAndSendOtp(user_id, email.trim(), "REGISTER");

    res.json({ message: "OTP sent to email" });

  } catch (err) {
    console.error("Register error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

/* ================================
   VERIFY REGISTER OTP
================================ */
router.post("/verify-register-otp", async (req, res) => {
  const { email, otp } = req.body;

  if (!email || !otp) {
    return res.status(400).json({ message: "Email and OTP are required" });
  }

  try {
    const result = await pool.query(
      `SELECT o.otp_id, u.user_id
       FROM otp_verification o
       JOIN users u ON u.user_id = o.user_id
       WHERE u.email = $1
         AND o.otp_code = $2
         AND o.purpose = 'REGISTER'
         AND o.is_used = false
         AND o.expires_at > clock_timestamp()
       ORDER BY o.expires_at DESC
       LIMIT 1`,
      [email.trim(), otp.trim()]
    );

    if (result.rowCount === 0) {
      return res.status(400).json({ message: "Invalid or expired OTP" });
    }

    const { otp_id, user_id } = result.rows[0];

    await pool.query(
      "UPDATE users SET is_verified = true WHERE user_id = $1",
      [user_id]
    );

    await pool.query(
      "UPDATE otp_verification SET is_used = true WHERE otp_id = $1",
      [otp_id]
    );

    res.json({ message: "Registration successful" });

  } catch (err) {
    console.error("Verify register OTP error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

/* ================================
   LOGIN WITH PASSWORD
================================ */
router.post("/login-password", async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: "Email and password are required" });
  }

  try {
    const result = await pool.query(
      "SELECT * FROM users WHERE email = $1",
      [email.trim()]
    );

    if (result.rowCount === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    const user = result.rows[0];

    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ message: "Invalid password" });
    }

    res.json({
      user_id: user.user_id,
      full_name: user.full_name,
      message: "Login successful"
    });

  } catch (err) {
    console.error("Login password error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

/* ================================
   LOGIN WITH OTP (SEND)
================================ */
router.post("/login-otp", async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ message: "Email is required" });
  }

  try {
    const result = await pool.query(
      "SELECT user_id FROM users WHERE email = $1",
      [email.trim()]
    );

    if (result.rowCount === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    await createAndSendOtp(result.rows[0].user_id, email.trim(), "LOGIN");

    res.json({ message: "OTP sent to email" });

  } catch (err) {
    console.error("Login OTP error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

/* ================================
   VERIFY LOGIN OTP
================================ */
router.post("/verify-login-otp", async (req, res) => {
  const { email, otp } = req.body;

  if (!email || !otp) {
    return res.status(400).json({ message: "Email and OTP are required" });
  }

  try {
    const result = await pool.query(
      `SELECT o.otp_id, u.user_id, u.full_name
       FROM otp_verification o
       JOIN users u ON u.user_id = o.user_id
       WHERE u.email = $1
         AND o.otp_code = $2
         AND o.purpose = 'LOGIN'
         AND o.is_used = false
         AND o.expires_at > clock_timestamp()
       ORDER BY o.expires_at DESC
       LIMIT 1`,
      [email.trim(), otp.trim()]
    );

    if (result.rowCount === 0) {
      return res.status(400).json({ message: "Invalid or expired OTP" });
    }

    const { otp_id, user_id, full_name } = result.rows[0];

    await pool.query(
      "UPDATE otp_verification SET is_used = true WHERE otp_id = $1",
      [otp_id]
    );

    res.json({
      user_id,
      full_name,
      message: "Login successful"
    });

  } catch (err) {
    console.error("Verify login OTP error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

module.exports = router;