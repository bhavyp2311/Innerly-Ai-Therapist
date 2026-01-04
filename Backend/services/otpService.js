require("dotenv").config();
const nodemailer = require("nodemailer");
const { v4: uuidv4 } = require("uuid");
const { pool } = require("../db/db");

/* ================================
   OTP GENERATOR
================================ */
function generateOTP() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

/* ================================
   MAIL TRANSPORT
================================ */
const transporter = nodemailer.createTransport({
  host: process.env.MAIL_HOST,
  port: process.env.MAIL_PORT,
  secure: false,
  auth: {
    user: process.env.MAIL_USER,
    pass: process.env.MAIL_PASS,
  },
});

/* ================================
   SEND OTP EMAIL (HTML)
================================ */
async function sendOtpEmail(email, otp, purpose) {
  const action =
    purpose === "REGISTER"
      ? "create your Innerly account"
      : "sign in to your Innerly account";

  await transporter.sendMail({
    from: `"Innerly – AI Therapist" <${process.env.MAIL_USER}>`,
    to: email,
    subject: "Your Innerly verification code",
    html: `
      <div style="font-family: Arial, sans-serif; color: #222;">
        <h2>Innerly Verification Code</h2>

        <p>Hello,</p>

        <p>
          You recently requested to <strong>${action}</strong>.
          Please use the verification code below:
        </p>

        <div style="
          font-size: 28px;
          font-weight: bold;
          letter-spacing: 4px;
          margin: 20px 0;
        ">
          ${otp}
        </div>

        <p>
          This code is valid for <strong>5 minutes</strong> and can be used only once.
        </p>

        <p>
          If you did not request this, you can safely ignore this email.
        </p>

        <hr />

        <p style="font-size: 12px; color: #666;">
          Innerly provides a private, judgment-free space for reflection and emotional clarity.
          Your privacy and security matter to us.
        </p>

        <p style="font-size: 12px; color: #666;">
          — Innerly AI Therapist
        </p>
      </div>
    `,
  });
}

/* ================================
   CREATE & SEND OTP (UTC SAFE)
================================ */
async function createAndSendOtp(user_id, email, purpose) {
  // 🔁 Invalidate previous OTPs for same purpose
  await pool.query(
    `
    UPDATE otp_verification
    SET is_used = true
    WHERE user_id = $1 AND purpose = $2
    `,
    [user_id, purpose]
  );

  const otp = generateOTP();
  const expiresAt = new Date(Date.now() + 5 * 60 * 1000);

  await pool.query(
    `
    INSERT INTO otp_verification
      (otp_id, user_id, otp_code, purpose, expires_at, is_used)
    VALUES
      ($1, $2, $3, $4, $5, false)
    `,
    [uuidv4(), user_id, otp, purpose, expiresAt]
  );

  await sendOtpEmail(email, otp, purpose);
}

module.exports = { createAndSendOtp };
