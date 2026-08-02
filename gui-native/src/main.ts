import { invoke } from "@tauri-apps/api/core";
import { getVersion } from "@tauri-apps/api/app";
import { listen } from "@tauri-apps/api/event";
import { open as openFileDialog } from "@tauri-apps/plugin-dialog";
import { openUrl } from "@tauri-apps/plugin-opener";
import { check, type Update } from "@tauri-apps/plugin-updater";
import { relaunch } from "@tauri-apps/plugin-process";

// ===== Types (khop voi struct Rust ben src-tauri/src/mcp_cli.rs + jobs.rs) =====

interface ProfileItem {
  id: string;
  label: string | null;
  url: string | null;
}

interface ProfilesData {
  active: string | null;
  items: ProfileItem[];
}

interface LicenseStatus {
  profile_id: string;
  label: string;
  url: string;
  is_active: boolean;
  has_credentials: boolean;
  type: string;
  expires_at: number | null;
  expires_in_human: string;
  is_expired: boolean;
  is_warning: boolean;
  last_saved: number | null;
  extra: { session_cookies?: string[]; total_cookies?: number; token_endpoint?: string };
}

interface JobDonePayload {
  code: number;
  label: string;
}

interface McpServerStatus {
  name: string;
  category: string;
  description: string;
  envVars: string[];
  registered: boolean;
  doc: string | null;
}

interface McpStatusData {
  servers: McpServerStatus[];
  claudeAvailable: boolean;
}

interface RuntimeStatus {
  ok: boolean;
  mode: string;
  detail: string;
  install_hint: string;
}

const REPO_URL = "https://github.com/StormShynn/sap-abap-agent";
const RELEASES_URL = `${REPO_URL}/releases`;
const GUI_LATEST_URL = `${REPO_URL}/releases/tag/gui-latest`;

// ===== State =====

let profilesData: ProfilesData = { active: null, items: [] };
let licenseCache: Map<string, LicenseStatus> = new Map();
let selectedId: string | null = null;
let earlyFinishPath: string | null = null;
let licenseDashboardOpen = false;

// ===== DOM refs (gan trong init()) =====
const el = {
  runtimeBanner: byId<HTMLDivElement>("runtime-banner"),
  runtimeBannerTitle: byId<HTMLElement>("runtime-banner-title"),
  runtimeBannerDetail: byId<HTMLParagraphElement>("runtime-banner-detail"),
  runtimeBannerHint: byId<HTMLPreElement>("runtime-banner-hint"),
  btnRuntimeRecheck: byId<HTMLButtonElement>("btn-runtime-recheck"),
  profileSelect: byId<HTMLSelectElement>("profile-select"),
  btnRefresh: byId<HTMLButtonElement>("btn-refresh"),
  btnAdd: byId<HTMLButtonElement>("btn-add"),
  addDropdown: byId<HTMLDivElement>("add-dropdown"),
  urlText: byId<HTMLSpanElement>("url-text"),
  licenseText: byId<HTMLSpanElement>("license-text"),
  btnLicense: byId<HTMLButtonElement>("btn-license"),
  btnReauth: byId<HTMLButtonElement>("btn-reauth"),
  btnConnect: byId<HTMLButtonElement>("btn-connect"),
  btnPing: byId<HTMLButtonElement>("btn-ping"),
  btnSetActive: byId<HTMLButtonElement>("btn-set-active"),
  btnRemove: byId<HTMLButtonElement>("btn-remove"),
  logText: byId<HTMLPreElement>("log-text"),
  logCard: byId<HTMLDivElement>("log-text").parentElement as HTMLDivElement,
  btnClear: byId<HTMLButtonElement>("btn-clear"),
  btnCopy: byId<HTMLButtonElement>("btn-copy"),
  btnDone: byId<HTMLButtonElement>("btn-done"),
  statusText: byId<HTMLSpanElement>("status-text"),
  licenseModal: byId<HTMLDivElement>("license-modal"),
  licenseRows: byId<HTMLDivElement>("license-rows"),
  btnLicenseRefresh: byId<HTMLButtonElement>("btn-license-refresh"),
  btnLicenseClose: byId<HTMLButtonElement>("btn-license-close"),
  btnMcpServers: byId<HTMLButtonElement>("btn-mcp-servers"),
  mcpModal: byId<HTMLDivElement>("mcp-modal"),
  mcpRows: byId<HTMLDivElement>("mcp-rows"),
  btnMcpRefresh: byId<HTMLButtonElement>("btn-mcp-refresh"),
  btnMcpClose: byId<HTMLButtonElement>("btn-mcp-close"),
  btnMcpPresetCore: byId<HTMLButtonElement>("btn-mcp-preset-core"),
  btnMcpPresetResearch: byId<HTMLButtonElement>("btn-mcp-preset-research"),
  btnAbout: byId<HTMLButtonElement>("btn-about"),
  aboutModal: byId<HTMLDivElement>("about-modal"),
  aboutVersion: byId<HTMLSpanElement>("about-version"),
  aboutUpdateActions: byId<HTMLDivElement>("about-update-actions"),
  aboutUpdateMsg: byId<HTMLParagraphElement>("about-update-msg"),
  btnAboutClose: byId<HTMLButtonElement>("btn-about-close"),
  btnAboutRepo: byId<HTMLButtonElement>("btn-about-repo"),
  btnCheckUpdate: byId<HTMLButtonElement>("btn-check-update"),
  promptModal: byId<HTMLDivElement>("prompt-modal"),
  promptTitle: byId<HTMLHeadingElement>("prompt-title"),
  promptMessage: byId<HTMLParagraphElement>("prompt-message"),
  promptInput: byId<HTMLInputElement>("prompt-input"),
  promptCancel: byId<HTMLButtonElement>("prompt-cancel"),
  promptOk: byId<HTMLButtonElement>("prompt-ok"),
  confirmModal: byId<HTMLDivElement>("confirm-modal"),
  confirmTitle: byId<HTMLHeadingElement>("confirm-title"),
  confirmMessage: byId<HTMLParagraphElement>("confirm-message"),
  confirmCancel: byId<HTMLButtonElement>("confirm-cancel"),
  confirmOk: byId<HTMLButtonElement>("confirm-ok"),
};

function byId<T extends HTMLElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) throw new Error(`Missing element #${id}`);
  return found as T;
}

// ===== Small reusable modal helpers (thay the tk.simpledialog / messagebox) =====

function promptText(
  title: string,
  message: string,
  defaultValue = "",
  options: { secret?: boolean } = {},
): Promise<string | null> {
  return new Promise((resolve) => {
    el.promptTitle.textContent = title;
    el.promptMessage.textContent = message;
    el.promptInput.value = defaultValue;
    el.promptInput.type = options.secret ? "password" : "text";
    el.promptModal.classList.remove("hidden");
    el.promptInput.focus();

    const cleanup = () => {
      el.promptModal.classList.add("hidden");
      el.promptInput.type = "text";
      el.promptInput.value = "";
      el.promptOk.onclick = null;
      el.promptCancel.onclick = null;
    };
    el.promptOk.onclick = () => {
      const val = el.promptInput.value;
      cleanup();
      resolve(val);
    };
    el.promptCancel.onclick = () => {
      cleanup();
      resolve(null);
    };
  });
}

function confirmDialog(title: string, message: string): Promise<boolean> {
  return new Promise((resolve) => {
    el.confirmTitle.textContent = title;
    el.confirmMessage.textContent = message;
    el.confirmModal.classList.remove("hidden");

    const cleanup = () => {
      el.confirmModal.classList.add("hidden");
      el.confirmOk.onclick = null;
      el.confirmCancel.onclick = null;
    };
    el.confirmOk.onclick = () => {
      cleanup();
      resolve(true);
    };
    el.confirmCancel.onclick = () => {
      cleanup();
      resolve(false);
    };
  });
}

// ===== Log helpers =====

function appendLog(text: string) {
  el.logText.textContent += text.endsWith("\n") ? text : text + "\n";
  el.logCard.scrollTop = el.logCard.scrollHeight;
}

function clearLog() {
  el.logText.textContent = "";
}

async function copyLog() {
  await navigator.clipboard.writeText(el.logText.textContent ?? "");
}

function setStatus(text: string) {
  el.statusText.textContent = text;
}

/** PATH-only: kiem tra mcp-sap-connect goi duoc truoc khi dung GUI. */
async function checkRuntime(): Promise<boolean> {
  try {
    const st = await invoke<RuntimeStatus>("check_runtime");
    if (st.ok) {
      el.runtimeBanner.classList.add("hidden");
      setStatus(st.detail);
      return true;
    }
    el.runtimeBanner.classList.remove("hidden");
    el.runtimeBannerTitle.textContent =
      st.mode === "path-broken"
        ? "mcp-sap-connect có trên PATH nhưng không chạy được"
        : "Thiếu mcp-sap-connect (PATH-only)";
    el.runtimeBannerDetail.textContent = st.detail;
    el.runtimeBannerHint.textContent = st.install_hint;
    setStatus("Cần cài mcp-sap-connect trước khi dùng GUI");
    return false;
  } catch (err) {
    el.runtimeBanner.classList.remove("hidden");
    el.runtimeBannerTitle.textContent = "Không kiểm tra được runtime";
    el.runtimeBannerDetail.textContent = String(err);
    el.runtimeBannerHint.textContent =
      'pip install "mcp-sap-connect[win-dpapi]"\npython -m mcp_sap_connect.doctor';
    return false;
  }
}

// ===== Profile list + license label (giong _refresh_profiles/_update_license_label) =====

function formatBadge(st: LicenseStatus | undefined): string {
  if (!st) return "";
  if (!st.has_credentials) return "🔓";
  if (st.is_expired) return "❌";
  if (st.is_warning) return `⚠ ${st.expires_in_human}`;
  return `✓ ${st.expires_in_human}`;
}

async function fetchLicenseCache(): Promise<void> {
  try {
    const statuses = await invoke<LicenseStatus[]>("get_license_statuses");
    licenseCache = new Map(statuses.map((s) => [s.profile_id, s]));
  } catch (err) {
    // Khong co profile nao / loi doc - giu cache cu, khong lam vo UI.
    console.warn("get_license_statuses failed", err);
  }
}

async function refreshProfiles(): Promise<void> {
  try {
    profilesData = await invoke<ProfilesData>("list_profiles");
  } catch (err) {
    setStatus(`Lỗi đọc profile: ${err}`);
    return;
  }
  await fetchLicenseCache();

  el.profileSelect.innerHTML = "";
  for (const p of profilesData.items) {
    const opt = document.createElement("option");
    opt.value = p.id;
    const marker = p.id === profilesData.active ? "* " : "  ";
    const badge = formatBadge(licenseCache.get(p.id));
    opt.textContent = `${marker}${p.id}  ${badge}`.trimEnd();
    el.profileSelect.appendChild(opt);
  }

  if (profilesData.active && profilesData.items.some((p) => p.id === profilesData.active)) {
    el.profileSelect.value = profilesData.active;
  } else if (profilesData.items.length > 0) {
    el.profileSelect.value = profilesData.items[0].id;
  }
  onProfileChanged();
}

function selectedProfile(): ProfileItem | null {
  return profilesData.items.find((p) => p.id === selectedId) ?? null;
}

function onProfileChanged() {
  selectedId = el.profileSelect.value || null;
  const p = selectedProfile();
  if (p) {
    el.urlText.textContent = p.url || "(no URL)";
  } else {
    el.urlText.textContent =
      profilesData.items.length === 0
        ? "(chưa có profile nào - bấm '+ Add' để setup)"
        : "(no URL)";
  }
  updateLicenseLabel();
  setButtonsEnabled(!currentJobLabel);
}

function updateLicenseLabel() {
  if (!selectedId) {
    el.licenseText.textContent = "";
    return;
  }
  const st = licenseCache.get(selectedId);
  if (!st) {
    el.licenseText.textContent = "";
    return;
  }
  el.licenseText.classList.remove("ok-color", "warn-color", "danger-color");
  if (!st.has_credentials) {
    el.licenseText.textContent = "🔓 No credentials saved";
    el.licenseText.style.color = "var(--muted)";
  } else if (st.is_expired) {
    el.licenseText.textContent = `❌ Expired (${st.expires_in_human}) - run Reauth`;
    el.licenseText.style.color = "var(--danger)";
  } else if (st.is_warning) {
    el.licenseText.textContent = `⚠ Expiring soon: ${st.expires_in_human} remaining`;
    el.licenseText.style.color = "var(--warn)";
  } else {
    el.licenseText.textContent = `✓ OK: ${st.expires_in_human} remaining`;
    el.licenseText.style.color = "var(--ok)";
  }
}

// Countdown tick moi giay (tuong duong _tick_countdown) - chi tinh lai text tu
// expires_at da co san trong cache, KHONG goi lai invoke moi giay (do se qua
// nhieu subprocess). Cache duoc lam moi that su moi khi refreshProfiles()/
// license dashboard refresh() chay.
function tickCountdownDisplay() {
  if (!selectedId) return;
  const st = licenseCache.get(selectedId);
  if (!st || st.expires_at == null) return;
  const remaining = st.expires_at - Date.now() / 1000;
  st.expires_in_human = humanizeDuration(remaining);
  st.is_expired = remaining < 0;
  st.is_warning = !st.is_expired && remaining < 3600;
  updateLicenseLabel();
}

function humanizeDuration(seconds: number): string {
  if (seconds < 0) {
    const ago = -seconds;
    if (ago < 60) return `expired ${Math.floor(ago)}s ago`;
    if (ago < 3600) return `expired ${Math.floor(ago / 60)}m ${Math.floor(ago % 60)}s ago`;
    if (ago < 86400) return `expired ${(ago / 3600).toFixed(1)}h ago`;
    return `expired ${(ago / 86400).toFixed(1)}d ago`;
  }
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
  if (seconds < 86400) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return m ? `${h}h ${m}m` : `${h}h`;
  }
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  return h ? `${d}d ${h}h` : `${d}d`;
}

// ===== Job / buttons state =====

let currentJobLabel: string | null = null;

function setButtonsEnabled(enabled: boolean) {
  const hasProfile = !!selectedId;
  for (const btn of [el.btnReauth, el.btnConnect, el.btnPing, el.btnSetActive, el.btnRemove]) {
    btn.disabled = !(enabled && hasProfile);
  }
}

// ===== Action handlers =====

async function onReauth() {
  if (!selectedId || currentJobLabel) return;
  const pid = selectedId;

  earlyFinishPath = await invoke<string>("make_early_finish_path");
  el.btnDone.disabled = false;

  appendLog(`$ mcp-sap-connect reauth ${pid}`);
  currentJobLabel = `reauth ${pid}`;
  setButtonsEnabled(false);
  setStatus("Đang đăng nhập lại...");

  try {
    await invoke("start_streamed", {
      args: ["reauth", pid],
      envExtra: { SAP_BTP_EARLY_FINISH_FILE: earlyFinishPath },
      label: currentJobLabel,
    });
  } catch (err) {
    appendLog(`[ERROR] ${err}`);
    resetJobState();
  }
}

async function onConnect() {
  if (!selectedId || currentJobLabel) return;
  const pid = selectedId;
  appendLog(`$ mcp-sap-connect connect ${pid}`);
  currentJobLabel = `connect ${pid}`;
  setButtonsEnabled(false);
  setStatus("Đang test kết nối...");
  try {
    await invoke("start_streamed", { args: ["connect", pid], envExtra: null, label: currentJobLabel });
  } catch (err) {
    appendLog(`[ERROR] ${err}`);
    resetJobState();
  }
}

async function onPing() {
  if (!selectedId || currentJobLabel) return;
  const pid = selectedId;
  appendLog(`$ mcp-sap-connect ping ${pid}`);
  currentJobLabel = `ping ${pid}`;
  setButtonsEnabled(false);
  setStatus("Đang ping...");
  try {
    await invoke("start_streamed", { args: ["ping", pid], envExtra: null, label: currentJobLabel });
  } catch (err) {
    appendLog(`[ERROR] ${err}`);
    resetJobState();
  }
}

async function onSetActive() {
  if (!selectedId) return;
  try {
    await invoke("set_active_profile", { profileId: selectedId });
  } catch (err) {
    alert(`Lỗi: ${err}`);
    return;
  }
  appendLog(`[OK] Đã set '${selectedId}' làm profile active.`);
  setStatus(`Active: ${selectedId}`);
  await refreshProfiles();
}

async function onRemove() {
  if (!selectedId) return;
  const pid = selectedId;
  const yes = await confirmDialog(
    "Xóa profile?",
    `Bạn có chắc muốn xóa profile '${pid}'?\n(sẽ xóa config.json + secrets.json của profile này)`,
  );
  if (!yes) return;
  try {
    await invoke("remove_profile", { profileId: pid });
  } catch (err) {
    alert(`Lỗi: ${err}`);
    return;
  }
  appendLog(`[OK] Đã xóa profile '${pid}'.`);
  await refreshProfiles();
}

function resetJobState() {
  currentJobLabel = null;
  el.btnDone.disabled = true;
  if (earlyFinishPath) {
    invoke("cleanup_early_finish", { path: earlyFinishPath }).catch(() => {});
    earlyFinishPath = null;
  }
  setButtonsEnabled(true);
}

async function onDoneClicked() {
  if (!earlyFinishPath) return;
  await invoke("touch_early_finish", { path: earlyFinishPath });
  appendLog("[gui] ✓ Đã bấm nút OK - yêu cầu subprocess kết thúc sớm...");
  el.btnDone.disabled = true;
}

// ===== Add menu =====

async function onNewSetup() {
  if (currentJobLabel) return;
  const url = await promptText(
    "Setup new profile",
    "Nhập URL SAP (bỏ trống để wizard tự hỏi):\nVD: https://project1.s4hana.cloud.sap",
  );
  if (url === null) return; // user cancelled
  const args = url.trim() ? ["setup", url.trim()] : ["setup"];
  appendLog(`$ mcp-sap-connect ${args.join(" ")}  (mở cửa sổ CMD mới)`);
  currentJobLabel = "setup";
  setStatus("Setup đang chạy (cửa sổ CMD riêng)...");
  try {
    await invoke("start_new_console", { args, label: currentJobLabel });
  } catch (err) {
    appendLog(`[ERROR] ${err}`);
    currentJobLabel = null;
  }
}

async function onSetupFromFile() {
  if (currentJobLabel) return;
  const path = await openFileDialog({
    title: "Chọn file profile đã điền (vd profile.cookie.json)",
    filters: [{ name: "JSON", extensions: ["json"] }],
  });
  if (!path || Array.isArray(path)) return;

  // start_streamed (khong phai start_new_console): lenh nay non-interactive va
  // thoat gan nhu ngay lap tuc (thanh cong hoac bi reject) - cua so CMD rieng
  // se dong qua nhanh de doc duoc gi ca. Stream vao log chinh (ben lai duoc)
  // + van ho tro nut "Da xong" cho nhanh browser-fallback qua marker file.
  earlyFinishPath = await invoke<string>("make_early_finish_path");
  el.btnDone.disabled = false;

  appendLog(`$ mcp-sap-connect setup --from-file "${path}"`);
  currentJobLabel = "setup --from-file";
  setButtonsEnabled(false);
  setStatus("Setup từ file đang chạy...");
  try {
    await invoke("start_streamed", {
      args: ["setup", "--from-file", path],
      envExtra: { SAP_BTP_EARLY_FINISH_FILE: earlyFinishPath },
      label: currentJobLabel,
    });
  } catch (err) {
    appendLog(`[ERROR] ${err}`);
    resetJobState();
  }
}

async function onImportJson() {
  const path = await openFileDialog({
    title: "Chọn file config.json để import",
    filters: [{ name: "JSON", extensions: ["json"] }],
  });
  if (!path || Array.isArray(path)) return;
  try {
    const result = await invoke<{ profileId: string; url: string }>("import_json_backup", { path });
    alert(
      `Đã đăng ký profile: ${result.profileId}\nURL: ${result.url}\n\n` +
        "Tiếp theo hãy copy secrets.json vào thư mục profile này trên máy mới (không tự import được vì đã mã hóa DPAPI).",
    );
    appendLog(`[OK] Đã import profile: ${result.profileId}`);
    await refreshProfiles();
  } catch (err) {
    alert(`Import failed: ${err}`);
  }
}

// ===== License dashboard =====

function pctForRow(st: LicenseStatus): number {
  if (st.expires_at == null) return 0;
  const maxAge = st.last_saved ? st.expires_at - st.last_saved : 8 * 3600;
  const remaining = Math.max(0, st.expires_at - Date.now() / 1000);
  return Math.min(100, Math.max(0, (remaining / Math.max(1, maxAge)) * 100));
}

function renderLicenseDashboard(statuses: LicenseStatus[]) {
  el.licenseRows.innerHTML = "";
  if (statuses.length === 0) {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "(chưa có profile nào - chạy: mcp-sap-connect setup <url>)";
    el.licenseRows.appendChild(p);
    return;
  }
  for (const s of statuses) {
    const card = document.createElement("div");
    card.className = "license-row-card";
    card.dataset.pid = s.profile_id;

    const header = document.createElement("div");
    header.className = "license-row-header";
    header.textContent = `${s.is_active ? "★ " : "  "}${s.profile_id}  (${s.type})`;
    card.appendChild(header);

    const wrap = document.createElement("div");
    wrap.className = "progress-wrap";
    const track = document.createElement("div");
    track.className = "progress-track";
    const fill = document.createElement("div");
    fill.className = "progress-fill";
    track.appendChild(fill);
    const countdown = document.createElement("div");
    countdown.className = "countdown-text";
    wrap.appendChild(track);
    wrap.appendChild(countdown);
    card.appendChild(wrap);

    const detail = document.createElement("div");
    detail.className = "license-row-detail";
    const savedTxt = s.last_saved ? new Date(s.last_saved * 1000).toLocaleString() : "(never)";
    const extraTxt =
      s.type === "cookie"
        ? `${s.extra?.session_cookies?.length ?? 0} session / ${s.extra?.total_cookies ?? 0} total`
        : s.type === "oauth2"
          ? (s.extra?.token_endpoint ?? "?").slice(0, 50)
          : "";
    detail.textContent = `Saved: ${savedTxt}    ${extraTxt}`;
    card.appendChild(detail);

    el.licenseRows.appendChild(card);
  }
  tickLicenseDashboard(statuses);
}

function tickLicenseDashboard(statuses: LicenseStatus[]) {
  for (const s of statuses) {
    const card = el.licenseRows.querySelector(`[data-pid="${CSS.escape(s.profile_id)}"]`);
    if (!card) continue;
    const fill = card.querySelector<HTMLDivElement>(".progress-fill")!;
    const countdown = card.querySelector<HTMLDivElement>(".countdown-text")!;
    if (s.expires_at == null) {
      fill.style.width = "0%";
      countdown.textContent = "unknown";
      countdown.style.color = "var(--muted)";
      continue;
    }
    const remaining = s.expires_at - Date.now() / 1000;
    const pct = pctForRow(s);
    fill.style.width = `${pct}%`;
    fill.classList.remove("warn", "danger");
    if (pct < 5) fill.classList.add("danger");
    else if (pct < 20) fill.classList.add("warn");
    countdown.textContent = humanizeDuration(remaining);
    countdown.style.color = pct < 5 ? "var(--danger)" : pct < 20 ? "var(--warn)" : "var(--ok)";
  }
}

let dashboardStatuses: LicenseStatus[] = [];

async function openLicenseDashboard() {
  el.licenseModal.classList.remove("hidden");
  licenseDashboardOpen = true;
  await refreshLicenseDashboard();
}

async function refreshLicenseDashboard() {
  try {
    dashboardStatuses = await invoke<LicenseStatus[]>("get_license_statuses");
  } catch (err) {
    dashboardStatuses = [];
    console.warn("license dashboard refresh failed", err);
  }
  renderLicenseDashboard(dashboardStatuses);
}

function closeLicenseDashboard() {
  el.licenseModal.classList.add("hidden");
  licenseDashboardOpen = false;
}

// ===== MCP Servers Setup panel =====
// Khac voi mcp-switch (bat/tat MCP da cai) - panel nay goi mcp-setup --status-json/
// --register-json de THIET LAP (chay `claude mcp add`) server con thieu, khong
// phai toggle server da co san.

const MCP_CATEGORY_LABELS: Record<string, string> = {
  core: "Core (bắt buộc)",
  remote: "Remote (bắt buộc)",
  "adt-alternative": "ADT Alternative (chọn 1 trong các lựa chọn thay thế)",
  special: "Đặc biệt",
  manual: "Cần cài đặt thủ công (xem doc)",
};
const MCP_CATEGORY_ORDER = ["core", "remote", "adt-alternative", "special", "manual"];

async function openMcpModal() {
  el.mcpModal.classList.remove("hidden");
  await refreshMcpStatus();
}

function closeMcpModal() {
  el.mcpModal.classList.add("hidden");
}

async function refreshMcpStatus() {
  el.mcpRows.innerHTML = `<p class="muted">Đang tải...</p>`;
  try {
    const data = await invoke<McpStatusData>("mcp_status");
    renderMcpRows(data);
  } catch (err) {
    el.mcpRows.innerHTML = `<p class="muted">Lỗi đọc trạng thái MCP: ${err}</p>`;
  }
}

function renderMcpRows(data: McpStatusData) {
  el.mcpRows.innerHTML = "";
  if (!data.claudeAvailable) {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "⚠ Không tìm thấy 'claude' trong PATH - cài Claude Code trước khi đăng ký server.";
    el.mcpRows.appendChild(p);
  }

  const byCategory = new Map<string, McpServerStatus[]>();
  for (const s of data.servers) {
    if (!byCategory.has(s.category)) byCategory.set(s.category, []);
    byCategory.get(s.category)!.push(s);
  }

  for (const cat of MCP_CATEGORY_ORDER) {
    const servers = byCategory.get(cat);
    if (!servers || servers.length === 0) continue;

    const header = document.createElement("div");
    header.className = "mcp-category-header";
    header.textContent = MCP_CATEGORY_LABELS[cat] ?? cat;
    el.mcpRows.appendChild(header);

    for (const s of servers) {
      el.mcpRows.appendChild(renderMcpRow(s));
    }
  }
}

function renderMcpRow(s: McpServerStatus): HTMLElement {
  const row = document.createElement("div");
  row.className = "mcp-row";

  const main = document.createElement("div");
  main.className = "mcp-row-main";

  const name = document.createElement("span");
  name.className = "mcp-row-name";
  name.textContent = s.name;
  main.appendChild(name);

  const badge = document.createElement("span");
  badge.className = `mcp-row-badge ${s.registered ? "ok" : "off"}`;
  badge.textContent = s.registered ? "✓ Đã đăng ký" : "○ Chưa đăng ký";
  main.appendChild(badge);

  const spacer = document.createElement("span");
  spacer.className = "mcp-row-spacer";
  main.appendChild(spacer);

  if (s.category === "manual") {
    const doc = document.createElement("span");
    doc.className = "muted";
    doc.style.fontSize = "0.8em";
    doc.textContent = s.doc ?? "";
    main.appendChild(doc);
  } else if (!s.registered) {
    const btn = document.createElement("button");
    btn.className = "btn btn-flat btn-sm";
    btn.textContent = "Đăng ký";
    btn.addEventListener("click", () => void onRegisterMcpServer(s));
    main.appendChild(btn);
  } else {
    const btn = document.createElement("button");
    btn.className = "btn btn-flat btn-sm";
    btn.textContent = "Hủy đăng ký";
    btn.addEventListener("click", () => void onUnregisterMcpServer(s));
    main.appendChild(btn);
  }

  row.appendChild(main);

  const desc = document.createElement("div");
  desc.className = "mcp-row-desc";
  desc.textContent = s.description;
  row.appendChild(desc);

  return row;
}

async function onRegisterMcpServer(s: McpServerStatus) {
  const env: Record<string, string> = {};
  for (const varName of s.envVars) {
    const secret = /key|token|secret|password|passwd/i.test(varName);
    const val = await promptText(
      `${s.name}: ${varName}`,
      `Nhập giá trị cho biến môi trường '${varName}':`,
      "",
      { secret },
    );
    if (val === null) return; // user huy giua chung - khong dang ky
    env[varName] = val;
  }

  appendLog(`$ mcp-sap-connect mcp-setup --register-json ${s.name}`);
  try {
    await invoke("mcp_register", { name: s.name, env });
    appendLog(`[OK] Đã đăng ký MCP server '${s.name}'. Khởi động lại Claude Code để nhận server mới.`);
  } catch (err) {
    appendLog(`[ERROR] Đăng ký '${s.name}' thất bại: ${err}`);
  }
  await refreshMcpStatus();
}

async function onUnregisterMcpServer(s: McpServerStatus) {
  const ok = await confirmDialog(
    "Hủy đăng ký MCP",
    `Gỡ '${s.name}' khỏi Claude Code (claude mcp remove)?`,
  );
  if (!ok) return;
  appendLog(`$ mcp-sap-connect mcp-setup --unregister-json ${s.name}`);
  try {
    await invoke("mcp_unregister", { name: s.name });
    appendLog(`[OK] Đã hủy đăng ký '${s.name}'. Khởi động lại Claude Code nếu đang mở.`);
  } catch (err) {
    appendLog(`[ERROR] Hủy đăng ký '${s.name}' thất bại: ${err}`);
  }
  await refreshMcpStatus();
}

const MCP_PRESET_CORE = ["sap-btp", "sap-dict-bridge", "cds-kb", "mcp-sap-docs-btp"];
const MCP_PRESET_RESEARCH = [...MCP_PRESET_CORE, "arc-1", "sap-vsp"];

async function onMcpPreset(names: string[], label: string) {
  appendLog(`[MCP] Áp dụng preset ${label}...`);
  let data: McpStatusData;
  try {
    data = await invoke<McpStatusData>("mcp_status");
  } catch (err) {
    appendLog(`[ERROR] Không đọc được MCP status: ${err}`);
    return;
  }
  if (!data.claudeAvailable) {
    appendLog("[ERROR] Không tìm thấy 'claude' trong PATH.");
    return;
  }
  const byName = new Map(data.servers.map((s) => [s.name, s]));
  for (const name of names) {
    const s = byName.get(name);
    if (!s) {
      appendLog(`[WARN] Preset bỏ qua '${name}' (không có trong inventory).`);
      continue;
    }
    if (s.registered) {
      appendLog(`[OK] '${name}' đã đăng ký — bỏ qua.`);
      continue;
    }
    if (s.category === "manual") {
      appendLog(`[WARN] '${name}' cần cài thủ công — bỏ qua.`);
      continue;
    }
    await onRegisterMcpServer(s);
  }
  appendLog(`[MCP] Preset ${label} xong.`);
}

// ===== About / Auto-updater (tauri-plugin-updater + gui-latest/update.json) =====

let cachedAppVersion = "";
let pendingUpdate: Update | null = null;

async function openAboutModal() {
  el.aboutModal.classList.remove("hidden");
  if (!cachedAppVersion) {
    try {
      cachedAppVersion = await getVersion();
    } catch {
      cachedAppVersion = "unknown";
    }
  }
  el.aboutVersion.textContent = cachedAppVersion;
}

function closeAboutModal() {
  el.aboutModal.classList.add("hidden");
}

function setUpdateMsg(text: string, isError = false) {
  el.aboutUpdateMsg.textContent = text;
  el.aboutUpdateMsg.classList.toggle("about-update-error", isError);
}

function resetUpdateActions() {
  pendingUpdate = null;
  el.aboutUpdateActions.innerHTML = "";
  el.aboutUpdateActions.appendChild(el.btnCheckUpdate);
  el.btnCheckUpdate.disabled = false;
  el.btnCheckUpdate.textContent = "Check for updates";
  el.btnCheckUpdate.onclick = () => void onCheckUpdate();
}

function showRetryActions(extraBrowse = false) {
  el.aboutUpdateActions.innerHTML = "";
  const again = document.createElement("button");
  again.className = "btn btn-flat btn-sm";
  again.textContent = "Check again";
  again.addEventListener("click", () => void onCheckUpdate());
  el.aboutUpdateActions.appendChild(again);
  if (extraBrowse) {
    const browse = document.createElement("button");
    browse.className = "btn btn-flat btn-sm";
    browse.textContent = "Browse releases";
    browse.addEventListener("click", () => {
      void openUrl(RELEASES_URL);
    });
    el.aboutUpdateActions.appendChild(browse);
  }
}

async function onInstallUpdate() {
  if (!pendingUpdate) return;
  setUpdateMsg("Downloading update…");
  el.aboutUpdateActions.innerHTML = "";
  const progress = document.createElement("span");
  progress.className = "muted";
  progress.textContent = "0%";
  el.aboutUpdateActions.appendChild(progress);

  try {
    let downloaded = 0;
    let total = 0;
    await pendingUpdate.downloadAndInstall((event) => {
      if (event.event === "Started") {
        total = event.data.contentLength ?? 0;
        setUpdateMsg("Downloading update…");
      } else if (event.event === "Progress") {
        downloaded += event.data.chunkLength;
        const pct =
          total > 0 ? Math.min(100, Math.round((downloaded / total) * 100)) : 0;
        progress.textContent = `${pct}%`;
      } else if (event.event === "Finished") {
        setUpdateMsg("Installing… app will restart.");
        progress.textContent = "Installing…";
      }
    });
    await relaunch();
  } catch (err) {
    setUpdateMsg(String(err), true);
    showRetryActions(true);
  }
}

async function onCheckUpdate() {
  setUpdateMsg("Checking…");
  el.aboutUpdateActions.innerHTML = "";
  const checking = document.createElement("span");
  checking.className = "muted";
  checking.textContent = "Checking…";
  el.aboutUpdateActions.appendChild(checking);
  pendingUpdate = null;

  try {
    const update = await check();
    if (!update) {
      setUpdateMsg("You are on the latest version.");
      showRetryActions(false);
      return;
    }
    pendingUpdate = update;
    setUpdateMsg(
      `Update available: v${update.version}${update.body ? ` — ${update.body}` : ""}`,
    );
    el.aboutUpdateActions.innerHTML = "";
    const installBtn = document.createElement("button");
    installBtn.className = "btn btn-accent btn-sm";
    installBtn.textContent = `Download & install v${update.version}`;
    installBtn.addEventListener("click", () => void onInstallUpdate());
    el.aboutUpdateActions.appendChild(installBtn);
    const again = document.createElement("button");
    again.className = "btn btn-flat btn-sm";
    again.textContent = "Check again";
    again.addEventListener("click", () => void onCheckUpdate());
    el.aboutUpdateActions.appendChild(again);
    const browse = document.createElement("button");
    browse.className = "btn btn-flat btn-sm";
    browse.textContent = "Release notes";
    browse.addEventListener("click", () => {
      void openUrl(GUI_LATEST_URL);
    });
    el.aboutUpdateActions.appendChild(browse);
  } catch (err) {
    const msg = String(err);
    const hint =
      msg.includes("404") || msg.toLowerCase().includes("not found")
        ? " (chua co release gui-latest/update.json — can CI secrets + tag gui-v*)"
        : "";
    setUpdateMsg(`${msg}${hint}`, true);
    showRetryActions(true);
  }
}

// ===== Wiring =====

function initEventListeners() {
  el.profileSelect.addEventListener("change", onProfileChanged);
  el.btnRefresh.addEventListener("click", () => void refreshProfiles());

  el.btnAdd.addEventListener("click", (e) => {
    e.stopPropagation();
    el.addDropdown.classList.toggle("hidden");
  });
  document.addEventListener("click", () => el.addDropdown.classList.add("hidden"));
  el.addDropdown.querySelectorAll<HTMLButtonElement>("button[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      el.addDropdown.classList.add("hidden");
      const action = btn.dataset.action;
      if (action === "wizard") void onNewSetup();
      else if (action === "from-file") void onSetupFromFile();
      else if (action === "import-json") void onImportJson();
    });
  });

  el.btnReauth.addEventListener("click", () => void onReauth());
  el.btnConnect.addEventListener("click", () => void onConnect());
  el.btnPing.addEventListener("click", () => void onPing());
  el.btnSetActive.addEventListener("click", () => void onSetActive());
  el.btnRemove.addEventListener("click", () => void onRemove());

  el.btnClear.addEventListener("click", clearLog);
  el.btnCopy.addEventListener("click", () => void copyLog());
  el.btnDone.addEventListener("click", () => void onDoneClicked());

  el.btnLicense.addEventListener("click", () => void openLicenseDashboard());
  el.licenseText.addEventListener("click", () => void openLicenseDashboard());
  el.btnLicenseRefresh.addEventListener("click", () => void refreshLicenseDashboard());
  el.btnLicenseClose.addEventListener("click", closeLicenseDashboard);

  el.btnMcpServers.addEventListener("click", () => void openMcpModal());
  el.btnMcpRefresh.addEventListener("click", () => void refreshMcpStatus());
  el.btnMcpClose.addEventListener("click", closeMcpModal);
  el.btnMcpPresetCore.addEventListener("click", () => void onMcpPreset(MCP_PRESET_CORE, "Core"));
  el.btnMcpPresetResearch.addEventListener("click", () =>
    void onMcpPreset(MCP_PRESET_RESEARCH, "Research"),
  );

  el.btnAbout.addEventListener("click", () => void openAboutModal());
  el.btnAboutClose.addEventListener("click", closeAboutModal);
  el.btnAboutRepo.addEventListener("click", () => void openUrl(REPO_URL));
  el.btnCheckUpdate.onclick = () => void onCheckUpdate();
  el.btnRuntimeRecheck.addEventListener("click", () => void checkRuntime().then((ok) => {
    if (ok) void refreshProfiles();
  }));

  // Tauri events tu Rust backend
  void listen<string>("job-line", (event) => appendLog(event.payload));
  void listen<JobDonePayload>("job-done", (event) => {
    const { code, label } = event.payload;
    appendLog(`\n[exit ${label} rc=${code}]\n`);
    setStatus(`${label}: rc=${code}`);
    resetJobState();
    void refreshProfiles();
  });
  void listen("open-license-dashboard", () => void openLicenseDashboard());
  void listen("open-about", () => void openAboutModal());

  // Countdown tick moi giay: header label + dashboard (neu dang mo)
  setInterval(() => {
    tickCountdownDisplay();
    if (licenseDashboardOpen && dashboardStatuses.length) {
      tickLicenseDashboard(dashboardStatuses);
    }
  }, 1000);
}

window.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  resetUpdateActions();
  void checkRuntime().then((ok) => {
    if (ok) void refreshProfiles();
  });
  // Quiet background check — surface only when an update exists (About for install).
  void check().then((update) => {
    if (!update) return;
    appendLog(`[Update] Có bản mới ${update.version} — mở About để tải & cài.`);
    setStatus(`Có bản GUI mới: ${update.version}`);
  }).catch(() => {
    /* ignore 404 / offline until gui-latest exists */
  });
});
