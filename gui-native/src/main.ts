import { invoke } from "@tauri-apps/api/core";
import { getVersion } from "@tauri-apps/api/app";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { open as openFileDialog } from "@tauri-apps/plugin-dialog";
import { openUrl } from "@tauri-apps/plugin-opener";
import { check, type Update } from "@tauri-apps/plugin-updater";
import { relaunch } from "@tauri-apps/plugin-process";
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from "@tauri-apps/plugin-notification";

// Shoelace (Web Components) — themes + components dùng trong GUI này
import "@shoelace-style/shoelace/dist/themes/light.css";
import "@shoelace-style/shoelace/dist/themes/dark.css";
import "@shoelace-style/shoelace/dist/components/alert/alert.js";
import "@shoelace-style/shoelace/dist/components/badge/badge.js";
import "@shoelace-style/shoelace/dist/components/progress-bar/progress-bar.js";
import { registerIconLibrary } from "@shoelace-style/shoelace/dist/utilities/icon-library.js";

// Shoelace mặc định tải icon từ CDN — bị CSP chặn trong Tauri. Đăng ký thư
// viện icon local (inline SVG data URI) để chạy offline, không cần network.
const SL_ICONS: Record<string, string> = {
  "x-lg":
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/></svg>',
  "check2-circle":
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0z"/></svg>',
  "exclamation-triangle":
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.15.15 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.2.2 0 0 1-.054.06.1.1 0 0 1-.066.017H1.146a.1.1 0 0 1-.066-.017.2.2 0 0 1-.054-.06.18.18 0 0 1 .002-.183L7.884 2.073a.15.15 0 0 1 .054-.057m1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767z"/><path d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/></svg>',
  "exclamation-octagon":
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M4.54.146A.5.5 0 0 1 4.893 0h6.214a.5.5 0 0 1 .353.146l4.394 4.394a.5.5 0 0 1 .146.353v6.214a.5.5 0 0 1-.146.353l-4.394 4.394a.5.5 0 0 1-.353.146H4.893a.5.5 0 0 1-.353-.146L.146 11.46A.5.5 0 0 1 0 11.107V4.893a.5.5 0 0 1 .146-.353zM5.1 1 1 5.1v5.8L5.1 15h5.8l4.1-4.1V5.1L10.9 1z"/><path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/></svg>',
  "info-circle":
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/><path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/></svg>',
};

registerIconLibrary("default", {
  resolver: (name: string) => {
    const svg = SL_ICONS[name] ?? SL_ICONS["info-circle"];
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  },
  mutator: (svg: SVGElement) => svg,
});

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
  docUrl?: string | null;
  installHint?: string | null;
  canRegister?: boolean;
}

interface McpStatusData {
  servers: McpServerStatus[];
  claudeAvailable: boolean;
  coreServers?: string[];
}

interface RuntimeStatus {
  ok: boolean;
  mode: string;
  detail: string;
  install_hint: string;
}

interface DoctorReport {
  all_ok: boolean;
  path_ok: boolean;
  scripts_dir: string | null;
  path_fix: string | null;
}

interface PluginStatusData {
  claudeAvailable: boolean;
  found: boolean;
  pluginId: string | null;
  version: string | null;
  lastUpdated: string | null;
  detail: string | null;
}

const REPO_URL = "https://github.com/StormShynn/sap-abap-agent";
const RELEASES_URL = `${REPO_URL}/releases`;
const GUI_LATEST_URL = `${REPO_URL}/releases/tag/gui-latest`;

// ===== Theme (dark/light) =====
// Sync <html> class `sl-theme-dark` (Shoelace) + `data-theme` (our CSS vars).

const THEME_KEY = "sap-abap-agent.gui.theme";

function systemPrefersDark(): boolean {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
}

function loadTheme(): "dark" | "light" {
  try {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === "dark" || saved === "light") return saved;
  } catch {
    /* private mode */
  }
  return systemPrefersDark() ? "dark" : "light";
}

function applyTheme(theme: "dark" | "light") {
  document.documentElement.classList.toggle("sl-theme-dark", theme === "dark");
  document.documentElement.dataset.theme = theme;
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* private mode */
  }
  if (el.btnTheme) {
    el.btnTheme.textContent = theme === "dark" ? "☀️" : "🌙";
  }
}

function toggleTheme() {
  applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
}

// ===== Window controls (decorations: false — custom titlebar) =====
// getCurrentWindow() o module level se crash khi chay ngoai Tauri (browser
// dev / preview thuần). Lazy-init + try/catch de app van hoat dong.

let appWindow: ReturnType<typeof getCurrentWindow> | null = null;

function getAppWindow() {
  if (!appWindow) {
    try {
      appWindow = getCurrentWindow();
    } catch {
      appWindow = null;
    }
  }
  return appWindow;
}

async function refreshMaximizeIcon() {
  const win = getAppWindow();
  if (!win) return;
  let maximized = false;
  try {
    maximized = await win.isMaximized();
  } catch {
    /* dev / non-window context */
  }
  el.winMaxIcon.classList.toggle("hidden", maximized);
  el.winRestoreIcon.classList.toggle("hidden", !maximized);
}

function initWindowControls() {
  const win = getAppWindow();
  if (!win) {
    // Chay ngoai Tauri: an luon cac nut dieu khien cua so.
    el.winMin.classList.add("hidden");
    el.winMax.classList.add("hidden");
    el.winClose.classList.add("hidden");
    return;
  }
  el.winMin.addEventListener("click", () => void win.minimize());
  el.winMax.addEventListener("click", () => {
    void win.toggleMaximize().then(refreshMaximizeIcon);
  });
  el.winClose.addEventListener("click", () => void win.close());
  // Windows convention: double-click titlebar to toggle maximize.
  el.titlebar.addEventListener("dblclick", (e) => {
    if ((e.target as HTMLElement).closest("button")) return;
    void win.toggleMaximize().then(refreshMaximizeIcon);
  });
  void refreshMaximizeIcon();
  void win.onResized(() => void refreshMaximizeIcon());
}

// ===== Toast helper (Shoelace) — thay the alert() =====

type ToastVariant = "success" | "danger" | "warning" | "primary" | "neutral";

function showToast(message: string, variant: ToastVariant = "primary", duration = 4500) {
  const alert = Object.assign(document.createElement("sl-alert"), {
    variant,
    duration,
    closable: true,
  });
  alert.textContent = message;
  document.body.appendChild(alert);
  alert.toast();
}

// ===== Windows notifications (tauri-plugin-notification) =====
// Rust side da init plugin (lib.rs); capability `notification:default` da co.
// Chay ngoai Tauri (browser dev/preview): isPermissionGranted() se reject →
// notify() im lang, khong crash.

let notifyPermission: boolean | null = null;

// ===== Notifications on/off setting (localStorage) =====
// User co the tat thong bao Windows cho job/update. Khi tat, notify() im lang
// (khong request permission, khong hien gi). Setting duoc sync sang Rust qua
// invoke "set_notifications_enabled" de tray menu cung ton trong setting.

const NOTIFY_DISABLED_KEY = "sap-abap-agent.gui.notifyDisabled";

function loadNotifyDisabled(): boolean {
  try {
    return localStorage.getItem(NOTIFY_DISABLED_KEY) === "1";
  } catch {
    return false;
  }
}

function setNotifyDisabled(disabled: boolean) {
  try {
    if (disabled) localStorage.setItem(NOTIFY_DISABLED_KEY, "1");
    else localStorage.removeItem(NOTIFY_DISABLED_KEY);
  } catch {
    /* private mode */
  }
  el.btnNotifyToggle.classList.toggle("active", !disabled);
  el.btnNotifyToggle.setAttribute("aria-pressed", String(!disabled));
  el.btnNotifyToggle.textContent = disabled ? "🔕 Off" : "🔔 On";
  // Sync sang Rust (gate notify() trong tray.rs) — khong fail neu chay ngoai Tauri.
  invoke("set_notifications_enabled", { enabled: !disabled }).catch(() => {});
}

function toggleNotifyDisabled() {
  setNotifyDisabled(!loadNotifyDisabled());
}

async function ensureNotifyPermission(): Promise<boolean> {
  if (notifyPermission !== null) return notifyPermission;
  try {
    let granted = await isPermissionGranted();
    if (!granted) {
      const permission = await requestPermission();
      granted = permission === "granted";
    }
    notifyPermission = granted;
  } catch {
    notifyPermission = false; // non-Tauri context
  }
  return notifyPermission;
}

async function notify(title: string, body: string) {
  if (loadNotifyDisabled()) return; // user tat thong bao
  if (!(await ensureNotifyPermission())) return;
  try {
    sendNotification({ title, body });
  } catch (err) {
    console.warn("sendNotification failed", err);
  }
}

// ===== Clear-on-job-start toggle =====

const CLEAR_ON_JOB_KEY = "sap-abap-agent.gui.clearOnJobStart";

function loadClearOnJobStart(): boolean {
  try {
    return localStorage.getItem(CLEAR_ON_JOB_KEY) === "1";
  } catch {
    return false;
  }
}

function setClearOnJobStart(enabled: boolean) {
  try {
    if (enabled) localStorage.setItem(CLEAR_ON_JOB_KEY, "1");
    else localStorage.removeItem(CLEAR_ON_JOB_KEY);
  } catch {
    /* private mode */
  }
  el.btnClearOnJob.classList.toggle("active", enabled);
  el.btnClearOnJob.setAttribute("aria-pressed", String(enabled));
}

function toggleClearOnJobStart() {
  setClearOnJobStart(!loadClearOnJobStart());
}

/** Goi truoc khi bat dau job moi: neu toggle ON thi xoa log cu. */
function maybeClearLogForNewJob() {
  if (loadClearOnJobStart()) clearLog();
}

// ===== State =====

let profilesData: ProfilesData = { active: null, items: [] };
let licenseCache: Map<string, LicenseStatus> = new Map();
let selectedId: string | null = null;
let earlyFinishPath: string | null = null;
let licenseDashboardOpen = false;
/** Cached PowerShell/shell PATH fix from last doctor --json (null when PATH OK). */
let cachedPathFix: string | null = null;

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
  btnDoctor: byId<HTMLButtonElement>("btn-doctor"),
  btnReauth: byId<HTMLButtonElement>("btn-reauth"),
  btnConnect: byId<HTMLButtonElement>("btn-connect"),
  btnPing: byId<HTMLButtonElement>("btn-ping"),
  btnSetActive: byId<HTMLButtonElement>("btn-set-active"),
  btnRemove: byId<HTMLButtonElement>("btn-remove"),
  logText: byId<HTMLPreElement>("log-text"),
  logCard: byId<HTMLDivElement>("log-text").parentElement as HTMLDivElement,
  btnClear: byId<HTMLButtonElement>("btn-clear"),
  btnCopy: byId<HTMLButtonElement>("btn-copy"),
  btnOpenLogDir: byId<HTMLButtonElement>("btn-open-log-dir"),
  btnCopyPathFix: byId<HTMLButtonElement>("btn-copy-path-fix"),
  btnClearOnJob: byId<HTMLButtonElement>("btn-clear-on-job"),
  btnDone: byId<HTMLButtonElement>("btn-done"),
  statusText: byId<HTMLSpanElement>("status-text"),
  licenseModal: byId<HTMLDivElement>("license-modal"),
  licenseRows: byId<HTMLDivElement>("license-rows"),
  btnLicenseRefresh: byId<HTMLButtonElement>("btn-license-refresh"),
  btnLicenseClose: byId<HTMLButtonElement>("btn-license-close"),
  btnMcpServers: byId<HTMLButtonElement>("btn-mcp-servers"),
  mcpModal: byId<HTMLDivElement>("mcp-modal"),
  mcpRows: byId<HTMLDivElement>("mcp-rows"),
  mcpCoreCta: byId<HTMLDivElement>("mcp-core-cta"),
  mcpCoreCtaDetail: byId<HTMLSpanElement>("mcp-core-cta-detail"),
  mcpNotionCta: byId<HTMLDivElement>("mcp-notion-cta"),
  btnMcpRegisterRequired: byId<HTMLButtonElement>("btn-mcp-register-required"),
  btnMcpSkipRequired: byId<HTMLButtonElement>("btn-mcp-skip-required"),
  btnMcpRefresh: byId<HTMLButtonElement>("btn-mcp-refresh"),
  btnMcpClose: byId<HTMLButtonElement>("btn-mcp-close"),
  btnMcpPresetCore: byId<HTMLButtonElement>("btn-mcp-preset-core"),
  btnMcpPresetResearch: byId<HTMLButtonElement>("btn-mcp-preset-research"),
  btnPluginControl: byId<HTMLButtonElement>("btn-plugin-control"),
  pluginModal: byId<HTMLDivElement>("plugin-modal"),
  pluginInstalledText: byId<HTMLSpanElement>("plugin-installed-text"),
  pluginLastUpdatedText: byId<HTMLSpanElement>("plugin-last-updated-text"),
  btnPluginUpdate: byId<HTMLButtonElement>("btn-plugin-update"),
  pluginUpdateMsg: byId<HTMLParagraphElement>("plugin-update-msg"),
  btnPluginClose: byId<HTMLButtonElement>("btn-plugin-close"),
  btnAbout: byId<HTMLButtonElement>("btn-about"),
  btnNotifyToggle: byId<HTMLButtonElement>("btn-notify-toggle"),
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
  titlebar: byId<HTMLDivElement>("titlebar"),
  btnTheme: byId<HTMLButtonElement>("btn-theme"),
  winMin: byId<HTMLButtonElement>("win-min"),
  winMax: byId<HTMLButtonElement>("win-max"),
  winClose: byId<HTMLButtonElement>("win-close"),
  winMaxIcon: byId<SVGElement>("win-max-icon"),
  winRestoreIcon: byId<SVGElement>("win-restore-icon"),
};

function byId<T extends Element>(id: string): T {
  const found = document.getElementById(id);
  if (!found) throw new Error(`Missing element #${id}`);
  // getElementById tra ve HTMLElement — cast qua unknown vi T co the la SVGElement.
  return found as unknown as T;
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

// ===== Log helpers (raw text + timestamped/colorized render) =====
// rawLog la nguon that (de Copy / Clear — khong kem timestamp). logLines luu
// tung dong + timestamp tai thoi diem append (renderLog chay lai toan bo moi
// lan nen timestamp phai tinh luc append, khong phai luc render). logText hien
// thi HTML co mau theo muc: lenh `$` (cmd), [OK], [ERROR], [WARN], [exit ...]
// (dim), moi dong co prefix [HH:MM:SS] muted.

interface LogLine {
  ts: string;
  text: string;
}

let rawLog = "";
let logLines: LogLine[] = [];

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => {
    switch (c) {
      case "&": return "&amp;";
      case "<": return "&lt;";
      case ">": return "&gt;";
      case '"': return "&quot;";
      default: return "&#39;";
    }
  });
}

function logLineClass(line: string): string {
  if (/\[ERROR\]|\[err\]/i.test(line)) return "log-err";
  if (/\[WARN\]/i.test(line)) return "log-warn";
  if (/\[OK\]/i.test(line)) return "log-ok";
  if (/^\[exit /.test(line.trim())) return "log-dim";
  if (line.trimStart().startsWith("$")) return "log-cmd";
  return "";
}

function nowTimestamp(): string {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

// Follow mode: chi auto-scroll xuong day khi user DANG o day (cach day < 40px).
// Neu user da cuon len doc log cu, giu nguyen vi tri doc khi log them dong moi.
function renderLog() {
  const scrolledAway =
    el.logCard.scrollHeight - el.logCard.scrollTop - el.logCard.clientHeight > 40;
  el.logText.innerHTML = logLines
    .map(({ ts, text }) => {
      if (!text) return ""; // dong rong: giu nguyen, khong prefix timestamp
      const cls = logLineClass(text);
      const safe = escapeHtml(text);
      const body = cls ? `<span class="${cls}">${safe}</span>` : safe;
      return `<span class="log-ts">[${ts}]</span> ${body}`;
    })
    .join("\n");
  if (!scrolledAway) {
    el.logCard.scrollTop = el.logCard.scrollHeight;
  }
}

function appendLog(text: string) {
  const ts = nowTimestamp();
  rawLog += text.endsWith("\n") ? text : text + "\n";
  // Giu ca dong rong (log format) — moi dong 1 timestamp rieng tai luc append.
  const chunks = text.split("\n");
  if (text.endsWith("\n")) chunks.pop();
  for (const chunk of chunks) {
    logLines.push({ ts, text: chunk });
  }
  renderLog();
}

function clearLog() {
  rawLog = "";
  logLines = [];
  renderLog();
}

async function copyLog() {
  await navigator.clipboard.writeText(rawLog);
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
      '$WHL = python -c \'import json,urllib.request as u; r=json.load(u.urlopen("https://api.github.com/repos/StormShynn/sap-abap-agent/releases")); rel=next(x for x in r if x["tag_name"].startswith("mcp-server-v")); print(next(a["browser_download_url"] for a in rel["assets"] if a["name"].endswith(".whl")))\'\n' +
      'pip install "mcp_sap_connect[win-dpapi] @ $WHL"\n' +
      'python -m mcp_sap_connect.doctor';
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
  el.btnDoctor.disabled = !enabled;
  updateCopyPathFixButton(enabled);
}

function updateCopyPathFixButton(jobIdle = !currentJobLabel) {
  el.btnCopyPathFix.disabled = !(jobIdle && !!cachedPathFix);
}

// ===== Action handlers =====

async function onReauth() {
  if (!selectedId || currentJobLabel) return;
  const pid = selectedId;

  earlyFinishPath = await invoke<string>("make_early_finish_path");
  el.btnDone.disabled = false;

  maybeClearLogForNewJob();
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
  maybeClearLogForNewJob();
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
  maybeClearLogForNewJob();
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
  const previous = profilesData.active;
  try {
    await invoke("set_active_profile", { profileId: selectedId });
  } catch (err) {
    showToast(`Lỗi: ${err}`, "danger");
    return;
  }
  appendLog(`[OK] Đã set '${selectedId}' làm profile active.`);
  if (previous && previous !== selectedId) {
    appendLog(
      "[WARN] sap-vsp (nếu đã đăng ký) không tự nhận profile mới — " +
        "chạy lại mcp-setup / MCP Servers để rebind SAP_ADT_*.",
    );
  }
  setStatus(`Active: ${selectedId}`);
  await refreshProfiles();
}

async function onDoctor() {
  if (currentJobLabel) return;
  maybeClearLogForNewJob();
  appendLog("$ mcp-sap-connect doctor");
  currentJobLabel = "doctor";
  setButtonsEnabled(false);
  setStatus("Đang chạy doctor...");
  try {
    await invoke("start_streamed", { args: ["doctor"], envExtra: null, label: currentJobLabel });
  } catch (err) {
    appendLog(`[ERROR] ${err}`);
    resetJobState();
  }
}

async function refreshDoctorPathFix(opts: { announce?: boolean } = {}) {
  try {
    const report = await invoke<DoctorReport>("doctor_json");
    cachedPathFix = report.path_ok ? null : report.path_fix ?? null;
    updateCopyPathFixButton();
    if (!opts.announce) return;
    if (report.path_ok) {
      appendLog("[Doctor] PATH OK — không cần Copy PATH fix.");
    } else if (cachedPathFix) {
      appendLog(
        "[Doctor] PATH thiếu Scripts — bấm «Copy PATH fix» rồi dán vào PowerShell, mở lại terminal/app.",
      );
      if (report.scripts_dir) {
        appendLog(`[Doctor] Scripts dir: ${report.scripts_dir}`);
      }
    } else {
      appendLog("[Doctor] Không tìm thấy mcp-sap-connect — chạy pip install trước (xem runtime banner).");
    }
  } catch (err) {
    cachedPathFix = null;
    updateCopyPathFixButton();
    if (opts.announce) {
      appendLog(`[WARN] Không đọc được doctor --json: ${err}`);
    }
  }
}

/** Mo thu muc log (~/.mcp-sap-connect/log) trong Explorer. */
async function onOpenLogDir() {
  try {
    const path = await invoke<string>("open_log_dir");
    appendLog(`[OK] Đã mở thư mục log: ${path}`);
    setStatus("Đã mở thư mục log");
  } catch (err) {
    appendLog(`[ERROR] Không mở được thư mục log: ${err}`);
    showToast(`Không mở được thư mục log: ${err}`, "danger");
  }
}

async function onCopyPathFix() {
  let fix = cachedPathFix;
  if (!fix) {
    await refreshDoctorPathFix();
    fix = cachedPathFix;
  }
  if (!fix) {
    appendLog("[WARN] Không có PATH fix để copy (PATH đã OK hoặc chưa cài mcp-sap-connect).");
    setStatus("Không có PATH fix");
    return;
  }
  try {
    await navigator.clipboard.writeText(fix);
    appendLog("[OK] Đã copy lệnh PATH fix vào clipboard. Dán vào PowerShell (User PATH), rồi mở terminal/app mới.");
    setStatus("Đã copy PATH fix");
  } catch (err) {
    await promptText("PATH fix", "Copy lệnh bên dưới:", fix);
    appendLog(`[WARN] Clipboard lỗi (${err}) — đã hiện hộp thoại để copy tay.`);
  }
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
    showToast(`Lỗi: ${err}`, "danger");
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
  maybeClearLogForNewJob();
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

  maybeClearLogForNewJob();
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
    showToast(
      `Đã đăng ký profile: ${result.profileId} (${result.url}). ` +
        "Copy secrets.json vào thư mục profile này trên máy mới (không tự import được vì đã mã hóa DPAPI).",
      "success",
      7000,
    );
    appendLog(`[OK] Đã import profile: ${result.profileId}`);
    await refreshProfiles();
  } catch (err) {
    showToast(`Import failed: ${err}`, "danger");
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
    const star = document.createElement("span");
    star.textContent = s.is_active ? "★" : "";
    const pidText = document.createElement("span");
    pidText.textContent = s.profile_id;
    const typeBadge = document.createElement("sl-badge");
    typeBadge.variant = s.type === "oauth2" ? "warning" : "primary";
    typeBadge.pill = true;
    typeBadge.textContent = s.type;
    header.append(star, pidText, typeBadge);
    card.appendChild(header);

    const wrap = document.createElement("div");
    wrap.className = "progress-wrap";
    const bar = document.createElement("sl-progress-bar");
    bar.value = 0;
    const countdown = document.createElement("div");
    countdown.className = "countdown-text";
    wrap.appendChild(bar);
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
    const bar = card.querySelector<HTMLElementTagNameMap["sl-progress-bar"]>("sl-progress-bar")!;
    const countdown = card.querySelector<HTMLDivElement>(".countdown-text")!;
    if (s.expires_at == null) {
      bar.value = 0;
      countdown.textContent = "unknown";
      countdown.style.color = "var(--muted)";
      continue;
    }
    const remaining = s.expires_at - Date.now() / 1000;
    const pct = pctForRow(s);
    bar.value = pct;
    bar.classList.remove("warn", "danger");
    if (pct < 5) bar.classList.add("danger");
    else if (pct < 20) bar.classList.add("warn");
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
  remote: "Remote (bắt buộc — CDS/Docs)",
  "adt-alternative": "ADT Alternative (chọn 1 nếu cần)",
  special: "Tùy chọn / Research",
  manual: "Cần cài đặt thủ công",
};
const MCP_CATEGORY_ORDER = ["core", "remote", "adt-alternative", "special", "manual"];

/** Core = bắt buộc theo rollout + MCP_PRESET_CORE. */
const MCP_PRESET_CORE = ["sap-connect", "sap-dict-bridge", "cds-kb", "mcp-sap-docs-btp"];
const MCP_PRESET_RESEARCH = [...MCP_PRESET_CORE, "arc-1", "sap-vsp"];
const MCP_CORE_SKIP_KEY = "sap-abap-agent.mcpCoreSkip";
const MCP_CORE_OFFERED_KEY = "sap-abap-agent.mcpCoreOffered";

function isMcpCoreSkip(): boolean {
  try {
    return localStorage.getItem(MCP_CORE_SKIP_KEY) === "1";
  } catch {
    return false;
  }
}

function setMcpCoreSkip(skip: boolean) {
  try {
    if (skip) localStorage.setItem(MCP_CORE_SKIP_KEY, "1");
    else localStorage.removeItem(MCP_CORE_SKIP_KEY);
  } catch {
    /* private mode */
  }
}

function missingCoreServers(data: McpStatusData): McpServerStatus[] {
  const coreNames = data.coreServers?.length ? data.coreServers : MCP_PRESET_CORE;
  const byName = new Map(data.servers.map((s) => [s.name, s]));
  return coreNames
    .map((n) => byName.get(n))
    .filter((s): s is McpServerStatus => !!s && !s.registered);
}

function updateMcpCoreCta(data: McpStatusData) {
  const missing = missingCoreServers(data);
  const show = data.claudeAvailable && missing.length > 0 && !isMcpCoreSkip();
  el.mcpCoreCta.classList.toggle("hidden", !show);
  if (show) {
    el.mcpCoreCtaDetail.textContent =
      `Chưa có: ${missing.map((s) => s.name).join(", ")}. Bấm để đăng ký một lần.`;
  }
}

function updateMcpNotionCta(data: McpStatusData) {
  const notion = data.servers.find((s) => s.name === "notion");
  const show = !!notion?.registered;
  el.mcpNotionCta.classList.toggle("hidden", !show);
}

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
    updateMcpCoreCta(data);
    updateMcpNotionCta(data);
  } catch (err) {
    el.mcpCoreCta.classList.add("hidden");
    el.mcpNotionCta.classList.add("hidden");
    el.mcpRows.innerHTML = `<p class="muted">Lỗi đọc trạng thái MCP: ${err}</p>`;
  }
}

function renderMcpRows(data: McpStatusData) {
  el.mcpRows.innerHTML = "";
  if (!data.claudeAvailable) {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "⚠ Không tìm thấy 'claude' trong PATH — cài Claude Code trước khi đăng ký server.";
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

function appendMcpActionBtn(
  parent: HTMLElement,
  label: string,
  onClick: () => void,
  accent = false,
) {
  const btn = document.createElement("button");
  btn.className = accent ? "btn btn-accent btn-sm" : "btn btn-flat btn-sm";
  btn.textContent = label;
  btn.addEventListener("click", onClick);
  parent.appendChild(btn);
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

  const badge = document.createElement("sl-badge");
  badge.variant = s.registered ? "success" : "neutral";
  badge.pill = true;
  badge.textContent = s.registered ? "✓ Đã đăng ký" : "○ Chưa đăng ký";
  main.appendChild(badge);

  const spacer = document.createElement("span");
  spacer.className = "mcp-row-spacer";
  main.appendChild(spacer);

  // Non-manual: luon dang ky duoc. Manual: chi khi CLI tra canRegister (vd. sap-gui/uvx).
  const canRegister = s.category === "manual" ? !!s.canRegister : s.canRegister !== false;

  if (s.category === "manual") {
    if (canRegister && !s.registered) {
      appendMcpActionBtn(main, "Đăng ký", () => void onRegisterMcpServer(s), true);
    } else if (s.registered) {
      appendMcpActionBtn(main, "Hủy đăng ký", () => void onUnregisterMcpServer(s));
    }
    if (s.docUrl) {
      appendMcpActionBtn(main, "Mở hướng dẫn", () => void openUrl(s.docUrl!));
    }
    if (s.installHint) {
      appendMcpActionBtn(main, "Copy lệnh cài", () => void onCopyMcpInstallHint(s));
    }
    if (!s.docUrl && !s.installHint && !canRegister) {
      const fallback = document.createElement("span");
      fallback.className = "muted";
      fallback.style.fontSize = "0.8em";
      fallback.textContent = s.doc ?? "Chưa có hướng dẫn trong inventory";
      main.appendChild(fallback);
    }
  } else if (!s.registered) {
    appendMcpActionBtn(main, "Đăng ký", () => void onRegisterMcpServer(s));
  } else {
    appendMcpActionBtn(main, "Hủy đăng ký", () => void onUnregisterMcpServer(s));
  }

  row.appendChild(main);

  const desc = document.createElement("div");
  desc.className = "mcp-row-desc";
  desc.textContent = s.description;
  row.appendChild(desc);

  if (s.name === "notion" && s.registered) {
    const note = document.createElement("div");
    note.className = "mcp-row-oauth-note";
    note.textContent =
      "Sau đăng ký: mở Claude Code và chạy /mcp để hoàn tất OAuth Notion (remote HTTP).";
    row.appendChild(note);
  }

  return row;
}

async function onCopyMcpInstallHint(s: McpServerStatus) {
  const hint = s.installHint?.trim();
  if (!hint) return;
  try {
    await navigator.clipboard.writeText(hint);
    appendLog(`[OK] Đã copy lệnh cài '${s.name}' vào clipboard.`);
    setStatus(`Đã copy lệnh cài ${s.name}`);
  } catch (err) {
    // Fallback: hien prompt de user copy tay (khong dead-end)
    await promptText(`Lệnh cài ${s.name}`, "Copy lệnh bên dưới:", hint);
    appendLog(`[WARN] Clipboard lỗi (${err}) — đã hiện hộp thoại để copy tay.`);
  }
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
    if (s.name === "notion") {
      appendLog(
        "[MCP] Notion remote MCP cần OAuth: mở Claude Code và chạy /mcp để hoàn tất đăng nhập Notion.",
      );
    }
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
    if (s.category === "manual" && !s.canRegister) {
      appendLog(`[WARN] '${name}' cần cài thủ công — dùng «Mở hướng dẫn» / «Copy lệnh cài».`);
      continue;
    }
    await onRegisterMcpServer(s);
  }
  appendLog(`[MCP] Preset ${label} xong.`);
  if (label === "Core" || label === "bắt buộc") {
    setMcpCoreSkip(false);
  }
  await refreshMcpStatus();
}

async function onRegisterRequiredCore() {
  setMcpCoreSkip(false);
  await onMcpPreset(MCP_PRESET_CORE, "bắt buộc");
}

function onSkipRequiredCore() {
  setMcpCoreSkip(true);
  el.mcpCoreCta.classList.add("hidden");
  appendLog("[MCP] Đã tạm bỏ qua nhắc Core. Mở lại MCP Servers hoặc bấm «Cài Core» khi sẵn sàng.");
  setStatus("Đã để sau — cài Core khi cần");
}

/** Lan dau runtime OK: hoi 1 lan (confirm) neu Core thieu — khong dang ky am tham. */
async function maybeOfferCoreOnStartup() {
  if (isMcpCoreSkip()) return;
  try {
    if (localStorage.getItem(MCP_CORE_OFFERED_KEY) === "1") return;
  } catch {
    /* continue */
  }
  let data: McpStatusData;
  try {
    data = await invoke<McpStatusData>("mcp_status");
  } catch {
    return;
  }
  if (!data.claudeAvailable) return;
  const missing = missingCoreServers(data);
  if (missing.length === 0) return;
  try {
    localStorage.setItem(MCP_CORE_OFFERED_KEY, "1");
  } catch {
    /* private mode */
  }
  const ok = await confirmDialog(
    "Cài MCP bắt buộc?",
    `Thiếu: ${missing.map((s) => s.name).join(", ")}.\n\n`
      + "Đăng ký Core (sap-connect, sap-dict-bridge, cds-kb, mcp-sap-docs-btp) ngay? "
      + "Bạn có thể chọn «Hủy» rồi cài sau trong MCP Servers.",
  );
  if (ok) {
    await onRegisterRequiredCore();
  } else {
    setMcpCoreSkip(true);
    appendLog("[MCP] Bạn đã bỏ qua cài Core lúc khởi động. Mở «MCP Servers» khi cần.");
  }
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

// ===== Plugin Control (claude plugin update) =====
//
// Rieng biet voi About/Auto-updater o tren: About cap nhat CHINH APP GUI nay
// (tauri-plugin-updater, tag gui-latest). Muc nay cap nhat plugin Claude Code
// (skills/agents/hooks) qua goi thang binary `claude` (plugin_cli.rs) - restart
// Claude Code (KHONG PHAI app nay) moi ap dung, GUI khong tu lam duoc.

function formatAgo(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "không rõ";
  const seconds = (Date.now() - then) / 1000;
  if (seconds < 60) return "vừa xong";
  if (seconds < 3600) return `${Math.floor(seconds / 60)} phút trước`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} giờ trước`;
  return `${Math.floor(seconds / 86400)} ngày trước`;
}

async function openPluginModal() {
  el.pluginModal.classList.remove("hidden");
  await refreshPluginStatus();
}

function closePluginModal() {
  el.pluginModal.classList.add("hidden");
}

function setPluginMsg(text: string, isError = false) {
  el.pluginUpdateMsg.textContent = text;
  el.pluginUpdateMsg.classList.toggle("about-update-error", isError);
}

async function refreshPluginStatus() {
  el.pluginInstalledText.textContent = "…";
  el.pluginLastUpdatedText.textContent = "…";
  el.btnPluginUpdate.disabled = true;
  setPluginMsg("");
  try {
    const st = await invoke<PluginStatusData>("plugin_status");
    if (!st.claudeAvailable) {
      el.pluginInstalledText.textContent = "(không rõ)";
      el.pluginLastUpdatedText.textContent = "(không rõ)";
      setPluginMsg("⚠ Không tìm thấy 'claude' trong PATH — cài Claude Code trước.", true);
      return;
    }
    if (!st.found) {
      el.pluginInstalledText.textContent = "(chưa cài)";
      el.pluginLastUpdatedText.textContent = "(chưa cài)";
      setPluginMsg(st.detail ?? "Chưa tìm thấy plugin đã cài.", true);
      return;
    }
    el.pluginInstalledText.textContent = `${st.pluginId} (v${st.version})`;
    el.pluginLastUpdatedText.textContent = st.lastUpdated ? formatAgo(st.lastUpdated) : "không rõ";
    el.btnPluginUpdate.disabled = false;
  } catch (err) {
    el.pluginInstalledText.textContent = "(lỗi)";
    el.pluginLastUpdatedText.textContent = "(lỗi)";
    setPluginMsg(String(err), true);
  }
}

async function onPluginUpdateClick() {
  el.btnPluginUpdate.disabled = true;
  setPluginMsg("Đang cập nhật… (có thể mất đến ~2 phút)");
  maybeClearLogForNewJob();
  appendLog("$ claude plugin marketplace update ... && claude plugin update ...");
  try {
    const msg = await invoke<string>("plugin_update");
    setPluginMsg(msg);
    appendLog(`[OK] Plugin update:\n${msg}`);
    setStatus("Plugin: đã cập nhật");
  } catch (err) {
    setPluginMsg(String(err), true);
    appendLog(`[ERROR] Plugin update: ${err}`);
    setStatus("Plugin: cập nhật lỗi");
  }
  await refreshPluginStatus();
}

// ===== Wiring =====

function initEventListeners() {
  initWindowControls();
  el.btnTheme.addEventListener("click", toggleTheme);

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
  el.btnDoctor.addEventListener("click", () => void onDoctor());

  el.btnClear.addEventListener("click", clearLog);
  el.btnCopy.addEventListener("click", () => void copyLog());
  el.btnOpenLogDir.addEventListener("click", () => void onOpenLogDir());
  el.btnCopyPathFix.addEventListener("click", () => void onCopyPathFix());
  el.btnClearOnJob.addEventListener("click", toggleClearOnJobStart);
  el.btnDone.addEventListener("click", () => void onDoneClicked());

  el.btnLicense.addEventListener("click", () => void openLicenseDashboard());
  el.licenseText.addEventListener("click", () => void openLicenseDashboard());
  el.btnLicenseRefresh.addEventListener("click", () => void refreshLicenseDashboard());
  el.btnLicenseClose.addEventListener("click", closeLicenseDashboard);

  el.btnMcpServers.addEventListener("click", () => void openMcpModal());
  el.btnMcpRefresh.addEventListener("click", () => void refreshMcpStatus());
  el.btnMcpClose.addEventListener("click", closeMcpModal);
  el.btnMcpRegisterRequired.addEventListener("click", () => void onRegisterRequiredCore());
  el.btnMcpSkipRequired.addEventListener("click", onSkipRequiredCore);
  el.btnMcpPresetCore.addEventListener("click", () => {
    setMcpCoreSkip(false);
    void onMcpPreset(MCP_PRESET_CORE, "Core");
  });
  el.btnMcpPresetResearch.addEventListener("click", () =>
    void onMcpPreset(MCP_PRESET_RESEARCH, "Research"),
  );

  el.btnPluginControl.addEventListener("click", () => void openPluginModal());
  el.btnPluginClose.addEventListener("click", closePluginModal);
  el.btnPluginUpdate.addEventListener("click", () => void onPluginUpdateClick());

  el.btnAbout.addEventListener("click", () => void openAboutModal());
  el.btnAboutClose.addEventListener("click", closeAboutModal);
  el.btnNotifyToggle.addEventListener("click", toggleNotifyDisabled);
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
    if (label === "doctor" || label.startsWith("doctor")) {
      void refreshDoctorPathFix({ announce: true });
    }
    if (code === 0) {
      void notify(`✓ ${label} hoàn tất`, "Thao tác chạy thành công (rc=0).");
    } else {
      void notify(`❌ ${label} thất bại (rc=${code})`, "Xem log trong cửa sổ SAP ABAP Agent để biết chi tiết.");
    }
  });
  void listen("open-license-dashboard", () => void openLicenseDashboard());
  void listen("open-about", () => void openAboutModal());
  void listen("open-plugin-panel", () => void openPluginModal());
  // Tray menu: "Check for updates..." — mo About va chay check ngay lap tuc.
  // Khi co ban moi, notify Windows cho nhat quan voi quiet background check.
  void listen("tray-check-update", () => {
    openAboutModal();
    void onCheckUpdate().then(() => {
      if (pendingUpdate) {
        void notify(
          `Có bản cập nhật mới v${pendingUpdate.version}`,
          "Mở About (ℹ) để tải & cài.",
        );
      }
    });
  });

  // Countdown tick moi giay: header label + dashboard (neu dang mo)
  setInterval(() => {
    tickCountdownDisplay();
    if (licenseDashboardOpen && dashboardStatuses.length) {
      tickLicenseDashboard(dashboardStatuses);
    }
  }, 1000);
}

window.addEventListener("DOMContentLoaded", () => {
  applyTheme(loadTheme());
  setClearOnJobStart(loadClearOnJobStart());
  setNotifyDisabled(loadNotifyDisabled());
  initEventListeners();
  resetUpdateActions();
  void checkRuntime().then((ok) => {
    if (!ok) return;
    void refreshProfiles().then(() => void maybeOfferCoreOnStartup());
  });
  // Quiet background check — surface only when an update exists (About for install).
  void check().then((update) => {
    if (!update) return;
    appendLog(`[Update] Có bản mới ${update.version} — mở About để tải & cài.`);
    setStatus(`Có bản GUI mới: ${update.version}`);
    void notify(`Có bản cập nhật mới v${update.version}`, "Mở About (ℹ) trong SAP ABAP Agent để tải & cài.");
  }).catch(() => {
    /* ignore 404 / offline until gui-latest exists */
  });
});
