/**
 * X Assistant Phase 6 - Dynamic Web Dashboard Application Engine.
 * Handles real-time REST API synchronization, tab navigation, Web Speech API voice input,
 * telemetry updates, and multimodal interface controls.
 */

// --- Global State ---
let isListeningWebSpeech = false;
let recognitionEngine = null;

// --- DOM Content Loaded Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initTabNavigation();
  initWebSpeech();
  fetchSystemStatus();
  fetchIoTData();
  fetchRAGDocs();
  fetchPlugins();
  fetchAuditTrail();

  // Periodic Telemetry & Status Polling (every 3 seconds)
  setInterval(() => {
    fetchSystemStatus();
    fetchIoTData();
  }, 3000);
});

// --- Tab Switching Logic ---
function initTabNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      navBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// --- Web Speech API (Browser Voice Input) ---
function initWebSpeech() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognitionEngine = new SpeechRecognition();
    recognitionEngine.continuous = false;
    recognitionEngine.interimResults = false;
    recognitionEngine.lang = "en-US";

    recognitionEngine.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById("cmd-input").value = transcript;
      toggleWebMic(false);
      executeCommand();
    };

    recognitionEngine.onerror = (err) => {
      console.warn("Web Speech error:", err);
      toggleWebMic(false);
    };

    recognitionEngine.onend = () => {
      toggleWebMic(false);
    };
  } else {
    const micBtn = document.getElementById("mic-btn");
    if (micBtn) micBtn.title = "Web Speech API not supported in this browser.";
  }
}

function toggleWebMic(forceState) {
  const micBtn = document.getElementById("mic-btn");
  if (!recognitionEngine) return;

  isListeningWebSpeech = forceState !== undefined ? forceState : !isListeningWebSpeech;

  if (isListeningWebSpeech) {
    try {
      recognitionEngine.start();
      if (micBtn) {
        micBtn.style.background = "var(--danger)";
        micBtn.textContent = "🎙️ Listening...";
      }
    } catch (e) {
      isListeningWebSpeech = false;
    }
  } else {
    try {
      recognitionEngine.stop();
    } catch (e) {}
    if (micBtn) {
      micBtn.style.background = "rgba(255, 255, 255, 0.08)";
      micBtn.textContent = "🎙️";
    }
  }
}

// --- REST API Helpers ---
async function fetchSystemStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("app-title").textContent = `${data.name} Phase 6`;
    document.getElementById("backend-mode-badge").textContent = data.backend_mode;
    document.getElementById("active-personality-name").textContent = data.active_personality;
    document.getElementById("pomodoro-display").textContent = data.pomodoro;

    // Parse metrics string
    const infoStr = data.system_info || "";
    const cpuMatch = infoStr.match(/CPU:\s*([\d.]+)%/);
    const ramMatch = infoStr.match(/RAM:\s*([\d.]+)%/);
    const diskMatch = infoStr.match(/Disk:\s*([\d.]+)%/);

    if (cpuMatch) {
      const cpuVal = cpuMatch[1] + "%";
      document.getElementById("metric-cpu").textContent = cpuVal;
      document.getElementById("fill-cpu").style.width = cpuVal;
    }
    if (ramMatch) {
      const ramVal = ramMatch[1] + "%";
      document.getElementById("metric-ram").textContent = ramVal;
      document.getElementById("fill-ram").style.width = ramVal;
    }
    if (diskMatch) {
      const diskVal = diskMatch[1] + "%";
      document.getElementById("metric-disk").textContent = diskVal;
      document.getElementById("fill-disk").style.width = diskVal;
    }
  } catch (err) {
    console.error("Error fetching system status:", err);
  }
}

async function fetchIoTData() {
  try {
    const res = await fetch("/api/iot");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("tele-temp").textContent = `${data.temperature} °C`;
    document.getElementById("tele-humidity").textContent = `${data.humidity} %`;
    document.getElementById("tele-motion").textContent = data.motion ? "DETECTED!" : "Clear";
    document.getElementById("tele-gas").textContent = data.gas ? "ALERT!" : "Safe";

    const badge = document.getElementById("iot-status-badge");
    if (badge) {
      badge.textContent = data.is_simulated ? "⚡ Virtual IoT Simulation" : "⚡ Arduino Hardware Live";
      badge.style.color = data.is_simulated ? "var(--cyan)" : "var(--highlight)";
    }
  } catch (err) {
    console.error("Error fetching IoT data:", err);
  }
}

async function fetchRAGDocs() {
  try {
    const res = await fetch("/api/rag/docs");
    if (!res.ok) return;
    const data = await res.json();
    const list = document.getElementById("rag-docs-list");
    if (!list) return;

    if (!data.documents || data.documents.length === 0) {
      list.innerHTML = `<div class="system-msg">No documents ingested yet. Upload a PDF, TXT, or DOCX above.</div>`;
      return;
    }

    list.innerHTML = data.documents.map(d => `
      <div class="doc-item">
        <div>
          <strong>📄 ${escapeHtml(d.filename)}</strong>
          <span style="font-size:0.8rem; color:var(--text-muted); margin-left:10px;">(${d.doc_type.toUpperCase()}, ${d.total_chunks} chunks)</span>
        </div>
        <span style="font-size:0.75rem; color:var(--accent);">${d.imported_at}</span>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error fetching RAG docs:", err);
  }
}

async function fetchPlugins() {
  try {
    const res = await fetch("/api/plugins");
    if (!res.ok) return;
    const data = await res.json();
    const list = document.getElementById("plugins-list");
    if (!list) return;

    if (!data.plugins || data.plugins.length === 0) {
      list.innerHTML = `<div class="system-msg">No dynamic plugins currently installed.</div>`;
      return;
    }

    list.innerHTML = data.plugins.map(p => `
      <div class="plugin-item">
        <div>
          <strong>🔌 ${escapeHtml(p.name)}</strong> (ID: <code>${p.plugin_id}</code>)
          <div style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(p.description || '')}</div>
        </div>
        <span class="mode-badge">${p.status}</span>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error fetching plugins:", err);
  }
}

async function fetchAuditTrail() {
  try {
    const res = await fetch("/api/audit");
    if (!res.ok) return;
    const data = await res.json();
    const box = document.getElementById("audit-summary-box");
    if (box) {
      box.textContent = data.summary || "No audit trail logs available.";
    }
  } catch (err) {
    console.error("Error fetching audit trail:", err);
  }
}

// --- Command Processing ---
async function executeCommand(commandOverride) {
  const inputEl = document.getElementById("cmd-input");
  const cmd = commandOverride || inputEl.value.trim();
  if (!cmd) return;

  if (!commandOverride) inputEl.value = "";

  appendChatBubble("user", cmd);

  try {
    const res = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    if (data.success) {
      appendChatBubble("assistant", data.response);
    } else {
      appendChatBubble("assistant", `❌ Error: ${data.error}`);
    }
  } catch (err) {
    appendChatBubble("assistant", `❌ Network Connection Error: ${err}`);
  }
}

function sendQuickCmd(cmd) {
  executeCommand(cmd);
}

function clearLogs() {
  const box = document.getElementById("transcript-box");
  if (box) {
    box.innerHTML = `<div class="system-msg">🤖 <strong>Log cleared.</strong> Ready for new commands.</div>`;
  }
}

function appendChatBubble(role, text) {
  const box = document.getElementById("transcript-box");
  if (!box) return;

  const div = document.createElement("div");
  div.className = role === "user" ? "user-msg" : "assistant-msg";
  const prefix = role === "user" ? "👤 User: " : "🤖 X Assistant: ";
  div.innerHTML = `<strong>${prefix}</strong>${escapeHtml(text).replace(/\n/g, "<br>")}`;

  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

// --- Action Handlers ---
async function sendIoTControl(cmd) {
  appendChatBubble("user", cmd);
  try {
    const res = await fetch("/api/iot/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    appendChatBubble("assistant", data.result || "Executed IoT action.");
    fetchIoTData();
  } catch (err) {
    appendChatBubble("assistant", `❌ IoT Action Error: ${err}`);
  }
}

async function triggerVisionAction(cmd) {
  appendChatBubble("user", cmd);
  try {
    const res = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    appendChatBubble("assistant", data.response);

    const resultBox = document.getElementById("vision-result-box");
    if (resultBox) resultBox.textContent = data.response;
  } catch (err) {
    appendChatBubble("assistant", `❌ Vision AI Error: ${err}`);
  }
}

async function runWorkflow(cmd) {
  appendChatBubble("user", cmd);
  try {
    const res = await fetch("/api/workflows/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    appendChatBubble("assistant", data.result || "Executed macro workflow.");
  } catch (err) {
    appendChatBubble("assistant", `❌ Workflow Error: ${err}`);
  }
}

async function uploadRAGDocument(input) {
  if (!input.files || input.files.length === 0) return;
  const file = input.files[0];

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/rag/upload", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    alert(data.message || "Document uploaded successfully.");
    fetchRAGDocs();
  } catch (err) {
    alert("Upload failed: " + err);
  }
}

function escapeHtml(text) {
  return String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
