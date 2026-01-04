const { Pool } = require("pg");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// 🔥 Force public schema for Neon
pool.on("connect", (client) => {
  client.query("SET search_path TO public");
});

async function testDBConnection() {
  const res = await pool.query("SELECT current_database()");
  console.log("✅ Database connected:", res.rows[0].current_database);
}

module.exports = { pool, testDBConnection };
