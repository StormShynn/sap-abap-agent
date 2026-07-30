---
name: sap-multi-system-context
description: |
  Chon dung MCP server (sap-connect / sap-vsp / sap-dict-bridge) cho moi task dua tren
  profile SAP dang active va block `routingHints` (schema v2 cua mcp-sap-connect). Khi gap
  task ABAP moi, can biet goi tool nao o server nao - skill nay tra ve 1 bang quyet dinh
  (Public/Private/RISE/On-prem/BTP x Read/Write/Analysis/Debug/Dict-Bridge) thay vi de
  agent phai doan. Dung TRUOC khi goi tool sap_* hoac vsp_* neu khong ro tool do den tu
  server nao. KHONG dung khi da co cache con moi (< 7 ngay) hoac chi can 1 tool don le
  (vi du "read source class ZCL_FOO" -> goi truc tiep sap_read_source).
when_to_use: |
  "task nay can goi server nao", "tool sap_* vs vsp_* khac gi",
  "co the debug tren system nay khong", "co the tao Domain tren BTP Steampunk khong",
  "phan biet 5 edition SAP".
argument-hint: "[task hoac capability can check]"
model: sonnet
effort: low
tools: [Read, Bash]
---

# SAP Multi-System Context — Chon dung backend cho moi task

## Tai sao can skill nay

Sau Phase 1 (rename `mcp-sap-connect`) + Phase 2 (schema v2 + 5 service type + `routingHints`),
profile SAP cua user da co day du metadata de **quyet dinh** tool nen goi qua server nao.
Tuy nhien agent rat de:

- Lang phi token: thu goi `sap_*` tool khi task can `vsp_*` (hoac nguoc lai) mat vong lap retry.
- Dot loi: goi debug tool tren Public Cloud (khong ho tro) hoac dict-bridge tren Steampunk
  (khong co DDIC truyen thong).
- Canh bao sai edition: tra loi cho user theo SSCUI/Fiori cua Public nguoi dung that o Private
  se khong match.

Skill nay giai quyet bang cach:
1. Doc `routingHints` tu profile (schema v2).
2. Build decision matrix 5 edition x 5 capability.
3. Cache lai 7 ngay (cung TTL voi `sap-bootstrap-system-context`).
4. Tra ve 1 bang ngan cho agent, kem chi dinh tool can goi.

## Khi nao dung

- ✅ Truoc khi goi bat ky tool sap_* / vsp_* / sap_create_* neu khong ro backend.
- ✅ Khi user hoi "task X co lam duoc tren system nay khong".
- ✅ Khi can canh bao user (vi du "Public Cloud khong cho debug, chi On-prem/RISE moi co").
- ❌ Da co cache con moi (< 7 ngay) cho profile hien tai — dung lai.
- ❌ Chi can 1 tool don le da biet (sap_read_source, sap_search...) — goi truc tiep.

## Quy trinh

### Buoc 0: Kiem tra cache 7 ngay

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" cache/multi-system-context
```

Neu con file cache cho profile hien tai (path tra ve tu lenh tren) con trong 7 ngay, doc lai
va dung. **KHONG** tu kiem tra lai. Neu qua han hoac khong co -> Buoc 1.

Lay `profile_id` active:
- Uu tien env `MCP_SAP_CONNECT_PROFILE` (hoac alias cu `SAP_BTP_PROFILE`).
- Fallback `mcp-sap-connect profiles show` (doc registry.json trong `~/.mcp-sap-connect`).

### Buoc 1: Doc profile config

```bash
python -c "import json,os; from mcp_sap_connect.config.paths import get_profile_config_file; \
  print(json.dumps(json.loads(get_profile_config_file(os.environ.get('MCP_SAP_CONNECT_PROFILE')).read_text(encoding='utf-8')), ensure_ascii=False, indent=2))"
```

Hoac goi tool `mcp__sap-connect__sap_get_system_info` (tra ve system info + service type).
Doc 3 field:
- `service`: 1 trong 5 edition (s4hc_(public)/s4hc_(private)/btp/onprem/rise_with_sap)
- `authMode`: cookie/oauth2/password/bearer
- `routingHints`: block 7 key (supportsReadonlyClass, supportsDebug, supportsVspSlim,
  supportsVspHealth, supportsDictBridge, preferredTransport, preferredAnalysis)

Neu `routingHints` thieu -> file cu (schema v1) -> goi `mcp-sap-connect setup` de upgrade.

### Buoc 2: Build decision matrix

| Capability (task) | Public | Private | RISE | On-prem | BTP (Steampunk) |
|---|---|---|---|---|---|
| Doc source / search / list (sap_*) | sap-connect | sap-connect | sap-connect | sap-connect | sap-connect |
| Create/update/activate ABAP (sap_*) | sap-connect | sap-connect | sap-connect | sap-connect | sap-connect |
| Package health / dead code | sap-vsp (if supportsVspHealth/Slim) | sap-vsp | sap-vsp | sap-vsp | sap-vsp |
| Debug (breakpoint, listen, step) | ❌ (supportsDebug=false) | sap-vsp | sap-vsp | sap-vsp | sap-vsp (limited) |
| Tao DDIC (Domain/Data Element/Table) | sap-dict-bridge | sap-dict-bridge | sap-dict-bridge | sap-dict-bridge | ❌ (supportsDictBridge=false) |
| CDS view / RAP behavior (sap_*) | sap-connect | sap-connect | sap-connect | sap-connect | sap-connect |
| ABAP SQL query (sap_execute_query / vsp RunQuery) | sap-connect (limited) | sap-connect (limited) | sap-connect (limited) | sap-connect (limited) | sap-vsp RunQuery (prefers) |

**Rule**: luon check `supports*` tu `routingHints` truoc khi goi. Neu `supports* = false`, tool
do KHONG duoc goi tren profile nay (agent se nhan loi runtime).

### Buoc 3: Output cho agent

In ra 1 bang ngan de agent quyet dinh:

```
[profile: <id>] service=<service> authMode=<auth> routingHints=<key=value...>
| Task | Backend | Tool | Notes |
|---|---|---|---|
| read source class | sap-connect | sap_read_source | |
| package health | sap-vsp | vsp health | supportsVspHealth=true |
| debug | ❌ | - | supportsDebug=false (Public Cloud) |
| create Domain | sap-dict-bridge | sap_create_domain | supportsDictBridge=true |
```

### Buoc 4: Ghi cache

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" cache/multi-system-context
```

Ghi vao `<agent-home>/cache/multi-system-context/<profile-id>.md` (path tu lenh tren) gom:
- profile id + service + auth + routingHints
- decision matrix (Buoc 2) - la output, khong tinh lai
- timestamp hien tai
- known_limitations tu `KNOWN_LIMITATIONS.md` lien quan (neu co)

Cache **het han sau 7 ngay** - khi qua han, skill se re-do Buoc 1-3.

## Luu y

- ⚠️ **Phase 3 chua xong**: `sap-vsp` auto-download chua duoc implement. Hien tai user can
  tu cai `vsp` binary (xem `reference/mcp-guides/sap-vsp.md` - TODO Phase 3). Neu vsp chua
  duoc register trong `.mcp.json`, cac task goi `vsp_*` se fail - canh bao user.
- ⚠️ **Profile switching**: vsp single-profile. Neu user switch profile (qua
  `mcp-sap-connect profiles use <other>`), can re-register vsp voi credentials moi (Phase 3
  se tu dong).
- 🔗 Buoc tiep theo: goi tool cu the tren backend da chon. Skill `sap-ask-consultant` se
  goi skill nay o Buoc 5.5 cua routing matrix (tich hop Phase 4).
- 🔗 Source: `mcp_sap_connect.config.store.normalize_routing_hints(service)` de xem
  defaults cua moi edition.
