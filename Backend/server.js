require("dotenv").config();

const express = require("express");
const cors = require("cors");
const { testDBConnection } = require("./db/db");

const authRoutes = require("./routes/auth");
const chatRoutes = require("./routes/chat");
const userRoutes = require("./routes/user");

const app = express();

app.use(cors());
app.use(express.json()); // ✅ required

testDBConnection();

// ✅ API PREFIX
app.use("/api/auth", authRoutes);
app.use("/api/chat", chatRoutes);
app.use("/api/user", userRoutes);

app.get("/", (req, res) => {
  res.send("Backend running successfully ✅");
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
