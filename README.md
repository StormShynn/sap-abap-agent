# SAP ABAP Agent (tieng Viet)

[![Version](https://img.shields.io/badge/version-0.6.2-blue.svg)](CHANGELOG.md) [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org) [![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md) [![Security Policy](https://img.shields.io/badge/Security-View_Policy-blue.svg)](SECURITY.md) [![Changelog](https://img.shields.io/badge/Changelog-%23ff69b4.svg)](CHANGELOG.md)

Plugin Claude Code + MCP server tu dong ket noi **SAP BTP / S/4HANA Cloud** de thao tac
ABAP (doc / tim / syntax-check / activate). Ho tro **multi-profile** -- moi project SAP
co profile rieng (URL, tenant, secret), luu trong **folder user** tren may
(`%USERPROFILE%\.sap-btp-agent\` Windows, `~/.sap-btp-agent/` macOS/Linux).

## Noi bat

- **🧠 SAP Consultant System (19 modules)**: Routing tu dong bang auto-scoring engine. 19 module
  consultants cho SD, FI, MM, CO, PP, QM, PM, WM, PS, HCM, BW, Basis, TM, TR, Ariba, CA, GTS, EHS + Daily Learner.
- **🔌 SAP BTP Connection**: `sap-btp-agent` — ket noi S/4HANA Cloud, doc/activate ABAP, multi-profile.
- **📚 CDS Knowledge Base**: Tra cuu 7,355 CDS views released qua semantic search.
- **📖 SAP Docs Research**: Tra cuu SAP Help, Community, API Hub, Fiori App Library.
- **🔒 Process Discipline**: SessionStart hook ep routing truoc khi tra loi,
  verification-before-completion, systematic-debugging, finish-ticket checklist — chan lai kieu
  loi "code doc on nhung chua chay that".
- **🧠 Context Engineering** (v0.6.2): trim MCP output (observation masking),
  scaffold summary giua cac layer, 2-layer module routing (CORE+DEEP), 3-tier memory
  cho daily-learner — lay pattern tu agent-skills-for-context-engineering.

## Dong gop

Du an la **open-source**, moi dong gop deu duoc chao don!

| File | Muc dich |
|------|----------|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Huong dan dong gop skill, agent, docs |
| [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md) | Template chuan de tao skill / agent / reference module |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Quy tac ung xu cua cong dong |

## Cau truc

```text
sap-abap-agent/
+-- .claude-plugin/            # Manifest plugin Claude Code
+-- commands/                  # /sap-connect
+-- skills/
|   +-- sap-ask-consultant/    # 🧠 Auto-scoring routing engine (18 modules)
|   +-- sap-daily-learner/     # 📚 Daily SAP Learning — Hermes-like (self-improving)
|   +-- sap-btp-setup/         # Setup & troubleshoot SAP BTP connection
|   +-- sap-clean-code/        # ABAP Cloud naming conventions & clean code
|   +-- sap-extensibility/     # Extensibility bac thang cho Public Cloud
|   +-- sap-key-user-toolkit/  # Key User Extensibility handbook
|   +-- sap-cds-kb/            # Tra cuu CDS view qua cds-kb-mcp
|   +-- sap-docs-research/     # Tra cuu SAP Docs qua mcp-sap-docs
|   +-- sap-doc-to-md/         # Convert Word/Excel sang Markdown (markitdown)
|   +-- sap-analyze-function-spec/  # FS.docx -> INTAKE.md (buoc 1 codegen pipeline)
|   +-- sap-write-technical-spec/   # INTAKE.md -> TECHNICAL_SPEC.md (buoc 2)
|   +-- sap-scaffold-rap/           # TECHNICAL_SPEC.md -> RAP 3-layer skeleton (buoc 3)
|   +-- sap-scaffold-cds/           # -> CDS view skeleton, pattern read-only (buoc 3)
|   +-- sap-virtual-element/        # Calculated field trong CDS view
|   +-- sap-atc-review/             # Lint naming/released-API/clean-ABAP (buoc 4)
|   +-- sap-unit-test/              # Sinh ABAP Unit test class (buoc 5)
|   +-- sap-finish-ticket/          # Checklist dong ticket - activation/ATC/test/transport (buoc 6)
|   +-- sap-verification-before-completion/  # Bang chung chay that truoc khi bao "xong"
|   +-- sap-systematic-debugging/   # Debug runtime co he thong (ST22/SAT/breakpoint)
|   +-- sap-routing-discipline/     # Bom qua SessionStart hook - ep check routing truoc khi tra loi
|   +-- sap-context-tool-result-trim/  # Trim/compact MCP tool output (observation masking)
|   +-- sap-scaffold-context-summary/   # Compact giua cac layer scaffold 3-layer
|   +-- sap-context-module-routing/     # Pattern 2-layer (CORE+DEEP) cho reference modules
+-- agents/
|   +-- abap-reviewer.md       # Review code ABAP Cloud
|   +-- sap-ask-consultant dispatch toi 18 module consultants:
|   |   +-- sap-sd-consultant-cloud   # Sales & Distribution
|   |   +-- sap-fi-consultant-cloud   # Financial Accounting
|   |   +-- sap-mm-consultant-cloud   # Materials Management
|   |   +-- sap-co-consultant-cloud   # Controlling
|   |   +-- sap-pp-consultant-cloud   # Production Planning
|   |   +-- sap-qm-consultant-cloud   # Quality Management
|   |   +-- sap-pm-consultant-cloud   # Plant Maintenance
|   |   +-- sap-wm-consultant-cloud   # Warehouse Management
|   |   +-- sap-ps-consultant-cloud   # Project Systems
|   |   +-- sap-hcm-consultant-cloud  # Human Capital Management
|   |   +-- sap-bw-consultant-cloud   # Analytics / BW
|   |   +-- sap-basis-consultant-cloud# Basis / Technical Admin
|   |   +-- sap-tm-consultant-cloud   # Transportation Management
|   |   +-- sap-tr-consultant-cloud   # Treasury & Cash Management
|   |   +-- sap-ariba-consultant-cloud# Procurement Collaboration
|   |   +-- sap-ca-consultant-cloud   # Cross-Application Functions
|   |   +-- sap-gts-consultant-cloud  # Global Trade Services
|   |   +-- sap-ehs-consultant-cloud  # Environment, Health & Safety
|   |   +-- sap-docs-researcher       # CDS view & Docs Research
+-- hooks/                   # Canh bao SELECT * (PostToolUse) + routing discipline (SessionStart)
+-- reference/
    +-- modules/             # Kien thuc module cho tung consultant
    |   +-- sap-[module]-cloud/SKILL.md
    +-- mcp-server/          # MCP server Python (multi-profile)
        +-- sap_btp_agent/
        |   +-- config/        # paths, profile (registry), store, secrets
        |   +-- sap/           # auth (OAuth2), client (REST + auto-reconnect)
        |   +-- tools/         # registry cac tool MCP (co tham so `profile`)
        |   +-- cli/           # wizard setup + quan ly profile
        +-- pyproject.toml
```

## Cai dat (1 lan)

Yeu cau: **Python >= 3.10**. **Khong can clone repo** -- chi can tai 1 file `.whl` va `pip install`:

```bash
pip install https://github.com/StormShynn/sap-abap-agent/releases/download/mcp-server-v0.3.0/sap_abap_agent_mcp-0.3.0-py3-none-any.whl
```

(Hoac tai file `.whl` ve truoc roi `pip install duong-dan-file.whl` neu may khong co internet luc chay lenh.)

Tren Windows, cai them extra `win-dpapi` de ma hoa secrets bang DPAPI (them `[win-dpapi]` ngay sau ten file, truoc phan mo rong `.whl`):

```bash
pip install "sap_abap_agent_mcp-0.3.0-py3-none-any.whl[win-dpapi]"
```

Neu muon dung Cookie-based auth kieu **tu mo browser dang nhap** (khong can F12 copy tay), cai them extra `playwright`
va download browser binary:

```bash
pip install "sap_abap_agent_mcp-0.3.0-py3-none-any.whl[playwright]"
playwright install chromium
```

Sau buoc cai, ban se co lenh `sap-btp-agent` trong PATH (entry point khai bao trong `pyproject.toml`).

<details>
<summary>Dev / contributor: cai tu source (editable install)</summary>

```bash
git clone https://github.com/StormShynn/sap-abap-agent.git
cd sap-abap-agent/reference/mcp-server
pip install -e .[win-dpapi,playwright]
```

Dung khi ban muon sua code MCP server (`reference/mcp-server/sap_btp_agent/`) va thay doi co hieu luc ngay
khong can build lai wheel. Build wheel moi de release:

```bash
pip install build
python -m build --wheel
# -> dist/sap_abap_agent_mcp-<version>-py3-none-any.whl
```

</details>

**Kiem tra ngay sau khi cai** (khuyen dung, danh cho moi nguoi -- khong can dung AI de debug):

```bash
python -m sap_btp_agent.doctor
```

Lenh nay chay duoc **ngay ca khi `sap-btp-agent` chua nam trong PATH** (loi thuong gap nhat tren Windows: `pip`
cai vao user-scheme site-packages vi khong co quyen viet vao Python goc, VD `%APPDATA%\Python\PythonXY\Scripts`,
folder nay thuong khong tu dong co trong PATH). Doctor se tu phat hien va in san lenh PowerShell de fix, kem
kiem tra cac dependency hay bi thieu ngam (pywin32/DPAPI, playwright+chromium...). Sau khi da cai xong va PATH
dung, co the goi lai qua `sap-btp-agent doctor`.

## Them project SAP moi

Cach nhanh nhat -- truyen URL truc tiep:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Wizard se tu sinh profile id tu hostname (`project1.s4hana.cloud.sap`) va hoi phuong thuc xac thuc (chon 1-4):

1. **OAuth2** (client_credentials) -- `client_id` + `client_secret`, mac dinh/khuyen dung
2. **Password** -- `username` + `password`
3. **Bearer token** -- token co san, nhap tay
4. **Cookie-based** -- session cookie SAP (`MYSAPSSO2`, `SAP_SESSIONID`, `sap-usercontext`...). Wizard hoi tiep lay cookie tu dau:
   - (1) File cookie Netscape format
   - (2) Paste tay (F12 -> Application -> Cookies)
   - (3) **Auto** -- tu mo browser cho ban dang nhap, tu lay cookie (can extra `playwright`, khong co se fallback ve paste tay)

   Sau khi co cookie, tu dong re-auth qua browser popup (hoac Playwright) moi lan session het han (401).

Sau do hoi them Region, service type.

Thong tin duoc luu rieng trong `profiles/<id>/`:

```
%USERPROFILE%\.sap-btp-agent\profiles\project1.s4hana.cloud.sap\
+-- config.json     <- URL, tenant, client_id, region, service (khong nhay cam)
+-- secrets.json    <- client_secret / token (DA MA HOA)
```

**Them project thu 2, 3...** cung de:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Moi project se co profile rieng, secret rieng (ma hoa doc lap).

## Quan ly nhieu profile

```bash
sap-btp-agent profiles list             # liet ke profile (* = active)
sap-btp-agent profiles use project1     # chon profile active
sap-btp-agent profiles show             # xem chi tiet profile active
sap-btp-agent profiles remove project2  # xoa 1 profile
sap-btp-agent reset                     # xoa TAT CA (can than!)
```

## Kiem tra ket noi

```bash
sap-btp-agent connect                            # test profile active
sap-btp-agent connect project1.s4hana.cloud.sap  # test 1 profile cu the
```

## Dang ky MCP voi Claude Code

`sap-btp-agent` goi khong co argument se chay MCP stdio server (`sap_btp_agent/server.py`), serve cac tool
ben duoi qua JSON-RPC. Da test end-to-end (initialize -> tools/list -> tools/call) truoc khi cong bo.

Dung lenh `claude mcp add` (Claude Code khong con dung file `mcp_servers.json`):

```bash
claude mcp add --transport stdio sap-btp -- sap-btp-agent
```

Mac dinh la scope `local` (chi may nay, chi project hien tai). Dung `--scope user` de dung duoc o moi project,
hoac `--scope project` de luu vao `.mcp.json` va chia se qua git cho ca team.

Mo Claude Code voi plugin, cac tool sau se xuat hien:

| Tool                  | Mo ta                                                       |
|-----------------------|-------------------------------------------------------------|
| `sap_list_profiles`   | Liet ke cac profile da cau hinh                             |
| `sap_ping`            | Test ket noi profile (co tham so `profile`)                 |
| `sap_list_packages`   | Liet ke package ABAP                                        |
| `sap_search`          | Tim object ABAP theo ten                                    |
| `sap_read_source`     | Doc source code (class, program, include...)                |
| `sap_syntax_check`    | Syntax check (khong activate)                               |
| `sap_activate`        | Activate object (transport local)                           |

### MCP server phu tro: tra cuu CDS view & SAP docs

Theo mac dinh, Claude Code chi chap nhan 1 MCP server stdio. De su dung them cac MCP server
remote (cds-kb-mcp va mcp-sap-docs), dung `claude mcp add` voi transport `sse`:

**CDS Knowledge Base** (7,355 released CDS views):

Cach 1 — `claude mcp add` (neu Claude Code ho tro `--transport sse`):

```bash
claude mcp add --transport sse cds-kb --url https://cds-kb-mcp-production.up.railway.app/sse
# Neu primary khong truy cap duoc, dung fallback:
# claude mcp add --transport sse cds-kb --url https://cds-kb-mcp.cfapps.ap21.hana.ondemand.com/sse
```

Cach 2 — `supergateway` (tuong thich voi moi IDE ho tro MCP: Cursor, Claude Desktop, VS Code, Gemini IDE):

```json
{
  "mcpServers": {
    "cds-kb": {
      "command": "npx",
      "args": ["-y", "supergateway@2.0.0", "--sse", "https://cds-kb-mcp-production.up.railway.app/sse"]
    }
  }
}
```

**SAP Docs Research** (SAP Help, Community, API Hub, Fiori App, Clean Core):

Cach 1 — `claude mcp add`:

```bash
claude mcp add --transport sse mcp-sap-docs-btp --url https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse
# Neu co SAP-API-HUB-KEY:
# claude mcp add --transport sse mcp-sap-docs-btp --url https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse --headers "{\"SAP-API-HUB-KEY\": \"<YOUR_KEY>\"}"
```

Cach 2 — `supergateway`:

```json
{
  "mcpServers": {
    "mcp-sap-docs-btp": {
      "command": "npx",
      "args": ["-y", "supergateway@2.0.0", "--sse", "https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse"],
      "disabled": false
    }
  }
}
```

> **Windows users**: Neu dung supergateway, co the can dung `supergateway.cmd` thay vi `supergateway`
> hoac chi dinh duong dan tuyet doi.

Sau khi cau hinh, AI se co them cac tool:

| Tool | Server | Mo ta |
|------|--------|-------|
| `search_cds` | cds-kb | Tim CDS view theo business meaning |
| `get_cds_view` | cds-kb | Lay definition day du cua 1 CDS view |
| `get_views_by_tag` | cds-kb | Liet ke CDS view theo tag (BO, LOB, module) |
| `get_taxonomy` | cds-kb | Kham pha Lines of Business → Business Objects |
| `kb_info` | cds-kb | Kiem tra version KB |
| `search` | mcp-sap-docs-btp | Tra cuu SAP Help Portal + offline docs |
| `sap_community_search` | mcp-sap-docs-btp | Tim kiem SAP Community Q&A |
| `sap_search_objects` | mcp-sap-docs-btp | Tra cuu Clean Core Released Objects |
| `abap_feature_matrix` | mcp-sap-docs-btp | Kiem tra ABAP syntax support |
| `sap_accelerator_hub_*` | mcp-sap-docs-btp | Kham pha API tren SAP Accelerator Hub |
| `sap_fiori_library_*` | mcp-sap-docs-btp | Tra cuu Fiori App Reference Library |
| `sap_discovery_center_*` | mcp-sap-docs-btp | Kham pha BTP services & pricing |
| `abap_lint` | mcp-sap-docs-btp | Kiem tra chat luong code ABAP |

> **Luu y**: Server `mcp-sap-docs-btp` can `SAP-API-HUB-KEY` de cac tool `sap_accelerator_hub_*`
> hoat dong day du. Cac tool con lai van chay khong can key.

Moi tool deu co tham so `profile` (de trong = profile active). Vi du:

```
"Liet ke cac package trong project project1"
-> Claude goi sap_list_packages({ profile: "project1.s4hana.cloud.sap" })

"Tim class ZCL_* trong project dang dung"
-> Claude goi sap_search({ query: "ZCL_" })
```

## Chay nhieu instance cung luc (1 profile / instance)

Dat env `SAP_BTP_PROFILE=<id>` truoc moi lan chay:

```bash
# Terminal 1: Claude 1 voi profile A
SAP_BTP_PROFILE=project1.s4hana.cloud.sap sap-btp-agent

# Terminal 2: Claude 2 voi profile B
SAP_BTP_PROFILE=project1.s4hana.cloud.sap sap-btp-agent
```

## Cau hinh folder

```
%USERPROFILE%\.sap-btp-agent\   (Windows)
~/.sap-btp-agent/               (macOS/Linux)
+-- profiles.json                <- registry (danh sach + active)
+-- profiles/
|   +-- <profile-id>/            <- 1 folder / project SAP
|       +-- config.json
|       +-- secrets.json         <- MA HOA
+-- log/
+-- cache/
```

- **Windows**: secrets ma hoa bang **DPAPI** qua PowerShell (gan voi tai khoan Windows).
- **macOS/Linux**: **AES-256-GCM**, key derive tu `hostname + username`.
- File mode `0o600`, chi owner doc/ghi.

## Env

- `SAP_BTP_PROFILE=<id>` -- khoa profile cho 1 lan chay (uu tien registry)
- `SAP_BTP_AGENT_HOME=/path` -- doi folder cau hinh (test, multi-tenant)

## 🧠 SAP Consultant System (Auto-scoring Routing Engine)

`skills/sap-ask-consultant/SKILL.md` la skill trung tam, dispatch cau hoi user toi **18 module
consultants + 1 researcher + 1 daily learner** bang co che **keyword scoring + parallel dispatch**.

### Cach hoat dong

1. **Keyword Matrix**: Moi module co keywords voi weight 3/2/1.
2. **Tinh score**: Module nao >= threshold (2) thi duoc dispatch.
3. **Explicit mention**: "hoi SD", "hoi FI" → dispatch mac dinh.
4. **Module coupling**: Module thuong di cung (FI↔CO, PP→QM→MM...) tu dong dispatch.
5. **Parallel dispatch**: Tat ca module >= threshold dispatch song song trong 1 message.

### Vi du

| Cau hoi | Module dispatch |
|---------|----------------|
| "tim CDS view cho sales order bi cham giao hang" | `sap-docs-researcher` + `sap-sd-consultant-cloud` song song |
| "cau hinh cost center va GL" | `sap-co-consultant-cloud` + `sap-fi-consultant-cloud` (coupling) |
| "lam sao tao purchase order" | `sap-mm-consultant-cloud` |
| "hoi PP, QM, MM" | `sap-pp` + `sap-qm` + `sap-mm` song song |

### Cac module da co

| # | Agent | Module |
|---|-------|--------|
| 1 | `sap-sd-consultant-cloud` | Sales & Distribution |
| 2 | `sap-fi-consultant-cloud` | Financial Accounting |
| 3 | `sap-mm-consultant-cloud` | Materials Management |
| 4 | `sap-co-consultant-cloud` | Controlling |
| 5 | `sap-pp-consultant-cloud` | Production Planning |
| 6 | `sap-qm-consultant-cloud` | Quality Management |
| 7 | `sap-pm-consultant-cloud` | Plant Maintenance |
| 8 | `sap-wm-consultant-cloud` | Warehouse Management |
| 9 | `sap-ps-consultant-cloud` | Project Systems |
| 10 | `sap-hcm-consultant-cloud` | Human Capital Management |
| 11 | `sap-bw-consultant-cloud` | Analytics / BW |
| 12 | `sap-basis-consultant-cloud` | Basis / Technical Admin |
| 13 | `sap-tm-consultant-cloud` | Transportation Management |
| 14 | `sap-tr-consultant-cloud` | Treasury & Cash Management |
| 15 | `sap-ariba-consultant-cloud` | Procurement Collaboration |
| 16 | `sap-ca-consultant-cloud` | Cross-Application Functions |
| 17 | `sap-gts-consultant-cloud` | Global Trade Services |
| 18 | `sap-ehs-consultant-cloud` | Environment, Health & Safety |
| 19 | `sap-docs-researcher` | CDS view & Docs Research |
| 20 | `sap-daily-learner` | Daily SAP Learning, Hermes-like skill creation |

## 🏗️ Codegen Pipeline (Function Spec -> ABAP code)

8 skill noi tiep nhau, bien Function Spec (`.docx` khach hang gui) thanh code ABAP da activate,
review, test va san sang release, theo chuan RAP/CDS. File trung gian dat trong `in/`/`out/` — **thu muc local per-user, KHONG nam trong
git repo**: `%USERPROFILE%\.sap-btp-agent\in\` + `...\out\` (Windows) hoac `~/.sap-btp-agent/in/` +
`.../out/` (macOS/Linux), cung noi luu profile/secrets ket noi SAP BTP (xem muc "Cau hinh folder").
Ly do: tai lieu FS va output sinh ra la du lieu nghiep vu/khach hang, khong nen nam chung voi
source code plugin (rui ro commit nham len repo public). Co the doi qua env `SAP_BTP_AGENT_HOME`.
Lay dung duong dan: `python -c "from sap_btp_agent.config.paths import get_in_dir; print(get_in_dir())"`.

```bash
# 0. Dat FS vao in/ (thu muc local per-user o tren), convert sang markdown
cp /path/to/FS_xxx.docx "$(python -c 'from sap_btp_agent.config.paths import get_in_dir; print(get_in_dir())')/"
# -> skill sap-doc-to-md (reference/scripts/office_to_md.py, khong tham so) -> out/FS_xxx.md

# 1. Phan tich FS -> chuan hoa yeu cau
# -> skill sap-analyze-function-spec -> out/<ticket>/INTAKE.md

# 2. Quyet dinh kien truc (managed/unmanaged/CDS/class)
# -> skill sap-write-technical-spec -> out/<ticket>/TECHNICAL_SPEC.md

# 3. Sinh skeleton code
# -> skill sap-scaffold-rap (CRUD/RAP) hoac sap-scaffold-cds (chi-read) -> out/<ticket>/src/

# 4. Review naming/released-API/clean-ABAP
# -> skill sap-atc-review -> out/<ticket>/ATC_REVIEW.md

# 5. Sinh ABAP Unit test
# -> skill sap-unit-test

# 6. Checklist dong ticket (activation/ATC/test/transport/abapGit)
# -> skill sap-finish-ticket -> out/<ticket>/FINISH_CHECKLIST.md
```

Skill phu tro: `sap-virtual-element` (calculated field trong CDS). Quy uoc dat ten & bac thang
extensibility dung chung voi `sap-clean-code` / `sap-extensibility`. Khi can tim CDS view/API
chuan cho 1 phan he cu the (buoc 2), hoi agent consultant tuong ung (`sap-fi-consultant-cloud`,
`sap-mm-consultant-cloud`...) hoac `sap-docs-researcher`.

Ky luat xuyen suot (khong phai buoc rieng, ap dung moi luc trong pipeline): `sap-routing-discipline`
(luon check routing truoc khi tra loi — bom tu dong qua SessionStart hook),
`sap-verification-before-completion` (bang chung chay that truoc khi bao "xong"),
`sap-systematic-debugging` (khi co bug runtime, thay vi doan-sua-lap-lai).

## Test local

```bash
cd ..
claude --plugin-dir ./sap-abap-agent
```

Trong Claude:
- "Setup SAP BTP cho project https://project1.s4hana.cloud.sap" -> goi wizard
- "Liet ke cac profile SAP cua toi" -> goi `sap_list_profiles`
- "Tim class bat dau bang ZCL_ trong project project1" -> goi `sap_search` voi `profile="project1..."`
- "Hoi SD: cau hinh pricing cho sales order" -> goi `sap-sd-consultant-cloud`
- "Tim CDS view cho purchase order qua han va hoi MM" -> `sap-docs-researcher` + `sap-mm-consultant-cloud`
- "Hoc SAP hom nay" -> `sap-daily-learner` (daily tip + learning path)
- "Quiz MM cho toi" -> `sap-daily-learner` (trac nghiem MM)
- "Cau hinh cost center va cash management" -> `sap-co-consultant-cloud` + `sap-tr-consultant-cloud`

## Loi thuong gap

| Loi                                 | Cach sua                                                  |
|-------------------------------------|-----------------------------------------------------------|
| `401 Unauthorized`                  | Client_secret sai / het han. Chay `setup <profile-id>`    |
| `404 /oauth/token`                  | Sua `tokenUrl` trong `profiles/<id>/secrets.json`         |
| `Khong giai ma duoc secret`         | Doi may. Chay `setup <profile-id>` de tao lai             |
| `Chua co profile nao`               | Chay `sap-btp-agent setup <URL>`                          |
| `'sap-btp-agent' is not recognized` | PATH thieu folder chua entry point. Chay `python -m sap_btp_agent.doctor` de tu phat hien + lay lenh fix |

## Trang thai

v0.6.2 -- **20 agents (18 modules + 1 researcher + 1 daily learner)** voi auto-scoring routing engine,
CDS KB, SAP Docs Research, ABAP Cloud clean code, extensibility, key user toolkit, Hermes-like self-improving learning.
