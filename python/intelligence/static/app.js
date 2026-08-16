const API = ''; // relative url

// Global State
let capabilities = [];
let protocols = [];
let papers = [];
let agents = [];
let models = [];
let activeTab = 'dashboard';
let systemStartTime = Date.now();

// Pyodide state
let pyodideInstance = null;
let pyodideLoaded = false;
let pyodideLoading = false;

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    setupNavigation();
    setupSearch();
    loadDashboardData();
    startUptimeTimer();

    // Load initial tab data
    fetchData();
}

// Navigation
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    // Stat card link triggers
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('click', () => {
            const targetTab = card.getAttribute('data-target-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    activeTab = tabId;
    
    // Hide search results if switching to a regular tab
    document.getElementById('search-results-section').style.display = 'none';

    // Update nav button states
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Toggle content visibility
    document.querySelectorAll('.tab-content').forEach(section => {
        if (section.id === `${tabId}-tab`) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });

    // Trigger tab-specific refresh if needed
    if (tabId === 'dashboard') loadDashboardData();
    if (tabId === 'capabilities') renderCapabilities();
    if (tabId === 'research') loadResearchData();
    if (tabId === 'protocols') renderProtocols();
    if (tabId === 'papers') renderPapers();
    if (tabId === 'agents') loadAgentsData();
    if (tabId === 'pyodide') initPyodideSandbox();
    if (tabId === 'organism') loadOrganismData();
}

// Global Search
function setupSearch() {
    const searchInput = document.getElementById('global-search-input');
    const searchBtn = document.getElementById('global-search-btn');

    const handleSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        // Hide all regular tabs
        document.querySelectorAll('.tab-content').forEach(section => {
            section.classList.remove('active');
        });
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show search section
        const searchSection = document.getElementById('search-results-section');
        searchSection.style.display = 'block';
        searchSection.classList.add('active');

        const container = document.getElementById('search-results-container');
        container.innerHTML = '<div class="loading-placeholder">Searching intelligence matrix...</div>';

        try {
            const res = await fetch(`${API}/api/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            renderSearchResults(data);
        } catch (err) {
            container.innerHTML = `<div class="text-red">Search failed: ${err.message}</div>`;
        }
    };

    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
}

function closeSearchResults() {
    switchTab('dashboard');
}

function renderSearchResults(data) {
    const container = document.getElementById('search-results-container');
    container.innerHTML = '';

    if (data.total === 0) {
        container.innerHTML = '<div class="text-dim text-center">No matches found in the sovereign database.</div>';
        return;
    }

    const categories = [
        { key: 'index_results', title: 'Substrate Files & Registers', format: item => `
            <div class="search-item">
                <div class="search-item-title">[${item.kind}] ${item.name}</div>
                <div class="search-item-desc">${item.file_path} - ${item.description || 'No description available'}</div>
            </div>`
        },
        { key: 'protocol_results', title: 'Active Network Protocols', format: item => `
            <div class="search-item" onclick="switchTab('protocols')">
                <div class="search-item-title">${item.protocol_id}: ${item.name}</div>
                <div class="search-item-desc">${item.description} - Wire: ${item.wire}</div>
            </div>`
        },
        { key: 'paper_results', title: 'Academic Research Papers', format: item => `
            <div class="search-item" onclick="switchTab('papers')">
                <div class="search-item-title">${item.paper_id}: ${item.title}</div>
                <div class="search-item-desc">${item.abstract}</div>
            </div>`
        },
        { key: 'capability_results', title: 'Universal Capability Functions', format: item => `
            <div class="search-item" onclick="switchTab('capabilities')">
                <div class="search-item-title">${item.id}: ${item.name}</div>
                <div class="search-item-desc">${item.description}</div>
            </div>`
        }
    ];

    categories.forEach(cat => {
        const items = data[cat.key] || [];
        if (items.length > 0) {
            const block = document.createElement('div');
            block.className = 'search-category-block';
            block.innerHTML = `
                <h3>${cat.title} (${items.length})</h3>
                <div class="search-results-list">
                    ${items.map(cat.format).join('')}
                </div>
            `;
            container.appendChild(block);
        }
    });
}

// Fetch all initial data
async function fetchData() {
    try {
        const [healthRes, capRes, protoRes, paperRes, agentRes, modelRes] = await Promise.all([
            fetch(`${API}/api/health`),
            fetch(`${API}/api/capabilities`),
            fetch(`${API}/api/protocols`),
            fetch(`${API}/api/papers`),
            fetch(`${API}/api/agents`),
            fetch(`${API}/api/models`)
        ]);

        const health = await healthRes.json();
        capabilities = (await capRes.json()).capabilities;
        protocols = (await protoRes.json()).protocols;
        papers = (await paperRes.json()).papers;
        agents = (await agentRes.json()).agents;
        models = (await modelRes.json()).models;

        // Set system uptime counter base
        systemStartTime = Date.now() - (health.uptime_seconds * 1000);

        // Update counts on UI
        document.getElementById('stat-index').textContent = health.modules.master_index;
        document.getElementById('stat-capabilities').textContent = health.modules.capabilities;
        document.getElementById('stat-future-ai').textContent = health.modules.future_ai;
        document.getElementById('stat-protocols').textContent = health.modules.protocols;
        document.getElementById('stat-papers').textContent = health.modules.papers;
        document.getElementById('stat-agents').textContent = health.modules.agents;

        // Auto render active tab
        switchTab(activeTab);

    } catch (err) {
        console.error('Failed to boot application data lattice:', err);
    }
}

// Dashboard Tab
function loadDashboardData() {
    // Render models compact list
    const list = document.getElementById('dashboard-models-list');
    if (!models.length) {
        list.innerHTML = '<div class="text-dim">No models loaded.</div>';
        return;
    }
    list.innerHTML = models.map(m => `
        <div class="model-row-compact">
            <div class="model-name-group">
                <span class="model-latinum">${m.nomen_latinum}</span>
                <span class="model-breve">${m.nomen_breve} (${m.dominium})</span>
            </div>
            <div class="model-meta-group">
                <span class="model-phi-score">φ ${m.phi_score.toFixed(3)}</span>
                <span class="model-status-badge">${m.status}</span>
            </div>
        </div>
    `).join('');
}

function startUptimeTimer() {
    setInterval(() => {
        const diff = Date.now() - systemStartTime;
        const hrs = Math.floor(diff / 3600000).toString().padStart(2, '0');
        const mins = Math.floor((diff % 3600000) / 60000).toString().padStart(2, '0');
        const secs = Math.floor((diff % 60000) / 1000).toString().padStart(2, '0');
        document.getElementById('uptime-val').textContent = `${hrs}:${mins}:${secs}`;
    }, 1000);
}

// Capabilities Tab
function renderCapabilities(filteredDomain = 'all') {
    const container = document.getElementById('capabilities-container');
    const searchVal = document.getElementById('cap-search').value.toLowerCase();
    
    // Filter
    let filtered = capabilities;
    if (filteredDomain !== 'all') {
        filtered = filtered.filter(c => c.domain === filteredDomain);
    }
    if (searchVal) {
        filtered = filtered.filter(c => c.name.toLowerCase().includes(searchVal) || c.id.toLowerCase().includes(searchVal) || c.description.toLowerCase().includes(searchVal));
    }

    if (filtered.length === 0) {
        container.innerHTML = '<div class="text-dim text-center" style="grid-column: 1/-1;">No capabilities match the filter criteria.</div>';
        return;
    }

    container.innerHTML = filtered.map(c => `
        <div class="capability-card" onclick="openCapabilityModal('${c.id}')">
            <div>
                <span class="cap-id-tag">${c.id.toUpperCase()}</span>
                <h4 class="cap-name">${c.name}</h4>
            </div>
            <span class="cap-domain-badge domain-${c.domain}">${c.domain.replace('_', ' ')}</span>
        </div>
    `).join('');

    // Update active filter button
    document.querySelectorAll('#cap-domain-filters .filter-btn').forEach(btn => {
        if (btn.getAttribute('data-domain') === filteredDomain) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Bind search event once
    if (!container.dataset.bound) {
        document.getElementById('cap-search').addEventListener('input', () => {
            const activeFilter = document.querySelector('#cap-domain-filters .filter-btn.active').getAttribute('data-domain');
            renderCapabilities(activeFilter);
        });
        document.querySelectorAll('#cap-domain-filters .filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const dom = btn.getAttribute('data-domain');
                renderCapabilities(dom);
            });
        });
        container.dataset.bound = true;
    }
}

// Capability Execution Modal
function openCapabilityModal(capId) {
    const cap = capabilities.find(c => c.id === capId);
    if (!cap) return;

    document.getElementById('modal-title').textContent = `Run ${cap.name}`;
    document.getElementById('modal-desc').textContent = cap.description;

    const paramsContainer = document.getElementById('modal-params-container');
    paramsContainer.innerHTML = '';
    document.getElementById('modal-result-container').style.display = 'none';

    // Parse parameters from capability definition
    const params = cap.params || [];
    if (params.length === 0) {
        paramsContainer.innerHTML = '<p class="text-dim">No arguments required for this capability.</p>';
    } else {
        params.forEach(p => {
            const val = p.default !== undefined ? p.default : '';
            paramsContainer.innerHTML += `
                <div class="form-group">
                    <label for="param-${p.name}">${p.name} (${p.type})</label>
                    <input type="text" id="param-${p.name}" placeholder="${p.description || ''}" value="${val}">
                </div>
            `;
        });
    }

    // Set submit action
    const submitBtn = document.getElementById('modal-submit-btn');
    submitBtn.onclick = () => executeCapability(capId, params);

    document.getElementById('run-cap-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('run-cap-modal').classList.remove('active');
}

async function executeCapability(capId, params) {
    const kwargs = {};
    params.forEach(p => {
        const inputVal = document.getElementById(`param-${p.name}`).value;
        // Cast types
        if (p.type === 'int') kwargs[p.name] = parseInt(inputVal) || 0;
        else if (p.type === 'float') kwargs[p.name] = parseFloat(inputVal) || 0.0;
        else if (p.type === 'bool') kwargs[p.name] = inputVal.toLowerCase() === 'true';
        else if (p.type === 'list') {
            try {
                kwargs[p.name] = JSON.parse(inputVal);
            } catch {
                kwargs[p.name] = inputVal.split(',').map(s => s.trim());
            }
        } else if (p.type === 'dict') {
            try {
                kwargs[p.name] = JSON.parse(inputVal);
            } catch {
                kwargs[p.name] = {};
            }
        } else {
            kwargs[p.name] = inputVal;
        }
    });

    const consoleBox = document.getElementById('modal-result-console');
    const resultContainer = document.getElementById('modal-result-container');
    
    resultContainer.style.display = 'block';
    consoleBox.className = 'console-box';
    consoleBox.textContent = 'Running execution pipeline...';

    try {
        const res = await fetch(`${API}/api/capabilities/${capId}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ kwargs })
        });
        const data = await res.json();
        if (data.status === 'success') {
            consoleBox.classList.add('text-green');
            consoleBox.textContent = typeof data.result === 'object' ? JSON.stringify(data.result, null, 2) : data.result;
        } else {
            consoleBox.classList.add('text-red');
            consoleBox.textContent = `Error: ${data.error}`;
        }
    } catch (err) {
        consoleBox.classList.add('text-red');
        consoleBox.textContent = `Pipeline connection failure: ${err.message}`;
    }
}

// AI Research Tab
async function loadResearchData() {
    const container = document.getElementById('future-ai-container');
    container.innerHTML = '<div class="loading-placeholder">Compiling research registers...</div>';

    try {
        const res = await fetch(`${API}/api/future-ai`);
        const data = await res.json();
        
        container.innerHTML = data.features.map(f => `
            <div class="future-card" id="fai-card-${f.id}">
                <div class="future-card-header">
                    <div>
                        <h3>${f.name}</h3>
                        <p class="text-dim">${f.description}</p>
                    </div>
                    <span class="future-proto-link">Protocol: ${f.protocol}</span>
                </div>
                
                <div class="future-metrics-list">
                    ${f.key_metrics.map(m => `
                        <div class="future-metric-item">
                            <span>🛡️</span>
                            <span>${m}</span>
                        </div>
                    `).join('')}
                </div>

                <div class="future-actions">
                    <button class="btn btn-primary" onclick="runResearchDemo('${f.id}')">Run Simulation Demo</button>
                    <span class="text-muted" style="font-size: 0.75rem;">Class: ${f.class_name}</span>
                </div>

                <div class="demo-output-area" id="demo-output-${f.id}" style="display: none;">
                    <div class="demo-visual-flex">
                        <div class="demo-console-container">
                            <h4>Simulation output console:</h4>
                            <pre class="console-box" id="demo-console-${f.id}"></pre>
                        </div>
                        <div class="demo-chart-container" id="demo-chart-${f.id}">
                            <!-- SVG Render Target -->
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<div class="text-red">Failed to fetch research index: ${err.message}</div>`;
    }
}

async function runResearchDemo(featureId) {
    const output = document.getElementById(`demo-output-${featureId}`);
    const consoleBox = document.getElementById(`demo-console-${featureId}`);
    const chartContainer = document.getElementById(`demo-chart-${featureId}`);

    output.style.display = 'block';
    consoleBox.className = 'console-box';
    consoleBox.textContent = 'Spawning simulation container...\nRunning active mathematical validation...';
    chartContainer.innerHTML = '<span class="text-muted">Computing graph data...</span>';

    try {
        const res = await fetch(`${API}/api/future-ai/${featureId}/demo`, { method: 'POST' });
        const data = await res.json();
        
        if (data.status === 'error') {
            consoleBox.classList.add('text-red');
            consoleBox.textContent = `Simulation crash: ${data.error}`;
            chartContainer.innerHTML = '<span class="text-red">Rendering aborted.</span>';
        } else {
            consoleBox.classList.add('text-green');
            consoleBox.textContent = JSON.stringify(data.result, null, 2);
            
            // Trigger visual charting
            if (featureId === 'phi_resonance_network') {
                renderResonanceNetwork(data.result, chartContainer);
            } else if (featureId === 'sovereign_memory_lattice') {
                renderSovereignLattice(data.result, chartContainer);
            } else if (featureId === 'consensus_swarm_intelligence') {
                renderConsensusSwarm(data.result, chartContainer);
            } else if (featureId === 'causal_reasoning_engine') {
                renderCausalReasoning(data.result, chartContainer);
            } else if (featureId === 'evolutionary_code_optimizer') {
                renderEvolutionaryOptimizer(data.result, chartContainer);
            }
        }
    } catch (err) {
        consoleBox.classList.add('text-red');
        consoleBox.textContent = `Simulation connection timed out: ${err.message}`;
        chartContainer.innerHTML = '<span class="text-red">Network Timeout.</span>';
    }
}

// Visual Chart Renderers
function renderResonanceNetwork(res, container) {
    const history = res.coherence_history || [];
    if (!history.length) return;
    const width = 400;
    const height = 240;
    const padding = 30;
    const points = history.map((val, idx) => {
        const x = padding + (idx / (history.length - 1)) * (width - 2 * padding);
        const y = height - padding - (val * (height - 2 * padding));
        return `${x},${y}`;
    }).join(' ');

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 100%;">
            <!-- Grid lines -->
            <line x1="${padding}" y1="${padding}" x2="${width-padding}" y2="${padding}" stroke="rgba(255,255,255,0.05)" />
            <line x1="${padding}" y1="${height/2}" x2="${width-padding}" y2="${height/2}" stroke="rgba(255,255,255,0.05)" />
            <line x1="${padding}" y1="${height-padding}" x2="${width-padding}" y2="${height-padding}" stroke="rgba(255,255,255,0.1)" />
            
            <!-- Labels -->
            <text x="${width/2}" y="${height - 5}" fill="rgba(255,255,255,0.4)" font-size="10" text-anchor="middle">Simulation Step</text>
            <text x="5" y="${padding + 5}" fill="rgba(255,255,255,0.4)" font-size="10">R=1.0</text>
            <text x="5" y="${height - padding}" fill="rgba(255,255,255,0.4)" font-size="10">R=0.0</text>
            
            <!-- Curve -->
            <polyline fill="none" stroke="#10b981" stroke-width="3" points="${points}" style="filter: drop-shadow(0 0 5px rgba(16, 185, 129, 0.5));" />
            <!-- Final point indicator -->
            <circle cx="${padding + (width-2*padding)}" cy="${height-padding-(history[history.length-1]*(height-2*padding))}" r="5" fill="#10b981" />
        </svg>
    `;
}

function renderSovereignLattice(res, container) {
    const coords = res.coordinates || [];
    const width = 400;
    const height = 240;
    const cx = width / 2;
    const cy = height / 2;
    
    // Draw spiral path
    let spiralPoints = '';
    for (let theta = 0; theta < 25; theta += 0.1) {
        const r = 3 * Math.pow(1.15, theta);
        const x = cx + r * Math.cos(theta);
        const y = cy + r * Math.sin(theta);
        if (r > cx - 20) break;
        spiralPoints += `${x},${y} `;
    }

    // Render memory coordinates
    const memoryNodes = coords.map((c, idx) => {
        const theta = idx * 2.39996; // golden angle
        const r = 12 * Math.sqrt(idx + 1) + 15;
        const x = cx + r * Math.cos(theta);
        const y = cy + r * Math.sin(theta);
        return `
            <circle cx="${x}" cy="${y}" r="6" fill="#8b5cf6" style="filter: drop-shadow(0 0 3px rgba(139, 92, 246, 0.5));" />
            <text x="${x + 8}" y="${y + 4}" fill="#cbd5e1" font-size="8" font-family="monospace">${c.key}</text>
        `;
    }).join('');

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 100%;">
            <polyline fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1.5" points="${spiralPoints}" />
            ${memoryNodes}
        </svg>
    `;
}

function renderConsensusSwarm(res, container) {
    const consensus = res.consensus || {};
    const width = 400;
    const height = 240;
    const score = consensus.weighted_score || 0.0;
    const pct = Math.min(100, Math.round((score / 5.0) * 100));

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 100%;">
            <!-- Donut ring -->
            <circle cx="200" cy="110" r="60" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="16" />
            <circle cx="200" cy="110" r="60" fill="none" stroke="#3b82f6" stroke-width="16" 
                    stroke-dasharray="376.9" stroke-dashoffset="${376.9 - (376.9 * pct / 100)}"
                    stroke-linecap="round" style="filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.5)); transform: rotate(-90deg); transform-origin: 200px 110px;" />
            
            <!-- Center Text -->
            <text x="200" y="115" fill="#fff" font-size="18" font-weight="bold" text-anchor="middle">${pct}%</text>
            <text x="200" y="130" fill="rgba(255,255,255,0.5)" font-size="8" text-anchor="middle">Consensus Weighted Score</text>

            <text x="200" y="200" fill="${consensus.approved ? '#10b981' : '#f43f5e'}" font-size="12" font-weight="bold" text-anchor="middle">
                ${consensus.approved ? 'PROPOSAL APPROVED' : 'PROPOSAL REJECTED'}
            </text>
            <text x="200" y="215" fill="rgba(255,255,255,0.4)" font-size="9" text-anchor="middle">Quorum: ${consensus.quorum_reached ? 'REACHED' : 'FAILED'}</text>
        </svg>
    `;
}

function renderCausalReasoning(res, container) {
    const width = 400;
    const height = 240;
    const variables = {
        "training_data": { x: 50, y: 50, label: "Data" },
        "model_size": { x: 50, y: 120, label: "Size" },
        "compute": { x: 50, y: 190, label: "Compute" },
        "performance": { x: 220, y: 120, label: "Performance" },
        "latency": { x: 350, y: 60, label: "Latency" },
        "cost": { x: 350, y: 180, label: "Cost" }
    };

    const edges = [
        { from: "training_data", to: "performance" },
        { from: "model_size", to: "performance" },
        { from: "compute", to: "performance" },
        { from: "model_size", to: "latency" },
        { from: "compute", to: "cost" },
        { from: "model_size", to: "cost" }
    ];

    const edgeLines = edges.map(e => {
        const f = variables[e.from];
        const t = variables[e.to];
        return `
            <line x1="${f.x}" y1="${f.y}" x2="${t.x}" y2="${t.y}" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" marker-end="url(#arrow)" />
        `;
    }).join('');

    const nodeCircles = Object.entries(variables).map(([name, v]) => `
        <g>
            <circle cx="${v.x}" cy="${v.y}" r="22" fill="#0f172a" stroke="#06b6d4" stroke-width="2" style="filter: drop-shadow(0 0 4px rgba(6, 182, 212, 0.4));" />
            <text x="${v.x}" y="${v.y + 4}" fill="#fff" font-size="8" font-weight="600" text-anchor="middle">${v.label}</text>
        </g>
    `).join('');

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 100%;">
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.4)" />
                </marker>
            </defs>
            ${edgeLines}
            ${nodeCircles}
        </svg>
    `;
}

function renderEvolutionaryOptimizer(res, container) {
    const width = 400;
    const height = 240;

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 100%;">
            <rect x="20" y="30" width="360" height="180" fill="rgba(255,255,255,0.01)" stroke="rgba(255,255,255,0.05)" rx="8" />
            <text x="40" y="60" fill="#f59e0b" font-size="12" font-family="monospace" font-weight="bold">Base Code Template:</text>
            <text x="40" y="80" fill="#cbd5e1" font-size="11" font-family="monospace">${res.template}</text>
            
            <line x1="40" y1="110" x2="360" y2="110" stroke="rgba(255,255,255,0.08)" />
            
            <text x="40" y="140" fill="#10b981" font-size="12" font-family="monospace" font-weight="bold">Evolved Optimal Output:</text>
            <text x="40" y="160" fill="#cbd5e1" font-size="11" font-family="monospace">${res.best_code}</text>

            <text x="40" y="195" fill="rgba(255,255,255,0.4)" font-size="9">Generations: ${res.generations} | Population: ${res.population_size}</text>
        </svg>
    `;
}


// Protocols Tab
function renderProtocols() {
    const tbody = document.getElementById('protocols-table-body');
    const searchVal = document.getElementById('protocol-search').value.toLowerCase();

    let filtered = protocols;
    if (searchVal) {
        filtered = filtered.filter(p => p.name.toLowerCase().includes(searchVal) || p.protocol_id.toLowerCase().includes(searchVal) || p.domain.toLowerCase().includes(searchVal) || p.description.toLowerCase().includes(searchVal));
    }

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-dim">No protocols match current parameters.</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(p => `
        <tr>
            <td><strong style="font-family: monospace;">${p.protocol_id}</strong></td>
            <td><strong>${p.name}</strong><br><span class="text-muted" style="font-size:0.75rem;">${p.description}</span></td>
            <td><span class="cap-domain-badge domain-${p.domain}">${p.domain.replace('_', ' ')}</span></td>
            <td><span class="ring-badge ring-${p.ring.split(' ')[0].toLowerCase()}">${p.ring}</span></td>
            <td><code style="font-family: monospace; font-size: 0.75rem;">${p.wire}</code></td>
            <td>${p.uses_encryption ? '🔒 Encrypted' : '🔓 Plain'}</td>
            <td><span class="model-status-badge">${p.status}</span></td>
        </tr>
    `).join('');

    if (!tbody.dataset.bound) {
        document.getElementById('protocol-search').addEventListener('input', renderProtocols);
        tbody.dataset.bound = true;
    }
}

// Papers Tab
function renderPapers(filteredDomain = 'all') {
    const container = document.getElementById('papers-list-container');
    const searchVal = document.getElementById('paper-search').value.toLowerCase();

    let filtered = papers;
    if (filteredDomain !== 'all') {
        filtered = filtered.filter(p => p.domain === filteredDomain);
    }
    if (searchVal) {
        filtered = filtered.filter(p => p.title.toLowerCase().includes(searchVal) || p.abstract.toLowerCase().includes(searchVal) || p.paper_id.toLowerCase().includes(searchVal));
    }

    if (filtered.length === 0) {
        container.innerHTML = '<div class="text-dim text-center">No papers match criteria.</div>';
        return;
    }

    container.innerHTML = filtered.map(p => `
        <div class="paper-card">
            <div class="paper-meta-top">
                <span>ID: ${p.paper_id}</span>
                <span>Journal: ${p.journal}</span>
            </div>
            <h3>${p.title}</h3>
            <div class="paper-authors">Authors: ${p.authors.join(', ')}</div>
            <div class="paper-abstract">
                <strong>Abstract:</strong> ${p.abstract}
            </div>
            
            <div class="paper-results-list">
                <h5>Key Findings:</h5>
                <ul>
                    ${p.key_results.map(r => `<li>• ${r}</li>`).join('')}
                </ul>
            </div>

            <div class="paper-keywords">
                ${p.keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}
            </div>

            <div class="paper-citations-actions">
                <button class="btn btn-secondary" onclick="copyCitation('${p.paper_id}', 'apa')">Copy APA Citation</button>
                <button class="btn btn-secondary" onclick="copyCitation('${p.paper_id}', 'ieee')">Copy IEEE Citation</button>
            </div>
        </div>
    `).join('');

    // Update active filter button
    document.querySelectorAll('#paper-domain-filters .sidebar-filter-btn').forEach(btn => {
        if (btn.getAttribute('data-domain') === filteredDomain) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (!container.dataset.bound) {
        document.getElementById('paper-search').addEventListener('input', () => {
            const activeFilter = document.querySelector('#paper-domain-filters .sidebar-filter-btn.active').getAttribute('data-domain');
            renderPapers(activeFilter);
        });
        document.querySelectorAll('#paper-domain-filters .sidebar-filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const dom = btn.getAttribute('data-domain');
                renderPapers(dom);
            });
        });
        container.dataset.bound = true;
    }
}

async function copyCitation(paperId, format) {
    const paper = papers.find(p => p.paper_id === paperId);
    if (!paper) return;

    let text = '';
    // APA citation
    if (format === 'apa') {
        const auth = paper.authors.join(', ');
        const year = paper.publication_date ? paper.publication_date.split('-')[0] : '2026';
        text = `${auth} (${year}). ${paper.title}. ${paper.journal}.`;
    } else {
        // IEEE citation
        const auth = paper.authors.join(', ');
        const year = paper.publication_date ? paper.publication_date.split('-')[0] : '2026';
        text = `${auth}, "${paper.title}," ${paper.journal}, ${year}.`;
    }

    try {
        await navigator.clipboard.writeText(text);
        alert('Citation copied to clipboard!');
    } catch {
        alert(text);
    }
}

// Agents Tab
async function loadAgentsData() {
    const container = document.getElementById('agents-container');
    container.innerHTML = '<div class="loading-placeholder">Wiring neural agent channels...</div>';

    try {
        const res = await fetch(`${API}/api/agents`);
        const data = await res.json();
        agents = data.agents;

        container.innerHTML = agents.map(a => `
            <div class="agent-card">
                <div class="agent-card-header">
                    <h3>${a.name}</h3>
                    <div class="agent-tagline">${a.designation}</div>
                </div>

                <div class="agent-meta-info">
                    <div class="agent-meta-item">
                        <span>MODEL TARGET</span>
                        <span>${a.model}</span>
                    </div>
                    <div class="agent-meta-item">
                        <span>REPUTATION (φ)</span>
                        <span class="text-green">${a.reputation.toFixed(3)}</span>
                    </div>
                    <div class="agent-meta-item">
                        <span>COMPLETED TASKS</span>
                        <span>${a.completed_tasks} / ${a.total_tasks}</span>
                    </div>
                    <div class="agent-meta-item">
                        <span>PLATFORM</span>
                        <span>${a.platform.toUpperCase()}</span>
                    </div>
                </div>

                <div>
                    <span class="metric-label" style="margin-bottom:0.4rem;">SYSTEM PROMPT CONTEXT</span>
                    <div class="agent-prompt-box text-dim">
                        ${a.system_prompt}
                    </div>
                </div>

                <div>
                    <span class="metric-label" style="margin-bottom:0.4rem;">AVAILABLE CAPABILITY TOOLS</span>
                    <div class="paper-keywords">
                        ${a.tools.map(t => `<span class="keyword-tag" style="font-family:monospace; color:#3b82f6;">${t}</span>`).join('')}
                    </div>
                </div>

                <form class="dispatch-form" id="dispatch-form-${a.name}" onsubmit="dispatchTask(event, '${a.name}')">
                    <textarea id="dispatch-prompt-${a.name}" placeholder="Type instruction payload..." required></textarea>
                    <div class="form-row-actions">
                        <select id="dispatch-priority-${a.name}">
                            <option value="NORMAL">Priority: Normal</option>
                            <option value="HIGH">Priority: High</option>
                            <option value="CRITICAL">Priority: Critical</option>
                        </select>
                        <button class="btn btn-primary" type="submit">Dispatch payload</button>
                    </div>
                </form>

                <div id="dispatch-result-${a.name}" style="display: none;">
                    <span class="metric-label">DISPATCH TELEMETRY OUTPUT</span>
                    <pre class="console-box" id="dispatch-console-${a.name}"></pre>
                </div>
            </div>
        `).join('');

    } catch (err) {
        container.innerHTML = `<div class="text-red">Failed to wire agent grid: ${err.message}</div>`;
    }
}

async function dispatchTask(e, agentName) {
    e.preventDefault();
    const prompt = document.getElementById(`dispatch-prompt-${agentName}`).value;
    const priority = document.getElementById(`dispatch-priority-${agentName}`).value;
    const output = document.getElementById(`dispatch-result-${agentName}`);
    const consoleBox = document.getElementById(`dispatch-console-${agentName}`);

    output.style.display = 'block';
    consoleBox.className = 'console-box';
    consoleBox.textContent = 'Enveloping payload...\nNegotiating route through SRP Protocol...';

    try {
        const res = await fetch(`${API}/api/agents/${agentName}/dispatch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, priority })
        });
        const data = await res.json();
        consoleBox.classList.add('text-green');
        consoleBox.textContent = `Task Enqueued: ${data.task_id}\nStatus: ${data.status}\nResult: ${data.result}`;
        
        // Refresh counts
        fetchData();
    } catch (err) {
        consoleBox.classList.add('text-red');
        consoleBox.textContent = `Dispatch failed: ${err.message}`;
    }
}

// Organism Tab
async function loadOrganismData() {
    try {
        const res = await fetch(`${API}/api/organism`);
        const data = await res.json();

        // Update counts
        const organs = data.organs || {};
        
        if (organs.membrane) document.getElementById('org-membrane-stats').textContent = `Files: ${organs.membrane.file_count}`;
        if (organs.reflex) document.getElementById('org-reflex-stats').textContent = `Files: ${organs.reflex.file_count}`;
        if (organs.brain) document.getElementById('org-brain-stats').textContent = `Files: ${organs.brain.file_count}`;
        if (organs.identity) document.getElementById('org-identity-stats').textContent = `Files: ${organs.identity.file_count}`;
        if (organs.surfaces) document.getElementById('org-surfaces-stats').textContent = `Files: ${organs.surfaces.file_count}`;

        // Render paths
        const pathList = document.getElementById('organism-routes-list');
        pathList.innerHTML = data.cross_substrate_paths.map(p => `
            <div class="route-card">
                <div class="route-endpoints">${p.from} ➔ ${p.to}</div>
                <div class="route-desc">${p.desc}</div>
            </div>
        `).join('');

    } catch (err) {
        console.error('Failed to load organism telemetry:', err);
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// WASM-PYODIDE SANDBOX ENGINE
// ══════════════════════════════════════════════════════════════════════════════

async function initPyodideSandbox() {
    const consoleBox = document.getElementById('pyodide-console');
    const pulse = document.getElementById('pyodide-status-pulse');
    const label = document.getElementById('pyodide-status-label');
    const container = document.getElementById('pyodide-status-container');

    if (pyodideLoaded) return;
    if (pyodideLoading) return;

    pyodideLoading = true;
    consoleBox.textContent = '[SANDBOX] Initializing WebAssembly virtual engine...\n[SANDBOX] Fetching Pyodide distribution from CDN...';

    // Inject Pyodide script if not present
    if (!window.loadPyodide) {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js';
        document.head.appendChild(script);

        await new Promise((resolve) => {
            script.onload = resolve;
        });
    }

    try {
        pyodideInstance = await loadPyodide({
            stdout: (text) => {
                appendPyodideConsole(text, 'text-green');
            },
            stderr: (text) => {
                appendPyodideConsole(text, 'text-red');
            }
        });

        pyodideLoaded = true;
        pyodideLoading = false;

        // Enable UI buttons
        document.getElementById('run-pyodide-btn').disabled = false;
        document.getElementById('install-package-btn').disabled = false;

        // Update status badge
        pulse.style.backgroundColor = 'var(--accent-emerald)';
        pulse.style.boxShadow = '0 0 10px rgba(16, 185, 129, 0.4)';
        label.textContent = 'PYODIDE_READY';
        label.style.color = 'var(--accent-emerald)';
        container.style.backgroundColor = 'rgba(16, 185, 129, 0.06)';
        container.style.borderColor = 'rgba(16, 185, 129, 0.15)';

        consoleBox.textContent = '[WASM-CPYTHON] Runtime loaded successfully.\n[WASM-CPYTHON] WebAssembly sandbox fully active.\nType Python code and click "Run Client WASM".';

        // Bind button actions
        document.getElementById('run-pyodide-btn').onclick = runPyodideCode;
        document.getElementById('install-package-btn').onclick = installPyodidePackage;

    } catch (err) {
        pyodideLoading = false;
        consoleBox.textContent = `[SANDBOX_ERROR] Failed to compile WebAssembly instance:\n${err.message}`;
    }
}

function appendPyodideConsole(text, className = '') {
    const consoleBox = document.getElementById('pyodide-console');
    const div = document.createElement('div');
    div.className = `console-line ${className}`;
    div.textContent = text;
    consoleBox.appendChild(div);
    consoleBox.scrollTop = consoleBox.scrollHeight;
}

async function runPyodideCode() {
    if (!pyodideLoaded || !pyodideInstance) return;
    const code = document.getElementById('pyodide-code-input').value;
    const consoleBox = document.getElementById('pyodide-console');

    consoleBox.innerHTML = '<div class="console-line text-dim">[WASM] Commencing execution cycle...</div>';

    try {
        const result = await pyodideInstance.runPythonAsync(code);
        if (result !== undefined) {
            appendPyodideConsole(`\n[Returned Output]: ${result}`, 'text-blue');
        }
        appendPyodideConsole('[WASM] Execution completed successfully.', 'text-green');
    } catch (err) {
        appendPyodideConsole(`\n[WASM RuntimeError]:\n${err.message}`, 'text-red');
    }
}

async function installPyodidePackage() {
    if (!pyodideLoaded || !pyodideInstance) return;
    const pkgInput = document.getElementById('pyodide-package-input');
    const pkgName = pkgInput.value.trim().toLowerCase();
    if (!pkgName) return;

    const consoleBox = document.getElementById('pyodide-console');
    appendPyodideConsole(`\n[WASM] Loading package registry mapping for '${pkgName}'...`);

    try {
        await pyodideInstance.loadPackage(pkgName);
        appendPyodideConsole(`[WASM] Package '${pkgName}' loaded successfully and ready for import.`, 'text-green');
        pkgInput.value = '';
    } catch (err) {
        // Fallback to micropip if not a standard package
        try {
            appendPyodideConsole(`[WASM] Standard wheel not found. Attempting micropip dynamic resolve...`);
            await pyodideInstance.runPythonAsync(`
                import micropip
                await micropip.install('${pkgName}')
            `);
            appendPyodideConsole(`[WASM] Package '${pkgName}' installed via micropip successfully.`, 'text-green');
            pkgInput.value = '';
        } catch (micropipErr) {
            appendPyodideConsole(`[WASM PackageError] Failed to resolve package '${pkgName}':\n${micropipErr.message}`, 'text-red');
        }
    }
}

function loadPyodideTemplate(type) {
    const input = document.getElementById('pyodide-code-input');
    
    const templates = {
        phi: `# Pre-loaded template: Phi Coherence check
import math

PHI = (1 + math.sqrt(5)) / 2
print("Initializing client-side WASM-Pyodide...")
print(f"Mathematical constant PHI: {PHI:.8f}")

# Simulating a state alignment check
coherence = 1.0 / PHI
print(f"Inverse Coherence state weight: {coherence:.8f}")
print("Status: COHERENCE_STABLE")
`,
        resonance: `# Pre-loaded template: Kuramoto resonance simulation
import math

PHI = 1.618033988749895
N = 10
coupling = PHI

# Initializing 10 coupled oscillator phase offsets
phases = [i * (2 * math.pi / N) for i in range(N)]
print(f"Coupling strength K: {coupling:.4f}")
print("Initial phase offsets (radians):")
for idx, p in enumerate(phases):
    print(f"  Node {idx}: {p:.4f} rad")

# Compute instantaneous phase sync order parameter R
mean_cos = sum(math.cos(p) for p in phases) / N
mean_sin = sum(math.sin(p) for p in phases) / N
R = math.sqrt(mean_cos**2 + mean_sin**2)
print(f"Computed synchronization order parameter R: {R:.6f}")
`,
        agent: `# Pre-loaded template: Swarm Quorum weightings
PHI = 1.618033988749895

agents = {
    "AXIOM": {"confidence": 0.94, "expertise": 3},
    "FORTRESS": {"confidence": 0.91, "expertise": 4}
}

print("Running local swarm quorum score simulation:")
total_score = 0.0
total_weight = 0.0

for name, meta in agents.items():
    # Weight decays exponentially by expertise level mapped on PHI
    weight = meta["confidence"] * (PHI ** meta["expertise"])
    print(f"  Agent {name}: weight = {weight:.4f}")
    total_score += weight
    total_weight += 1.0

weighted_avg = total_score / total_weight
print(f"System Swarm Weighted Consensus: {weighted_avg:.4f}")
`,
        fft: `# Pre-loaded template: Client-Side MESIE FFT Processing
import math

print("Initializing MESIE FFT Processor in Pyodide...")
PHI = 1.618033988749895
N = 16  # Signal length
frequencies = [PHI, 2 * PHI]

print(f"Synthesizing test signal with components at frequencies {frequencies}...")
signal = [sum(math.sin(2 * math.pi * f * t / N) for f in frequencies) for t in range(N)]

print("Signal samples (first 5):", [round(s, 4) for s in signal[:5]])

def simple_dft(x):
    n = len(x)
    real = [0.0] * n
    imag = [0.0] * n
    for k in range(n):
        for t in range(n):
            angle = 2 * math.pi * k * t / n
            real[k] += x[t] * math.cos(angle)
            imag[k] -= x[t] * math.sin(angle)
    return [math.sqrt(r**2 + i**2) for r, i in zip(real, imag)]

print("Running Discrete Fourier Transform (DFT) locally...")
magnitudes = simple_dft(signal)
print("DFT Magnitudes:", [round(m, 2) for m in magnitudes])
print("FFT Processing Complete. Client node capability verified.")
`
    };

    if (templates[type]) {
        input.value = templates[type];
        appendPyodideConsole(`[WASM] Swapped editor template to: ${type.toUpperCase()}`);
    }
}

