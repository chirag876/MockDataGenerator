/* ── Config ───────────────────────────────────────────────────────────── */
const API = "http://localhost:8000";

/* ── State ────────────────────────────────────────────────────────────── */
const state = {
  topics: {},   // { name: { description, fields } }
  formats: [],
  domains: [],
  relSets: [],
  fieldTypes: [],

  // Quick
  quickFormat: "JSON",

  // Domain
  selectedDomain: null,
  domainFormat: "JSON",

  // Relational
  selectedRelSet: null,
  relFormat: "JSON",

  // Schema builder
  schemaTables: [],   // [{ name, fields:[{name,type,constraints,references_table,references_field}], num_records }]
  activeSchemaTable: null,
  schemaFormat: "JSON",

  // DB Seeder
  seedMode: "domain",
};

/* ── Utilities ────────────────────────────────────────────────────────── */
function $(id) { return document.getElementById(id); }

function showToast(msg, type = "info") {
  const t = $("toast");
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => { t.className = "toast"; }, 3000);
}

function setLoading(btn, on) {
  if (on) btn.classList.add("loading");
  else btn.classList.remove("loading");
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      typeof err.detail === "object"
        ? JSON.stringify(err.detail)
        : err.detail || "Request failed"
    );
  }
  return res;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `(${(bytes / 1024).toFixed(1)} KB)`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function buildFormatGrid(containerId, stateKey) {
  const container = $(containerId);
  container.innerHTML = "";
  state.formats.forEach(f => {
    const btn = document.createElement("button");
    btn.className = `format-btn${state[stateKey] === f ? " active" : ""}`;
    btn.textContent = f;
    btn.onclick = () => {
      state[stateKey] = f;
      container.querySelectorAll(".format-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    };
    container.appendChild(btn);
  });
}

function renderMultiPreview(containerId, tablesData) {
  const container = $(containerId);
  container.innerHTML = "";
  container.style.display = "flex";

  Object.entries(tablesData).forEach(([tableName, records]) => {
    const div = document.createElement("div");
    div.className = "multi-preview-table";
    div.innerHTML = `
      <div class="multi-preview-header">
        <span class="multi-preview-title">${tableName}</span>
        <span class="multi-preview-count">${records.length} records</span>
      </div>
      <div class="multi-preview-body">
        <pre>${JSON.stringify(records.slice(0, 3), null, 2)}${records.length > 3 ? `\n... and ${records.length - 3} more` : ""}</pre>
      </div>
    `;
    container.appendChild(div);
  });
}

/* ── Sidebar navigation ───────────────────────────────────────────────── */
const TAB_LABELS = {
  quick: "Quick Generate",
  domain: "By Domain",
  relational: "Relational Sets",
  schema: "Schema Builder",
  seeder: "DB Seeder",
};

document.querySelectorAll(".nav-item").forEach(item => {
  item.addEventListener("click", e => {
    e.preventDefault();
    const tab = item.dataset.tab;
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    item.classList.add("active");
    $(`tab-${tab}`).classList.add("active");
    $("breadcrumbCurrent").textContent = TAB_LABELS[tab];
  });
});

/* ── Bootstrap — load all API data on page load ───────────────────────── */
async function bootstrap() {
  try {
    // Topics
    const topicsRes = await apiFetch("/topics");
    const topicsData = await topicsRes.json();
    topicsData.forEach(t => { state.topics[t.name] = t; });

    // Formats
    const fmtRes = await apiFetch("/formats");
    const fmtData = await fmtRes.json();
    state.formats = fmtData.formats;

    // Domains
    const domRes = await apiFetch("/domains");
    state.domains = await domRes.json();

    // Relational sets
    const relRes = await apiFetch("/relational-sets");
    state.relSets = await relRes.json();

    // Field types (for schema builder)
    const ftRes = await apiFetch("/field-types");
    state.fieldTypes = await ftRes.json();

    // Init all tabs
    initQuickTab();
    initDomainTab();
    initRelationalTab();
    initSchemaTab();
    initSeederTab();

  } catch (err) {
    showToast("API unreachable — is the backend running?", "error");
    console.error(err);
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   TAB 1 — Quick Generate
═══════════════════════════════════════════════════════════════════════ */
function initQuickTab() {
  // Populate topic dropdown
  const sel = $("quickTopic");
  Object.keys(state.topics).forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name.replace(/_/g, " ");
    sel.appendChild(opt);
  });

  updateQuickTopicMeta();
  sel.addEventListener("change", updateQuickTopicMeta);
  // Format grid
  buildFormatGrid("quickFormatGrid", "quickFormat");

  // Records slider
  const recordInput = $("quickRecords");
  const presetButtons = document.querySelectorAll(".record-presets .record-btn");

  presetButtons.forEach(btn => {

    btn.addEventListener("click", () => {

      const value = btn.dataset.value;

      recordInput.value = value;

      presetButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

    });

  });

  recordInput.addEventListener("input", () => {

    recordInput.value = recordInput.value.replace(/\D/g, "");

    if (recordInput.value !== "") {

      let value = parseInt(recordInput.value);

      if (value > 1000)
        value = 1000;

      if (value < 1)
        value = 1;

      recordInput.value = value;
    }

    presetButtons.forEach(btn => {

      btn.classList.toggle(
        "active",
        btn.dataset.value === recordInput.value
      );

    });

  });

  // Buttons
  $("quickGenerateBtn").addEventListener("click", quickGenerate);
  $("quickDownloadBtn").addEventListener("click", quickDownload);
  $("quickCopyBtn").addEventListener("click", quickCopy);
  $("quickRawBtn").addEventListener("click", quickToggleRaw);
}

function updateQuickTopicMeta() {
  const name = $("quickTopic").value;
  const topic = state.topics[name];
  if (!topic) return;

  $("quickTopicDesc").textContent = topic.description;

  const list = $("quickFieldsList");
  list.innerHTML = "";
  (topic.fields || []).forEach(f => {
    const tag = document.createElement("span");
    tag.className = "field-tag";
    tag.textContent = f;
    list.appendChild(tag);
  });
}

async function quickGenerate() {
  const btn = $("quickGenerateBtn");
  setLoading(btn, true);
  try {
    const body = {
      topic: $("quickTopic").value,
      format: state.quickFormat,
      num_records: parseInt($("quickRecords").value),
      seed: $("quickUseSeed").checked ? parseInt($("quickSeed").value) || null : null,
    };

    const res = await apiFetch("/generate", { method: "POST", body: JSON.stringify(body) });
    const data = await res.json();

    if (!data.success) throw new Error(data.error || "Generation failed");

    // Show preview
    const preview = $("quickPreviewCard");
    const code = $("quickPreviewCode");
    preview.style.display = "block";
    preview.dataset.raw = data.data;
    preview.dataset.rawMode = "false";

    // For JSON try to parse and show pretty; others show raw
    let display = data.data;
    if (state.quickFormat === "JSON") {
      try { display = JSON.stringify(JSON.parse(data.data), null, 2); } catch { }
    }
    code.textContent = display.length > 8000 ? display.slice(0, 8000) + "\n... (truncated for preview)" : display;

    const byteLen = new TextEncoder().encode(data.data).length;
    $("quickPreviewMeta").textContent = `${body.num_records} records · ${state.quickFormat} · ${formatBytes(byteLen)}`;

    showToast("Data generated!", "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

async function quickDownload() {
  const btn = $("quickDownloadBtn");
  setLoading(btn, true);
  try {
    const body = {
      topic: $("quickTopic").value,
      format: state.quickFormat,
      num_records: parseInt($("quickRecords").value),
      seed: $("quickUseSeed").checked ? parseInt($("quickSeed").value) || null : null,
    };

    const res = await apiFetch("/download", { method: "POST", body: JSON.stringify(body) });
    const blob = await res.blob();
    const filename = res.headers.get("Content-Disposition")?.match(/filename=(.+)/)?.[1] || "data.json";
    triggerDownload(blob, filename);
    showToast("Download started!", "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

function quickCopy() {
  const code = $("quickPreviewCode").textContent;
  if (!code) { showToast("Generate data first.", "error"); return; }
  navigator.clipboard.writeText(code).then(() => showToast("Copied to clipboard!", "success"));
}

function quickToggleRaw() {
  const preview = $("quickPreviewCard");
  const code = $("quickPreviewCode");
  const raw = preview.dataset.raw || "";
  const isRaw = preview.dataset.rawMode === "true";

  if (isRaw) {
    let display = raw;
    if (state.quickFormat === "JSON") {
      try { display = JSON.stringify(JSON.parse(raw), null, 2); } catch { }
    }
    code.textContent = display;
    preview.dataset.rawMode = "false";
    $("quickRawBtn").textContent = "Raw";
  } else {
    code.textContent = raw;
    preview.dataset.rawMode = "true";
    $("quickRawBtn").textContent = "Pretty";
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   TAB 2 — By Domain
═══════════════════════════════════════════════════════════════════════ */
const DOMAIN_ICONS = {
  ecommerce: "🛒",
  hr: "👥",
  healthcare: "🏥",
  education: "🎓",
  banking: "🏦",
  logistics: "🚚",
  real_estate: "🏠",
  iot: "📡",
  social_media: "📱",
  aviation: "✈️",
  weather: "🌤️",
};

function initDomainTab() {
  const grid = $("domainGrid");
  grid.innerHTML = "";

  state.domains.forEach(domain => {
    const card = document.createElement("div");
    card.className = "domain-card";
    card.innerHTML = `
      <div class="domain-card-icon">${DOMAIN_ICONS[domain.name] || "🗂️"}</div>
      <div class="domain-card-name">${domain.name.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</div>
      <div class="domain-card-desc">${domain.description}</div>
    `;
    card.addEventListener("click", () => selectDomain(domain, card));
    grid.appendChild(card);
  });

  // Format grid
  buildFormatGrid("domainFormatGrid", "domainFormat");

  // Records slider
  $("domainRecords").addEventListener("input", e => {
    $("domainCountBadge").textContent = e.target.value;
  });

  $("domainGenerateBtn").addEventListener("click", domainGenerate);
  $("domainDownloadBtn").addEventListener("click", domainDownload);
}

function selectDomain(domain, card) {
  document.querySelectorAll(".domain-card").forEach(c => c.classList.remove("active"));
  card.classList.add("active");
  state.selectedDomain = domain;

  // Show config
  const config = $("domainConfig");
  config.style.display = "block";
  $("domainConfigTitle").textContent = `${DOMAIN_ICONS[domain.name] || ""} ${domain.name.replace(/_/g, " ")} — Configure`;

  // Show tables
  const preview = $("domainTablesPreview");
  preview.innerHTML = "";
  domain.tables.forEach(t => {
    const tag = document.createElement("span");
    tag.className = "domain-table-tag";
    tag.textContent = t;
    preview.appendChild(tag);
  });

  $("domainPreview").style.display = "none";
  $("domainPreview").innerHTML = "";
}

async function domainGenerate() {
  if (!state.selectedDomain) { showToast("Select a domain first.", "error"); return; }
  const btn = $("domainGenerateBtn");
  setLoading(btn, true);
  try {
    const body = {
      domain: state.selectedDomain.name,
      relational: $("domainRelational").checked,
      format: state.domainFormat,
      num_records: parseInt($("domainRecords").value),
    };

    const res = await apiFetch("/generate/domain", { method: "POST", body: JSON.stringify(body) });
    const data = await res.json();

    if (!data.success) throw new Error(data.error || "Generation failed");

    // Build tablesData from response
    const tablesData = {};
    data.tables.forEach(t => {
      try { tablesData[t.table_name] = JSON.parse(t.data); } catch { tablesData[t.table_name] = []; }
    });

    renderMultiPreview("domainPreview", tablesData);
    showToast(`${data.tables.length} tables generated!`, "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

async function domainDownload() {
  if (!state.selectedDomain) { showToast("Select a domain first.", "error"); return; }
  const btn = $("domainDownloadBtn");
  setLoading(btn, true);
  try {
    const body = {
      domain: state.selectedDomain.name,
      relational: $("domainRelational").checked,
      format: state.domainFormat,
      num_records: parseInt($("domainRecords").value),
    };

    const res = await apiFetch("/download/domain", { method: "POST", body: JSON.stringify(body) });
    const blob = await res.blob();
    const filename = res.headers.get("Content-Disposition")?.match(/filename=(.+)/)?.[1]
      || `${state.selectedDomain.name}_data.zip`;
    triggerDownload(blob, filename);
    showToast("Download started!", "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   TAB 3 — Relational Sets
═══════════════════════════════════════════════════════════════════════ */
function initRelationalTab() {
  const grid = $("relationalSetsGrid");
  grid.innerHTML = "";

  state.relSets.forEach(rs => {
    const card = document.createElement("div");
    card.className = "relset-card";
    card.innerHTML = `
      <div class="relset-card-name">${rs.name}</div>
      <div class="relset-card-desc">${rs.description}</div>
    `;
    card.addEventListener("click", () => selectRelSet(rs, card));
    grid.appendChild(card);
  });

  buildFormatGrid("relFormatGrid", "relFormat");

  $("relRecords").addEventListener("input", e => {
    $("relCountBadge").textContent = e.target.value;
  });

  $("relGenerateBtn").addEventListener("click", relGenerate);
  $("relDownloadBtn").addEventListener("click", relDownload);
}

function selectRelSet(rs, card) {
  document.querySelectorAll(".relset-card").forEach(c => c.classList.remove("active"));
  card.classList.add("active");
  state.selectedRelSet = rs;

  const config = $("relationalConfig");
  config.style.display = "block";
  $("relationalConfigTitle").textContent = rs.name;

  // Show relation graph
  const graph = $("relationGraph");
  graph.innerHTML = "";

  // Build a simple left-to-right chain showing unique parent → child links
  const shown = new Set();
  rs.relations.forEach((rel, i) => {
    const key = `${rel.parent}→${rel.child}`;
    if (shown.has(key)) return;
    shown.add(key);

    if (i > 0) {
      const sep = document.createElement("span");
      sep.className = "rel-arrow";
      sep.textContent = "·";
      graph.appendChild(sep);
    }

    const parent = document.createElement("span");
    parent.className = "rel-table";
    parent.textContent = rel.parent;
    graph.appendChild(parent);

    const arrow = document.createElement("span");
    arrow.className = "rel-arrow";
    arrow.textContent = "→";
    graph.appendChild(arrow);

    const child = document.createElement("span");
    child.className = "rel-table";
    child.textContent = rel.child;
    graph.appendChild(child);
  });

  $("relPreview").style.display = "none";
  $("relPreview").innerHTML = "";
}

async function relGenerate() {
  if (!state.selectedRelSet) { showToast("Select a relational set first.", "error"); return; }
  const btn = $("relGenerateBtn");
  setLoading(btn, true);
  try {
    const body = {
      predefined_set: state.selectedRelSet.name,
      format: state.relFormat,
      num_records: parseInt($("relRecords").value),
    };

    const res = await apiFetch("/generate/relational-set", { method: "POST", body: JSON.stringify(body) });
    const data = await res.json();

    if (!data.success) throw new Error(data.error || "Generation failed");

    const tablesData = {};
    data.tables.forEach(t => {
      try { tablesData[t.table_name] = JSON.parse(t.data); } catch { tablesData[t.table_name] = []; }
    });

    renderMultiPreview("relPreview", tablesData);
    showToast(`${data.tables.length} tables generated!`, "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

async function relDownload() {
  if (!state.selectedRelSet) { showToast("Select a relational set first.", "error"); return; }
  const btn = $("relDownloadBtn");
  setLoading(btn, true);
  try {
    const body = {
      predefined_set: state.selectedRelSet.name,
      format: state.relFormat,
      num_records: parseInt($("relRecords").value),
    };

    const res = await apiFetch("/download/relational-set", { method: "POST", body: JSON.stringify(body) });
    const blob = await res.blob();
    const filename = res.headers.get("Content-Disposition")?.match(/filename=(.+)/)?.[1]
      || `${state.selectedRelSet.name}.zip`;
    triggerDownload(blob, filename);
    showToast("Download started!", "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   TAB 4 — Schema Builder
═══════════════════════════════════════════════════════════════════════ */
function initSchemaTab() {
  buildFormatGrid("schemaFormatGrid", "schemaFormat");
  $("addTableBtn").addEventListener("click", showAddTableModal);
  $("addFieldBtn").addEventListener("click", showAddFieldModal);
  $("schemaGenerateBtn").addEventListener("click", schemaGenerate);
  $("schemaDownloadBtn").addEventListener("click", schemaDownload);
  renderSchemaTables();
}

function renderSchemaTables() {
  const list = $("schemaTablesList");
  list.innerHTML = "";

  if (state.schemaTables.length === 0) {
    list.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🧩</div>No tables yet.<br>Click "+ Add Table" to start.</div>`;
    return;
  }

  state.schemaTables.forEach((table, idx) => {
    const item = document.createElement("div");
    item.className = `schema-table-item${state.activeSchemaTable === idx ? " active" : ""}`;
    item.innerHTML = `
      <span>${table.name}</span>
      <div class="schema-table-item-actions">
        <button class="icon-btn" title="Delete table">✕</button>
      </div>
    `;
    item.querySelector(".icon-btn").addEventListener("click", e => {
      e.stopPropagation();
      state.schemaTables.splice(idx, 1);
      if (state.activeSchemaTable === idx) state.activeSchemaTable = null;
      else if (state.activeSchemaTable > idx) state.activeSchemaTable--;
      renderSchemaTables();
      renderSchemaFields();
    });
    item.addEventListener("click", () => {
      state.activeSchemaTable = idx;
      renderSchemaTables();
      renderSchemaFields();
    });
    list.appendChild(item);
  });
}

function renderSchemaFields() {
  const panel = $("schemaFieldsPanel");
  const list = $("schemaFieldsList");
  const addBtn = $("addFieldBtn");
  const title = $("schemaFieldsPanelTitle");

  if (state.activeSchemaTable === null || !state.schemaTables[state.activeSchemaTable]) {
    title.textContent = "Select a table";
    addBtn.style.display = "none";
    list.innerHTML = `<div class="empty-state"><div class="empty-state-icon">👈</div>Select a table to manage its fields.</div>`;
    return;
  }

  const table = state.schemaTables[state.activeSchemaTable];
  title.textContent = table.name;
  addBtn.style.display = "inline-flex";
  list.innerHTML = "";

  if (table.fields.length === 0) {
    list.innerHTML = `<div class="empty-state">No fields yet. Click "+ Add Field".</div>`;
    return;
  }

  table.fields.forEach((field, fidx) => {
    const row = document.createElement("div");
    row.className = "schema-field-row";
    row.innerHTML = `
      <span class="field-row-name">${field.name}</span>
      <span class="field-row-type">${field.type}</span>
      <button class="icon-btn" title="Remove field">✕</button>
    `;
    row.querySelector(".icon-btn").addEventListener("click", () => {
      table.fields.splice(fidx, 1);
      renderSchemaFields();
    });
    list.appendChild(row);
  });

  // Records input for this table
  const recRow = document.createElement("div");
  recRow.style.cssText = "margin-top:10px;display:flex;align-items:center;gap:10px;font-size:12.5px;color:var(--text-muted)";
  recRow.innerHTML = `
    <label style="color:var(--text-muted);font-size:12px">Records:</label>
    <input type="number" class="input" style="width:90px" min="1" max="1000"
      value="${table.num_records || 100}" />
  `;
  recRow.querySelector("input").addEventListener("change", e => {
    table.num_records = Math.min(1000, Math.max(1, parseInt(e.target.value) || 100));
  });
  list.appendChild(recRow);
}

/* ── Add Table Modal ─────────────────────────────────────────────────── */
function showAddTableModal() {
  const overlay = createModal("Add Table", `
    <div style="margin-bottom:14px">
      <label class="input-label">Table Name</label>
      <input type="text" class="input" id="modalTableName" placeholder="e.g. users" />
      <div class="field-meta" style="margin-top:6px">Letters, numbers and underscores only.</div>
    </div>
    <div>
      <label class="input-label">Records</label>
      <input type="number" class="input" id="modalTableRecords" value="100" min="1" max="1000" />
    </div>
  `, () => {
    const name = $("modalTableName").value.trim();
    const records = parseInt($("modalTableRecords").value) || 100;
    if (!name) { showToast("Table name is required.", "error"); return false; }
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name)) { showToast("Invalid table name.", "error"); return false; }
    if (state.schemaTables.find(t => t.name === name)) { showToast("Table already exists.", "error"); return false; }

    state.schemaTables.push({ name, fields: [], num_records: records });
    state.activeSchemaTable = state.schemaTables.length - 1;
    renderSchemaTables();
    renderSchemaFields();
    return true;
  });
  document.body.appendChild(overlay);
  setTimeout(() => overlay.classList.add("show"), 10);
  $("modalTableName").focus();
}

/* ── Add Field Modal ─────────────────────────────────────────────────── */
function showAddFieldModal() {
  if (state.activeSchemaTable === null) return;

  const typeOptions = state.fieldTypes
    .map(ft => `<option value="${ft.type}">${ft.label}</option>`)
    .join("");

  const otherTables = state.schemaTables
    .filter((_, i) => i !== state.activeSchemaTable)
    .map(t => `<option value="${t.name}">${t.name}</option>`)
    .join("");

  const overlay = createModal("Add Field", `
    <div style="display:grid;gap:12px">
      <div>
        <label class="input-label">Field Name</label>
        <input type="text" class="input" id="modalFieldName" placeholder="e.g. user_id" />
      </div>
      <div>
        <label class="input-label">Field Type</label>
        <select class="select" id="modalFieldType">${typeOptions}</select>
      </div>

      <div id="fkConfig" style="display:none;background:var(--surface-2);padding:12px;border-radius:8px;border:1px solid var(--border)">
        <label class="input-label">References Table</label>
        <select class="select" id="modalRefTable" style="margin-bottom:8px">
          <option value="">-- select table --</option>
          ${otherTables}
        </select>
        <label class="input-label">References Field</label>
        <input type="text" class="input" id="modalRefField" placeholder="e.g. id" />
      </div>

      <div id="enumConfig" style="display:none;background:var(--surface-2);padding:12px;border-radius:8px;border:1px solid var(--border)">
        <label class="input-label">Choices (comma-separated)</label>
        <input type="text" class="input" id="modalEnumChoices" placeholder="e.g. active, inactive, pending" />
      </div>
    </div>
  `, () => {
    const name = $("modalFieldName").value.trim();
    const type = $("modalFieldType").value;
    if (!name) { showToast("Field name is required.", "error"); return false; }

    const field = { name, type, constraints: null, references_table: null, references_field: null };

    if (type === "foreign_key") {
      field.references_table = $("modalRefTable").value;
      field.references_field = $("modalRefField").value.trim();
      if (!field.references_table || !field.references_field) {
        showToast("FK requires references_table and references_field.", "error");
        return false;
      }
    }

    if (type === "enum_pick") {
      const choices = $("modalEnumChoices").value.split(",").map(s => s.trim()).filter(Boolean);
      if (!choices.length) { showToast("Provide at least one choice.", "error"); return false; }
      field.constraints = { choices };
    }

    state.schemaTables[state.activeSchemaTable].fields.push(field);
    renderSchemaFields();
    return true;
  });

  // Show/hide FK and enum config based on type selection
  document.body.appendChild(overlay);
  setTimeout(() => overlay.classList.add("show"), 10);

  $("modalFieldType").addEventListener("change", e => {
    $("fkConfig").style.display = e.target.value === "foreign_key" ? "block" : "none";
    $("enumConfig").style.display = e.target.value === "enum_pick" ? "block" : "none";
  });
  $("modalFieldName").focus();
}

function createModal(title, bodyHTML, onConfirm) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal">
      <div class="modal-title">${title}</div>
      <div class="modal-body">${bodyHTML}</div>
      <div class="modal-footer">
        <button class="btn btn-ghost btn-sm" id="modalCancel">Cancel</button>
        <button class="btn btn-primary btn-sm" id="modalConfirm">Confirm</button>
      </div>
    </div>
  `;

  const close = () => {
    overlay.classList.remove("show");
    setTimeout(() => overlay.remove(), 200);
  };

  overlay.querySelector("#modalCancel").addEventListener("click", close);
  overlay.querySelector("#modalConfirm").addEventListener("click", () => {
    if (onConfirm() !== false) close();
  });
  overlay.addEventListener("click", e => { if (e.target === overlay) close(); });

  return overlay;
}

async function schemaGenerate() {
  if (!state.schemaTables.length) { showToast("Add at least one table.", "error"); return; }
  const btn = $("schemaGenerateBtn");
  setLoading(btn, true);
  try {
    const body = {
      tables: state.schemaTables.map(t => ({
        name: t.name,
        fields: t.fields,
        num_records: t.num_records || 100,
      })),
      format: state.schemaFormat,
      seed: parseInt($("schemaSeed").value) || null,
    };

    const res = await apiFetch("/generate/schema", { method: "POST", body: JSON.stringify(body) });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Generation failed");

    const tablesData = {};
    data.tables.forEach(t => {
      try { tablesData[t.table_name] = JSON.parse(t.data); } catch { tablesData[t.table_name] = []; }
    });

    renderMultiPreview("schemaPreview", tablesData);
    showToast(`${data.tables.length} tables generated!`, "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

async function schemaDownload() {
  if (!state.schemaTables.length) { showToast("Add at least one table.", "error"); return; }
  const btn = $("schemaDownloadBtn");
  setLoading(btn, true);
  try {
    const body = {
      tables: state.schemaTables.map(t => ({
        name: t.name,
        fields: t.fields,
        num_records: t.num_records || 100,
      })),
      format: state.schemaFormat,
      seed: parseInt($("schemaSeed").value) || null,
    };

    const res = await apiFetch("/download/schema", { method: "POST", body: JSON.stringify(body) });
    const blob = await res.blob();
    const filename = res.headers.get("Content-Disposition")?.match(/filename=(.+)/)?.[1] || "schema_export.zip";
    triggerDownload(blob, filename);
    showToast("Download started!", "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(btn, false);
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   TAB 5 — DB Seeder
═══════════════════════════════════════════════════════════════════════ */
const DEFAULT_PORTS = {
  postgresql: 5432,
  mysql: 3306,
  sqlite: "",
  mssql: 1433,
};

function initSeederTab() {
  // Populate domain dropdown
  const domSel = $("seedDomain");
  state.domains.forEach(d => {
    const opt = document.createElement("option");
    opt.value = d.name;
    opt.textContent = d.name.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
    domSel.appendChild(opt);
  });

  // Populate relational set dropdown
  const relSel = $("seedRelSet");
  state.relSets.forEach(rs => {
    const opt = document.createElement("option");
    opt.value = rs.name;
    opt.textContent = rs.name;
    relSel.appendChild(opt);
  });

  // Dialect change → auto-fill port
  $("dbDialect").addEventListener("change", e => {
    const port = DEFAULT_PORTS[e.target.value];
    $("dbPort").value = port || "";
  });

  // Seed mode tabs
  document.querySelectorAll(".seed-mode-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".seed-mode-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      state.seedMode = tab.dataset.mode;
      $("seedModeDomain").style.display = state.seedMode === "domain" ? "block" : "none";
      $("seedModeRelset").style.display = state.seedMode === "relset" ? "block" : "none";
    });
  });

  $("dbTestBtn").addEventListener("click", testConnection);
  $("seedBtn").addEventListener("click", seedDatabase);
}

function getConnectionConfig() {
  return {
    dialect: $("dbDialect").value,
    host: $("dbHost").value.trim(),
    port: parseInt($("dbPort").value) || 5432,
    database: $("dbName").value.trim(),
    username: $("dbUser").value.trim(),
    password: $("dbPass").value,
    ssl: $("dbSSL").checked,
  };
}

async function testConnection() {
  const btn = $("dbTestBtn");
  const status = $("dbTestStatus");
  setLoading(btn, true);
  status.textContent = "Testing...";
  status.className = "connection-status";
  try {
    const body = { connection: getConnectionConfig() };
    const res = await apiFetch("/db/test", { method: "POST", body: JSON.stringify(body) });
    const data = await res.json();

    status.textContent = `✓ ${data.message}`;
    status.className = "connection-status ok";
    showToast("Connection successful!", "success");
  } catch (err) {
    status.textContent = `✗ ${err.message.slice(0, 60)}`;
    status.className = "connection-status fail";
    showToast("Connection failed.", "error");
  } finally {
    setLoading(btn, false);
  }
}

async function seedDatabase() {
  const btn = $("seedBtn");
  setLoading(btn, true);
  const result = $("seedResult");
  result.style.display = "none";

  try {
    const connection = getConnectionConfig();
    const num_records = parseInt($("seedRecords").value) || 100;
    const batch_size = parseInt($("seedBatchSize").value) || 500;
    const truncate_first = $("seedTruncate").checked;

    let endpoint, body;

    if (state.seedMode === "domain") {
      endpoint = `/db/seed/domain?domain=${$("seedDomain").value}&num_records=${num_records}&relational=${$("seedRelational").checked}&truncate_first=${truncate_first}&batch_size=${batch_size}`;
      body = JSON.stringify({ connection });
    } else {
      endpoint = `/db/seed/relational-set?predefined_set=${$("seedRelSet").value}&num_records=${num_records}&truncate_first=${truncate_first}&batch_size=${batch_size}`;
      body = JSON.stringify({ connection });
    }

    const res = await apiFetch(endpoint, { method: "POST", body });
    const data = await res.json();

    result.style.display = "block";
    if (data.success) {
      result.className = "seed-result success";
      result.innerHTML = `
        <div class="seed-result-title">✓ Seeding Complete</div>
        <div class="seed-result-rows">
          ${Object.entries(data.rows_inserted).map(([t, n]) =>
        `<div class="seed-result-row"><span>${t}</span><span>${n} rows inserted</span></div>`
      ).join("")}
          ${data.warning ? `<div style="margin-top:10px;font-size:12px;color:var(--amber)">${data.warning}</div>` : ""}
        </div>
      `;
      showToast("Database seeded successfully!", "success");
    } else {
      result.className = "seed-result error";
      result.innerHTML = `<div class="seed-result-title">✗ Seeding Failed</div><div style="font-size:13px;color:var(--text-secondary)">${data.error}</div>`;
    }
  } catch (err) {
    result.style.display = "block";
    result.className = "seed-result error";
    result.innerHTML = `<div class="seed-result-title">✗ Error</div><div style="font-size:13px;color:var(--text-secondary)">${err.message}</div>`;
  } finally {
    setLoading(btn, false);
  }
}

/* ── Download helper ──────────────────────────────────────────────────── */
function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/* ── Kick off ─────────────────────────────────────────────────────────── */
bootstrap();