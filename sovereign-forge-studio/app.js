// ── Sovereign Forge Studio - Cursor & Claude IDE (Real-API Bridge) ──

// ── Application State ────────────────────────────────────────────────────────
let state = {
  currentView: "browser", // 'browser' or 'editor'
  activeFile: "canister/main.mo",
  model: "cerebex",
  isCompiling: false,
  isDeploying: false,
  chatHistory: [
    { sender: 'assistant', text: "Workspace linked: **MedinaMemorySystems**. Choose an agent or model from the Composer dropdown to inspect changes or compile WASM canisters." }
  ],
  diffActive: false,
  fileOriginalContent: "",
  fileDiffContent: "",
  fileMergedContent: ""
};

// ── Clock Ticker ────────────────────────────────────────────────────────────
function initClocks() {
  const clock = document.getElementById('block-clock');
  if (!clock) return;
  setInterval(() => {
    const now = new Date();
    clock.innerHTML = `[ICP BLOCK] <span style="color: #58a6ff; font-weight:600;">${now.toISOString().replace('T', ' ').substring(0, 19)}</span>`;
  }, 1000);
}

// ── Fetch & Render Real Git Graph ────────────────────────────────────────────
async function loadGitGraph() {
  const container = document.getElementById('git-graph-container');
  if (!container) return;

  try {
    const response = await fetch('/api/git-log');
    if (response.ok) {
      const commits = await response.json();
      if (commits.length === 0) {
        container.innerHTML = `<div style="font-size: 11px; color: var(--text-dark); text-align: center; padding-top: 20px;">No commits found.</div>`;
        return;
      }
      
      container.innerHTML = commits.map(commit => {
        let color = "var(--git-graph-blue)";
        if (commit.branch === 1) color = "var(--git-graph-orange)";
        if (commit.branch === 2) color = "var(--git-graph-pink)";

        return `
          <div class="graph-row" title="Commit: ${commit.hash} - ${commit.msg}" onclick="logToWsl('[GIT] Commit hash: ${commit.hash}')">
            <div class="graph-canvas">
              <div class="graph-line" style="background: ${color};"></div>
              <div class="graph-circle" style="background: ${color}; box-shadow: 0 0 4px ${color}"></div>
            </div>
            <div class="graph-msg"><span style="color: var(--text-dark);">${commit.hash}</span> ${commit.msg}</div>
          </div>
        `;
      }).join('');
    }
  } catch (e) {
    container.innerHTML = `<div style="font-size: 11px; color: var(--text-dark); text-align: center; padding-top: 20px;">Failed to load git log.</div>`;
  }
}

// ── Fetch & Render Real Changes (Git Status) ─────────────────────────────────
async function loadGitChanges() {
  const listContainer = document.querySelector('.changes-list');
  if (!listContainer) return;

  try {
    const response = await fetch('/api/git-status');
    if (response.ok) {
      const changes = await response.json();
      if (changes.length === 0) {
        listContainer.innerHTML = `<div style="font-size: 11px; color: var(--text-dark); text-align: center; padding: 10px 0;">No changed files.</div>`;
        return;
      }

      listContainer.innerHTML = changes.map(change => {
        const parts = change.path.split('/');
        const name = parts[parts.length - 1];
        const path = parts.slice(0, -1).join('/') || './';
        
        let badgeClass = "mo";
        if (name.endsWith('.rs')) badgeClass = "rs";
        if (name.endsWith('.py')) badgeClass = "py";
        if (name.endsWith('.json') || name.endsWith('.yaml') || name.endsWith('.yml')) badgeClass = "json";

        return `
          <div class="change-item" data-file="${change.path}" onclick="showEditor('${change.path}')">
            <div class="change-item-left">
              <span>📄 ${name}</span>
              <span class="change-path">${path}</span>
            </div>
            <span class="change-status ${change.status}">${change.status}</span>
          </div>
        `;
      }).join('');
    }
  } catch (e) {
    listContainer.innerHTML = `<div style="font-size: 11px; color: var(--text-dark); text-align: center;">Failed to load git status.</div>`;
  }
}

// ── Fetch & Render Hierarchical Files Explorer ──────────────────────────────
async function loadWorkspaceFiles() {
  const explorerTree = document.querySelector('.explorer-tree');
  if (!explorerTree) return;

  try {
    const response = await fetch('/api/files');
    if (response.ok) {
      const files = await response.json();
      
      let html = "";
      for (const item of files) {
        // Calculate indentation depth based on path levels
        const depth = item.path.split('/').length - 1;
        const paddingLeft = depth * 12;

        if (item.isDir) {
          html += `<div class="tree-folder" style="margin-top: 6px; padding-left: ${paddingLeft}px;">📁 ${item.name}</div>`;
        } else {
          let badgeClass = "mo";
          if (item.name.endsWith('.rs')) badgeClass = "rs";
          if (item.name.endsWith('.py')) badgeClass = "py";
          if (item.name.endsWith('.jsx') || item.name.endsWith('.js') || item.name.endsWith('.ts')) badgeClass = "js";
          if (item.name.endsWith('.json')) badgeClass = "json";
          if (item.name.endsWith('.yaml') || item.name.endsWith('.yml')) badgeClass = "yaml";

          html += `
            <div class="tree-file ${state.activeFile === item.path ? 'active' : ''}" data-file="${item.path}" style="padding-left: ${paddingLeft + 12}px;" onclick="showEditor('${item.path}')">
              <span>📄 ${item.name}</span>
              <span class="badge-lang ${badgeClass}">${badgeClass}</span>
            </div>
          `;
        }
      }
      explorerTree.innerHTML = html;
    }
  } catch (e) {
    explorerTree.innerHTML = `<div style="font-size: 11px; color: var(--text-dark); padding: 10px;">Failed to scan workspace files.</div>`;
  }
}

// ── Log Console Output ───────────────────────────────────────────────────────
function logToWsl(message, type = 'normal') {
  const term = document.getElementById('wsl-terminal');
  if (!term) return;
  const row = document.createElement('div');
  row.className = `terminal-row ${type}`;
  row.innerText = message;
  term.appendChild(row);
  term.scrollTop = term.scrollHeight;
}

// ── View Transitions (Browser vs Code Editor) ────────────────────────────────
function showBrowser() {
  state.currentView = "browser";
  document.getElementById('view-browser-container').style.display = "flex";
  document.getElementById('view-editor-container').style.display = "none";

  document.getElementById('tab-gh-browser').classList.add('active');
  document.getElementById('tab-editor-file').classList.remove('active');
}

function showEditor(filename) {
  state.currentView = "editor";
  state.activeFile = filename;
  
  document.getElementById('view-browser-container').style.display = "none";
  document.getElementById('view-editor-container').style.display = "flex";

  document.getElementById('tab-gh-browser').classList.remove('active');
  
  const fileTab = document.getElementById('tab-editor-file');
  fileTab.style.display = "flex";
  fileTab.classList.add('active');
  
  document.getElementById('editor-tab-name').innerText = filename.split('/').pop();

  const items = document.querySelectorAll('.tree-file');
  items.forEach(item => {
    if (item.dataset.file === filename) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  loadEditorCode(filename);
}

// ── Real File Reading ────────────────────────────────────────────────────────
async function loadEditorCode(filename, mode = 'normal') {
  const editor = document.getElementById('code-editor-area');
  const lineNumbers = document.getElementById('editor-line-numbers');
  if (!editor || !lineNumbers) return;

  if (state.activeTab === 'candid') {
    const candidText = generateCandidSchema(filename);
    editor.value = candidText;
    updateLineNumbers(candidText);
    return;
  }

  if (mode === 'diff') {
    editor.value = state.fileDiffContent;
    updateLineNumbers(state.fileDiffContent);
    return;
  } else if (mode === 'merged') {
    editor.value = state.fileMergedContent;
    updateLineNumbers(state.fileMergedContent);
    return;
  }

  logToWsl(`[FILE] Fetching content from disk: ${filename}...`, 'info');
  try {
    const response = await fetch(`/api/file?path=${encodeURIComponent(filename)}`);
    if (response.ok) {
      const text = await response.text();
      state.fileOriginalContent = text;
      editor.value = text;
      updateLineNumbers(text);
      logToWsl(`[FILE] Loaded successfully: ${text.length} bytes.`, 'success');
    } else {
      editor.value = "// Error loading file content from local server API.";
    }
  } catch (err) {
    editor.value = "// Failed to connect to local server file system API.";
  }
}

function updateLineNumbers(text) {
  const lineNumbers = document.getElementById('editor-line-numbers');
  if (!lineNumbers) return;
  const lines = text.split('\n').length;
  let numbersHtml = "";
  for (let i = 1; i <= lines; i++) {
    numbersHtml += `${i}<br>`;
  }
  lineNumbers.innerHTML = numbersHtml;
}

// ── Real File Saving with Backup Logging (Ctrl+S) ───────────────────────────
async function saveActiveFile() {
  if (state.currentView !== 'editor' || state.activeTab === 'candid' || state.diffActive) return;
  
  const editor = document.getElementById('code-editor-area');
  if (!editor) return;

  const content = editor.value;
  logToWsl(`[SAVE] Writing changes to disk for: ${state.activeFile}...`, 'info');

  try {
    const response = await fetch('/api/file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: state.activeFile, content })
    });

    if (response.ok) {
      const data = await response.json();
      logToWsl(`[SAVE] Overwritten successfully: ${state.activeFile}`, 'success');
      
      if (data.backupCreated) {
        logToWsl(`[BACKUP] Created copy: sovereign-forge-studio/.backups/${data.backupCreated}`, 'info');
      }
      
      state.fileOriginalContent = content;
      loadGitChanges();
      loadWorkspaceFiles();
    } else {
      logToWsl(`[SAVE] Error: API returned status ${response.status}`, 'err');
    }
  } catch (err) {
    logToWsl(`[SAVE] Connection error: Failed to reach local backend API.`, 'err');
  }
}

function generateCandidSchema(filename) {
  if (filename.includes('token')) {
    return `type Account = record { owner: principal; subaccount: opt vec nat8; };\nservice : (text, text) -> {\n  icrc1_name: () -> (text) query;\n  icrc1_symbol: () -> (text) query;\n}`;
  }
  return `type Entry = record { id: text; author: principal; };\nservice : {\n  create_entry: (text, text, text) -> (variant { ok: text; err: text });\n}`;
}

// ── Real Shell Process Spawn ────────────────────────────────────────────────
function runTerminalCommand(command, shellTarget = 'wsl') {
  const eventSource = new EventSource(`/api/run-command?cmd=${encodeURIComponent(command)}`);
  
  const termWsl = document.getElementById('wsl-terminal');
  const termPs = document.getElementById('powershell-terminal');

  if (shellTarget === 'wsl') {
    logToWsl(`$ ${command}`, 'cmd');
  } else {
    logToPowerShell(`PS C:\\Users\\Medin\\MedinaMemorySystems> ${command}`, 'cmd');
  }

  eventSource.addEventListener('log', (e) => {
    const data = JSON.parse(e.data);
    if (shellTarget === 'wsl') {
      logToWsl(data.text, data.type);
    } else {
      logToPowerShell(data.text, data.type);
    }
  });

  eventSource.addEventListener('done', (e) => {
    const data = JSON.parse(e.data);
    if (shellTarget === 'wsl') {
      logToWsl(`[DONE] Process exited. Code: ${data.code}`, 'info');
    } else {
      logToPowerShell(`[DONE] Process exited. Code: ${data.code}`, 'info');
    }
    eventSource.close();
    
    // Refresh states
    loadGitChanges();
    loadWorkspaceFiles();
    loadGitGraph();
  });

  eventSource.addEventListener('error', (e) => {
    if (shellTarget === 'wsl') {
      logToWsl("[ERROR] SSE socket connection error.", 'err');
    } else {
      logToPowerShell("[ERROR] SSE socket connection error.", 'err');
    }
    eventSource.close();
  });
}

// ── Interactive Inline Diff Engine ──────────────────────────────────────────
function triggerInlineDiff() {
  if (state.activeFile !== "canister/main.mo") {
    showEditor("canister/main.mo");
  }

  state.fileDiffContent = `// Sovereign OS Core Integration Layer: Enabled [MCGR E1-E15]
import Array "mo:base/Array";
import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Result "mo:base/Result";

shared({ caller = creator }) actor class SovereignCrudCanister() {
  
  public type Entry = {
    id: Text;
    title: Text;
    content: Text;
    timestamp: Int;
    author: Principal;
  };

  private stable var entriesMap : [(Text, Entry)] = [];
<<<<- DIFF DELETE - LINE 19
  public shared func create_entry(id: Text, title: Text, content: Text) : async Result.Result<Text, Text> {
    let newEntry : Entry = { id = id; title = title; content = content; timestamp = Time.now(); author = msg.caller; };
====+ DIFF INSERT - LINE 19
  // ARCHON Security Guard: Verify caller before creating database entries
  public shared(msg) func create_entry(id: Text, title: Text, content: Text) : async Result.Result<Text, Text> {
    if (msg.caller == Principal.anonymous()) { return #err("Anonymous caller rejected by ARCHON Guard."); };
    let newEntry : Entry = { id = id; title = title; content = content; timestamp = Time.now(); author = msg.caller; };
====
    entriesMap := Array.append(entriesMap, [(id, newEntry)]);
    return #ok(id);
  };
}`;

  state.fileMergedContent = `// Sovereign OS Core Integration Layer: Enabled [MCGR E1-E15]
import Array "mo:base/Array";
import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Result "mo:base/Result";

shared({ caller = creator }) actor class SovereignCrudCanister() {
  
  public type Entry = {
    id: Text;
    title: Text;
    content: Text;
    timestamp: Int;
    author: Principal;
  };

  private stable var entriesMap : [(Text, Entry)] = [];

  // ARCHON Security Guard: Verify caller before creating database entries
  public shared(msg) func create_entry(id: Text, title: Text, content: Text) : async Result.Result<Text, Text> {
    if (msg.caller == Principal.anonymous()) { return #err("Anonymous caller rejected by ARCHON Guard."); };
    let newEntry : Entry = { id = id; title = title; content = content; timestamp = Time.now(); author = msg.caller; };
    entriesMap := Array.append(entriesMap, [(id, newEntry)]);
    return #ok(id);
  };
}`;

  logToWsl("[AGENT] Applying inline diff edits on canister/main.mo...");
  setTimeout(() => {
    state.diffActive = true;
    loadEditorCode("canister/main.mo", 'diff');
    document.getElementById('floating-diff-bar').style.display = "flex";
  }, 800);
}

async function acceptDiff() {
  if (!state.diffActive) return;

  logToWsl("[DIFF] Merging diff block changes...", 'info');
  try {
    const response = await fetch('/api/file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: state.activeFile, content: state.fileMergedContent })
    });

    if (response.ok) {
      loadEditorCode(state.activeFile, 'merged');
      document.getElementById('floating-diff-bar').style.display = "none";
      state.diffActive = false;
      logToWsl("[DIFF] Changes saved to disk. Re-formatting file layout...", 'success');
      runTerminalCommand("wsl moc -format canister/main.mo", 'wsl');
    }
  } catch (err) {
    logToWsl("[DIFF] Error writing merged code to filesystem.", 'err');
  }
}

function rejectDiff() {
  if (!state.diffActive) return;
  loadEditorCode(state.activeFile, 'normal');
  document.getElementById('floating-diff-bar').style.display = "none";
  state.diffActive = false;
  logToWsl("[DIFF] Edits rejected. Reverted canister file.", 'warn');
}

// ── AI Composer Chat Logic ──────────────────────────────────────────────────
function triggerAgentPrompt(text) {
  if (!text.trim()) return;

  state.chatHistory.push({ sender: 'user', text });
  updateChatUI();

  logToWsl(`[COMPOSER] Query model '${state.model}': "${text}"`, 'info');

  setTimeout(() => {
    if (text.toLowerCase().includes('modify') || text.toLowerCase().includes('add') || text.toLowerCase().includes('change') || text.toLowerCase().includes('security')) {
      triggerInlineDiff();
      state.chatHistory.push({
        sender: 'assistant',
        text: "I've generated the secure validator diff inside `canister/main.mo`. You can review it, compare changes, and click Accept to write the updates to your disk."
      });
    } else {
      state.chatHistory.push({
        sender: 'assistant',
        text: "Analyzing local repository. You can start local compiles by running the shell command `moc canister/main.mo` in the terminal panel below."
      });
    }
    updateChatUI();
  }, 1000);
}

function updateChatUI() {
  const container = document.getElementById('chat-container');
  if (!container) return;

  container.innerHTML = state.chatHistory.map(msg => {
    if (msg.sender === 'system') {
      return `<div class="agent-bubble system">${msg.text.replace(/\n/g, '<br>')}</div>`;
    }
    let parsedText = msg.text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\`(.*?)\`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
    return `<div class="agent-bubble ${msg.sender === 'user' ? 'user' : 'assistant'}">${parsedText}</div>`;
  }).join('');

  container.scrollTop = container.scrollHeight;
}

// ── Event Handlers ───────────────────────────────────────────────────────────
function initEventHandlers() {
  document.getElementById('tab-gh-browser').addEventListener('click', showBrowser);
  document.getElementById('tab-editor-file').addEventListener('click', () => showEditor(state.activeFile));
  
  document.getElementById('editor-tab-close-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    document.getElementById('tab-editor-file').style.display = "none";
    if (state.currentView === 'editor') {
      showBrowser();
    }
  });

  document.getElementById('btn-accept-diff').addEventListener('click', acceptDiff);
  document.getElementById('btn-reject-diff').addEventListener('click', rejectDiff);

  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      saveActiveFile();
    }
  });

  const promptInput = document.getElementById('ai-prompt-input');
  const sendBtn = document.getElementById('send-prompt-btn');

  const submitPrompt = () => {
    const text = promptInput.value;
    if (!text.trim()) return;
    triggerAgentPrompt(text);
    promptInput.value = '';
  };

  sendBtn.addEventListener('click', submitPrompt);
  promptInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitPrompt();
    }
  });

  document.getElementById('btn-attach').addEventListener('click', () => {
    promptInput.value += ' @canister/main.mo ';
    promptInput.focus();
  });

  document.getElementById('connect-ii-btn').addEventListener('click', () => {
    runTerminalCommand("medinad auth login --identity medina-admin-session", 'powershell');
  });

  const repos = document.querySelectorAll('.gh-repo-card');
  repos.forEach(card => {
    card.addEventListener('click', (e) => {
      const repo = e.currentTarget.dataset.repo;
      runTerminalCommand(`wsl echo "[COMPILER] Syncing ItsNotAILABS/${repo}" && wsl git log -n 1`, 'wsl');
    });
  });
}

// ── Initialization ───────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initClocks();
  loadGitGraph();
  loadGitChanges();
  loadWorkspaceFiles();
  initEventHandlers();
  updateChatUI();
  
  logToWsl("[SYSTEM] Sovereign local web IDE connection established.");
  logToPowerShell("PS C:\\Users\\Medin\\MedinaMemorySystems> git branch");
});
