const API_URL = "https://rag-chromeextension-youtube.onrender.com/ask";

let lastAnswer = "";
let currentVideoId = "";
let sourcesOpen = false;

// ---------- helpers ----------
async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

function parseVideoIdFromUrl(url) {
  try {
    const u = new URL(url);
    return u.searchParams.get("v");
  } catch {
    return null;
  }
}

async function getVideoId(tab) {
  return new Promise((resolve) => {
    chrome.tabs.sendMessage(tab.id, { type: "GET_VIDEO_ID" }, (resp) => {
      if (chrome.runtime.lastError) {
        resolve(parseVideoIdFromUrl(tab.url));
        return;
      }
      resolve(resp?.videoId || parseVideoIdFromUrl(tab.url));
    });
  });
}

function setStatus(text, cls = "") {
  const row = document.getElementById("statusRow");
  row.className = `status ${cls}`.trim();
  document.getElementById("status").textContent = text;
}

function setLoading(isLoading) {
  const btn = document.getElementById("askBtn");
  if (isLoading) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>Sending…`;
  } else {
    btn.disabled = false;
    btn.textContent = "Send";
  }
}

function appendMessage(role, text) {
  const chat = document.getElementById("chat");
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}

function formatTime(seconds) {
  seconds = Math.max(0, Math.floor(seconds));
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  const h = Math.floor(m / 60);
  const mm = m % 60;
  if (h > 0) return `${String(h).padStart(2,"0")}:${String(mm).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
  return `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}

// ---------- sources UI ----------
function renderSources(sources) {
  const list = document.getElementById("sourcesList");
  list.innerHTML = "";

  if (!sources || sources.length === 0) {
    const empty = document.createElement("div");
    empty.style.color = "rgba(255,255,255,.65)";
    empty.style.fontSize = "12px";
    empty.textContent = "No sources returned.";
    list.appendChild(empty);
    return;
  }

  sources.forEach((src, idx) => {
    const item = document.createElement("div");
    item.className = "sourceItem";

    const top = document.createElement("div");
    top.className = "sourceTop";

    const label = document.createElement("div");
    label.className = "sourceLabel";
    label.textContent = `Source [${idx + 1}]`;

    const tsBtn = document.createElement("button");
    tsBtn.className = "tsBtn";
    tsBtn.textContent = formatTime(src.start || 0);

    tsBtn.addEventListener("click", async () => {
      const tab = await getActiveTab();
      chrome.tabs.sendMessage(tab.id, { type: "SEEK_TO", seconds: src.start || 0 });
    });

    top.appendChild(label);
    top.appendChild(tsBtn);

    const text = document.createElement("div");
    text.className = "sourceText";
    text.textContent = src.text || "";

    item.appendChild(top);
    item.appendChild(text);
    list.appendChild(item);
  });
}

// ---------- storage (chat per video) ----------
async function saveChat(messages) {
  if (!currentVideoId) return;
  const key = `chat_${currentVideoId}`;
  await chrome.storage.local.set({ [key]: messages });
}

async function loadChat() {
  if (!currentVideoId) return [];
  const key = `chat_${currentVideoId}`;
  const data = await chrome.storage.local.get([key]);
  return data[key] || [];
}

async function clearChatStorage() {
  if (!currentVideoId) return;
  const key = `chat_${currentVideoId}`;
  await chrome.storage.local.remove([key]);
}

// ---------- main ----------
async function init() {
  // toggle button
  const toggleBtn = document.getElementById("toggleSourcesBtn");
  const sourcesBox = document.getElementById("sourcesBox");

  toggleBtn.addEventListener("click", () => {
    sourcesOpen = !sourcesOpen;
    toggleBtn.textContent = sourcesOpen ? "Hide Sources" : "Show Sources";
    sourcesBox.style.display = sourcesOpen ? "block" : "none";
  });

  // detect video
  const tab = await getActiveTab();
  const vid = await getVideoId(tab);

  currentVideoId = vid || "";
  document.getElementById("videoPill").textContent = `Video: ${vid || "not detected"}`;

  document.getElementById("chat").innerHTML = "";

  if (!vid) {
    appendMessage("ai", "Open a YouTube watch page first (URL includes ?v=...).");
    setStatus("No video detected.", "err");
    return;
  }

  // load chat history
  const oldMessages = await loadChat();
  if (oldMessages.length === 0) {
    const hello = "Hi! Ask me anything about this video.";
    appendMessage("ai", hello);
    await saveChat([{ role: "ai", text: hello }]);
  } else {
    oldMessages.forEach((m) => appendMessage(m.role, m.text));
  }

  setStatus("Ready.");
}

async function send() {
  const textarea = document.getElementById("question");
  const question = textarea.value.trim();
  const kVal = parseInt(document.getElementById("k").value || "3", 10);
  const k = Number.isFinite(kVal) ? Math.max(1, Math.min(10, kVal)) : 3;

  if (!question) {
    setStatus("Type a question first.", "err");
    return;
  }

  const tab = await getActiveTab();
  const videoId = await getVideoId(tab);

  if (!videoId) {
    setStatus("Open a YouTube watch page (URL must include ?v=VIDEO_ID).", "err");
    return;
  }

  currentVideoId = videoId;
  document.getElementById("videoPill").textContent = `Video: ${videoId}`;

  // show user message
  appendMessage("user", question);
  textarea.value = "";
  setStatus(`Thinking (top-k=${k})…`);
  setLoading(true);

  // persist user message
  const existing = await loadChat();
  existing.push({ role: "user", text: question });
  await saveChat(existing);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id: videoId, question, k })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = data?.detail ? JSON.stringify(data.detail) : "Request failed";
      throw new Error(detail);
    }

    const ans = data.answer || "(No answer returned)";
    lastAnswer = ans;

    appendMessage("ai", ans);

    const updated = await loadChat();
    updated.push({ role: "ai", text: ans });
    await saveChat(updated);

    // sources
    renderSources(data.sources || []);

    setStatus("Done.", "ok");
  } catch (e) {
    const msg =
      `Backend error:\n${e.message}\n\n` +
      `Check:\n- Server running at http://127.0.0.1:8000\n- Try /docs`;

    appendMessage("ai", msg);

    const updated = await loadChat();
    updated.push({ role: "ai", text: msg });
    await saveChat(updated);

    setStatus("Backend error.", "err");
  } finally {
    setLoading(false);
  }
}

// ---------- events ----------
document.addEventListener("DOMContentLoaded", init);

document.getElementById("askBtn").addEventListener("click", send);

document.getElementById("question").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

document.getElementById("clearBtn").addEventListener("click", async () => {
  await clearChatStorage();
  document.getElementById("chat").innerHTML = "";
  lastAnswer = "";

  // reset sources UI
  document.getElementById("sourcesList").innerHTML = "";
  document.getElementById("sourcesBox").style.display = "none";
  document.getElementById("toggleSourcesBtn").textContent = "Show Sources";
  sourcesOpen = false;

  setStatus("Cleared.", "");
  const msg = "Chat cleared for this video.";
  appendMessage("ai", msg);
  await saveChat([{ role: "ai", text: msg }]);
});

document.getElementById("copyBtn").addEventListener("click", async () => {
  if (!lastAnswer) {
    setStatus("Nothing to copy yet.", "err");
    return;
  }
  try {
    await navigator.clipboard.writeText(lastAnswer);
    setStatus("Copied last answer.", "ok");
  } catch {
    setStatus("Copy failed (permission).", "err");
  }
});