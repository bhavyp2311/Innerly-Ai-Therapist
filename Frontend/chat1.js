/* ================= CONFIG ================= */
const API_BASE = "http://localhost:5000/api";
const userId = localStorage.getItem("user_id");


/* ================= STATE ================= */
let currentSessionId = null;
let welcomeShown = false;
let typingIndicator = null;

/* ================= DOM ================= */
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const sessionsList = document.getElementById("sessionsList");

/* ================= URL ================= */
function getSessionIdFromURL() {
  const sid = new URLSearchParams(window.location.search).get("sid");
  return (!sid || sid === "undefined") ? null : sid;
}

function setSessionIdToURL(id) {
  const url = new URL(window.location.href);
  url.searchParams.set("sid", id);
  window.history.replaceState({}, "", url);
}

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadUserProfile();
    await bootstrapSession();
    await loadSessionHistory();
  } catch (err) {
    console.error("Init error:", err);
  }

  // 🔥 ALWAYS ENABLE INPUT
  userInput.disabled = false;
  sendBtn.disabled = false;
});

/* ================= SESSION ================= */
async function bootstrapSession() {
  const sid = getSessionIdFromURL();
  if (sid) {
    currentSessionId = sid;
    await loadSessionContext(sid);
    return;
  }
  await createNewSession();
}

async function createNewSession() {
  clearChat();
  welcomeShown = false;

  const res = await fetch(`${API_BASE}/chat/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId })
  });

  const data = await res.json();
  currentSessionId = data.session_id;
  setSessionIdToURL(currentSessionId);

  showWelcome();
  await loadSessionHistory();
}

async function loadSessionContext(sessionId) {
  clearChat();
  welcomeShown = false;

  const res = await fetch(`${API_BASE}/chat/context/${sessionId}`);
  const data = await res.json();

  if (data.messages?.length) {
    data.messages.forEach(m => addMessage(m.content, m.role));
    welcomeShown = true;
  } else {
    showWelcome();
  }
}

/* ================= SIDEBAR ================= */
async function loadSessionHistory() {
  sessionsList.innerHTML = "";

  const res = await fetch(`${API_BASE}/chat/sessions/${userId}`);
  const { sessions } = await res.json();

  sessions.forEach(s => {
    const div = document.createElement("div");
    div.className =
      "p-3 mb-2 rounded cursor-pointer border border-gray-700 hover:border-gray-400";

    div.innerHTML = `
      <div class="text-sm truncate text-gray-200">${s.title || "New Session"}</div>
      <div class="text-xs text-gray-500">${new Date(s.created_at).toLocaleDateString()}</div>
    `;

    div.onclick = () => {
      currentSessionId = s.session_id;
      setSessionIdToURL(s.session_id);
      loadSessionContext(s.session_id);
    };

    sessionsList.appendChild(div);
  });
}

/* ================= CHAT ================= */
function showWelcome() {
  if (welcomeShown) return;
  addMessage(
    "Welcome. This is your safe, private space. I'm here to listen.",
    "ai"
  );
  welcomeShown = true;
}

// function addMessage(text, role) {
//   const div = document.createElement("div");
//   div.className = "mb-4";

//   div.innerHTML =
//     role === "user"
//       ? `<div class="flex justify-end">
//            <div class="bg-blue-600 text-white px-4 py-2 rounded-xl max-w-md">
//              ${text}
//            </div>
//          </div>`
//       : `<div class="flex">
//            <div class="bg-gray-800 text-white px-4 py-2 rounded-xl max-w-md">
//              ${text}
//            </div>
//          </div>`;

//   chatBox.appendChild(div);
//   chatBox.scrollTop = chatBox.scrollHeight;
// }
function addMessage(text, role) {
  const wrapper = document.createElement("div");
  wrapper.className = "mb-6 flex";

  if (role === "user") {
    wrapper.classList.add("justify-end");
    wrapper.innerHTML = `
      <div class="bg-blue-600 text-white px-4 py-3 rounded-xl max-w-[70%]">
        ${text}
      </div>
    `;
  } else {
    wrapper.classList.add("items-start", "gap-3");
    wrapper.innerHTML = `
      <div class="w-8 h-8 bg-gradient-to-br from-gray-900 to-black
                  flex items-center justify-center rounded-lg
                  border border-gray-500 text-gray-300 flex-shrink-0">
        ♡
      </div>

      <div class="bg-gradient-to-br from-gray-900 to-black
                  text-gray-300 px-4 py-3 rounded-xl
                  max-w-[70%] border border-gray-500">
        ${text}
      </div>
    `;
  }

  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}


/* ================= SEND ================= */
async function sendMessage() {
  if (!currentSessionId) return;

  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = "";

  // store user message (also sets title if first msg)
  await fetch(`${API_BASE}/chat/message/user`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: currentSessionId,
      content: text
    })
  });

  showTyping();

  const aiRes = await fetch(`${API_BASE}/chat/message/ai`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: currentSessionId,
      user_message: text
    })
  });

  const ai = await aiRes.json();
  hideTyping();
  addMessage(ai.ai_message, "ai");

  loadSessionHistory();
}

/* ================= PROFILE ================= */
async function loadUserProfile() {
  const res = await fetch(`${API_BASE}/user/profile/${userId}`);
  const user = await res.json();

  document.getElementById("profileName").innerText = user.full_name || "Anonymous";
  document.getElementById("profileEmail").innerText = user.email || "";
  document.getElementById("userAvatar").innerText =
    (user.full_name || "A").charAt(0).toUpperCase();
}

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

/* ================= HELPERS ================= */
function clearChat() {
  chatBox.innerHTML = "";
}

function showTyping() {
  typingIndicator = document.createElement("div");
  typingIndicator.className = "text-gray-400 text-sm";
  typingIndicator.innerText = "typing...";
  chatBox.appendChild(typingIndicator);
}

function hideTyping() {
  typingIndicator?.remove();
  typingIndicator = null;
}

/* ================= EVENTS ================= */
sendBtn.onclick = sendMessage;

newChatBtn.onclick = createNewSession;

userInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

document.getElementById("logoutBtn").onclick = logout;


/* ================= VOICE INPUT ================= */
let recognition;
let isRecording = false;

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = navigator.language || "en-US";

  recognition.onstart = () => {
    isRecording = true;
    userInput.placeholder = "Listening...";
    document.body.classList.add("listening");
  };

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    userInput.value = transcript;
  };

  recognition.onend = () => {
    isRecording = false;
    userInput.placeholder = "Share your thoughts...";
    document.body.classList.remove("listening");

    if (userInput.value.trim()) {
      sendMessage();
    }
  };

  recognition.onerror = (e) => {
    console.warn("Speech error:", e.error);
    isRecording = false;
    document.body.classList.remove("listening");

    if (e.error === "not-allowed") {
      alert("Microphone permission denied by browser.");
    }
  };
}

/* ================= PUSH TO TALK ================= */
async function startVoice() {
  if (!recognition) {
    alert("Speech recognition not supported in this browser.");
    return;
  }

  try {
    await navigator.mediaDevices.getUserMedia({ audio: true });

    if (!isRecording) {
      recognition.start();
    }
  } catch (err) {
    alert("Please allow microphone access in browser settings.");
  }
}
