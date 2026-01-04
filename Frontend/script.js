/* ================= CONFIG ================= */
const API_BASE_URL = "http://localhost:5000/api";
let otpMode = null;

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", () => {
  createParticles();
  createNeuralNetwork();
  initReflectionPreview();

  window.addEventListener("scroll", () => {
    const navbar = document.getElementById("navbar");
    navbar?.classList.toggle("scrolled", window.scrollY > 50);
  });
});

/* ================= PARTICLES ================= */
function createParticles() {
  const container = document.getElementById("particles");
  if (!container) return;

  for (let i = 0; i < 80; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    p.style.left = Math.random() * 100 + "vw";
    p.style.top = Math.random() * 100 + "vh";
    p.style.width = p.style.height = Math.random() * 3 + 1 + "px";
    container.appendChild(p);
  }
}

/* ================= NEURAL NETWORK ================= */
function createNeuralNetwork() {
  const container = document.getElementById("neuralNetwork");
  if (!container) return;

  const nodes = [];
  for (let i = 0; i < 15; i++) {
    const n = document.createElement("div");
    n.className = "node";

    const angle = (i / 15) * Math.PI * 2;
    const r = 200;
    const x = r * Math.cos(angle);
    const y = r * Math.sin(angle);

    n.style.left = `calc(50% + ${x}px)`;
    n.style.top = `calc(50% + ${y}px)`;

    container.appendChild(n);
    nodes.push({ x, y });
  }

  nodes.forEach((a, i) => {
    nodes.slice(i + 1).forEach(b => {
      if (Math.random() > 0.7) {
        const c = document.createElement("div");
        c.className = "connection";
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        c.style.width = Math.hypot(dx, dy) + "px";
        c.style.left = `calc(50% + ${a.x}px)`;
        c.style.top = `calc(50% + ${a.y}px)`;
        c.style.transform = `rotate(${Math.atan2(dy, dx) * 180 / Math.PI}deg)`;
        container.appendChild(c);
      }
    });
  });
}

/* ================= REFLECTION PREVIEW ================= */
function initReflectionPreview() {
  const input = document.getElementById("previewInput");
  const response = document.getElementById("previewResponse");
  if (!input || !response) return;

  input.addEventListener("input", () => {
    const v = input.value.trim();
    response.textContent = !v
      ? ""
      : v.length < 10
      ? "Would you like to share more?"
      : v.length < 30
      ? "This seems important."
      : "The AI therapist can help you explore this further.";
    response.classList.toggle("active", !!v);
  });
}

/* ================= POPUP CONTROLS ================= */
function openLogin() {
  document.getElementById("loginPopup").style.display = "flex";
  showLogin();
}

function closeLogin() {
  document.getElementById("loginPopup").style.display = "none";
  resetForms();
  otpMode = null;
}

/* ================= VIEW SWITCH ================= */
function showLogin() {
  otpMode = null;
  toggleView("loginForm");
}
function showSignup() {
  otpMode = null;
  toggleView("signupForm");
}
function showEmailPassLogin() {
  toggleView("emailPassForm");
}
function showOtpLogin() {
  toggleView("otpForm");
}

function toggleView(id) {
  ["loginForm", "signupForm", "emailPassForm", "otpForm"].forEach(v => {
    const el = document.getElementById(v);
    if (el) el.style.display = v === id ? "block" : "none";
  });
}

/* ================= RESET ================= */
function resetForms() {
  document.querySelectorAll("input").forEach(i => (i.value = ""));
}

/* ================= REGISTER ================= */
async function submitSignup() {
  const full_name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const mobile_no = document.getElementById("mobile").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!full_name || !email || !mobile_no || !password) {
    alert("All fields required");
    return;
  }

  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      full_name,
      email,
      mobile_no,
      password
    })
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.message);
    return;
  }

  // 🔥 IMPORTANT
  otpMode = "REGISTER";

  alert("OTP sent to email");
  showOtpLogin();

  // lock email so user cannot change
  document.getElementById("otpEmail").value = email;
}


/* ================= LOGIN PASSWORD ================= */
async function submitEmailPass() {
  const email = loginEmail.value.trim();
  const password = loginPassword.value.trim();

  if (!email || !password) {
    alert("Email and password required");
    return;
  }

  const res = await fetch(`${API_BASE_URL}/auth/login-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  if (!res.ok) {
    alert(data.message);
    return;
  }

  localStorage.setItem("user_id", data.user_id);
  localStorage.setItem("user_name", data.full_name);
  localStorage.setItem("user_email", email);

  window.location.href = "chat.html";
}

/* ================= SEND OTP (LOGIN) ================= */
async function sendOtp() {
  otpMode = "LOGIN"; // 🔥 IMPORTANT

  const email = otpEmail.value.trim();
  if (!email) {
    alert("Enter email");
    return;
  }

  const res = await fetch(`${API_BASE_URL}/auth/login-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });

  const data = await res.json();
  if (!res.ok) {
    alert(data.message);
    return;
  }

  alert("OTP sent to email");
}

/* ================= VERIFY OTP ================= */
async function submitOtp() {
  const email = otpEmail.value.trim();
  const otp = otpCode.value.trim();

  if (!email || !otp) {
    alert("Email and OTP required");
    return;
  }

  if (!otpMode) {
    alert("OTP mode missing. Please retry.");
    return;
  }

  const endpoint =
    otpMode === "REGISTER"
      ? "/auth/verify-register-otp"
      : "/auth/verify-login-otp";

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp })
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.message);
    return;
  }

  /* ================= REGISTER → AUTO LOGIN ================= */
  if (otpMode === "REGISTER") {
    otpMode = null;

    // 🔥 AUTO LOGIN AFTER REGISTER
    const password = document.getElementById("password").value.trim();

    const loginRes = await fetch(`${API_BASE_URL}/auth/login-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const loginData = await loginRes.json();

    if (!loginRes.ok) {
      alert("Registration successful. Please login manually.");
      showLogin();
      return;
    }

    // ✅ LOGGED IN
    localStorage.setItem("user_id", loginData.user_id);
    localStorage.setItem("user_name", loginData.full_name);
    localStorage.setItem("user_email", email);

    window.location.href = "chat.html";
    return;
  }

  /* ================= LOGIN OTP FLOW ================= */
  localStorage.setItem("user_id", data.user_id);
  localStorage.setItem("user_name", data.full_name);
  localStorage.setItem("user_email", email);

  window.location.href = "chat.html";
}

