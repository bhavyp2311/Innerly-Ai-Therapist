const express = require("express");
const { pool } = require("../db/db");
const router = express.Router();

router.get("/profile/:userId", async (req, res) => {
  const { userId } = req.params;

  const result = await pool.query(
    "SELECT user_id, full_name, email FROM users WHERE user_id=$1",
    [userId]
  );

  if (!result.rowCount)
    return res.status(404).json({ message: "User not found" });

  res.json(result.rows[0]);
});

module.exports = router;
