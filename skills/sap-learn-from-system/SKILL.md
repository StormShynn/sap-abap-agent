---
name: sap-learn-from-system
description: |
  Hoc tu he thong SAP dang ket noi (MCP): doc table/class/CDS that, rut lesson card
  local (Hermes-like). KHONG push Notion o ban nay — chi checklist + ghi memory.
  Dung khi user muon "hoc tu he thong", kham pha Z* object, rut pattern tu code that.
  KHONG dung thay daily tip/quiz (sap-daily-learner) hay scaffold (sap-scaffold-*).
when_to_use: |
  "hoc tu he thong", "hoc tu SAP dang ket noi", "kham pha table Z", "doc class ZCL_ de hoc",
  "rut pattern tu package", "lesson tu object that", "explore system objects".
argument-hint: "[package | object name | module goi y]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Bash]
---

# SAP Learn From System — Hoc tu MCP SAP that (Hermes-like, local)

## Muc tieu

Khi user **da MCP vao SAP**, skill nay:

1. Xac nhan ket noi (ping).
2. Chon 1–5 object that (table / class / CDS / domain…).
3. Doc source/structure qua MCP — **khong doan**.
4. Viet **lesson card** vao `<agent-home>/memory/` (scrub: khong paste bulk source noi bo).
5. Hien **checklist** ket thuc session (Notion = buoc sau, chua auto).

Lay cam hung Hermes (self-improving) + `sap-daily-learner` memory — **khong** can Hermes Agent / `hermes mcp serve`.

## Khi nao dung

- ✅ User muon hoc / ghi nhan pattern tu **he thong dang ping**.
- ✅ Sau `mcp-sap-connect connect` / MCP Core san sang.
- ❌ Chi muon tip/quiz hang ngay → `sap-daily-learner`.
- ❌ Muon scaffold code → `sap-scaffold-*` / `sap-bootstrap-system-context`.
- ❌ Chua co MCP SAP → dung, huong dan `#cai-dat` / `#ket-noi` / GUI MCP Core.

## Pham vi ghi (BAT BUOC)

Giong `sap-daily-learner`:

- Chi `Write`/`Edit` duoi `<agent-home>` (`agent_home.py` / `SAP_ABAP_AGENT_HOME`).
- Duong dan hop le: `memory/semantic/lessons/`, `memory/semantic/notes/`, `memory/episodic/`.
- **KHONG** ghi source ABAP day du cua khach vao file; chi tom tat pattern (ten object, 3–7 bullet).
- **KHONG** goi Notion / khong promote `reference/modules/` o ban nay.

Bootstrap neu can:

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/bootstrap_memory.py" \
  --ensure-dir memory/semantic/lessons/system \
  --ensure-dir memory/semantic/notes/system
```

## Quy trinh

### Buoc 0 — Gate ket noi

1. Goi MCP `sap_ping` (hoac CLI `mcp-sap-connect ping`) tren profile active / user chi dinh.
2. Fail → dung. Bao user chay `mcp-sap-connect connect` / `reauth`, khong bia lesson.
3. (Tuy chon) `sap_get_system_info` — ghi edition/profile vao phan meta lesson.

### Buoc 1 — Chon doi tuong hoc (toi da 5 / session)

Uu tien (theo thu tu):

1. Object user **chi ro** (ten table/class/CDS).
2. Package user chi / package Z* gan day (`sap_list_packages` / `sap_search`).
3. Mau Z*/Y*: TABLE, CLAS, DDLS/CDS — 2–5 object **khac loai** neu co the.

Checklist chon (in cho user truoc khi doc nhieu):

- [ ] Da ping OK
- [ ] Co ten object / package muc tieu
- [ ] Gioi han ≤ 5 object
- [ ] User dong y doc object do (neu package lon / nhay cam)

### Buoc 2 — Doc that qua MCP

Voi moi object:

| Loai | Tool goi y |
|------|------------|
| Class / include | `sap_read_source` |
| Tim theo ten | `sap_search` |
| Package | `sap_list_packages` |
| CDS released (nghia nghiep) | CDS KB `search_cds` / `get_cds_view` (khong thay the object Z* tren tenant) |

Doc dung muc can de hieu pattern — **khong** dump toan bo class lon vao lesson.

### Buoc 3 — Lesson card (scrub)

Moi object (hoac 1 card gom nhom) ghi:

```markdown
# Lesson — <OBJECT> (<TYPE>)
- Profile / URL host (khong secret): ...
- Ngay: YYYY-MM-DD
- Package: ...
## Pattern rut ra
- ...
## Tai sao quan trong (1-3 cau)
- ...
## Lien quan
- Module goi y: SD/FI/... (neu co)
- Khong copy: source day du, client data, credential
## Next
- [ ] On lai bang quiz (`sap-daily-learner`) — tuy chon
- [ ] (Sau nay) Share Notion — **chua bat o skill nay**
```

Ghi file:

- 1 object: `memory/semantic/notes/system/<object-lower>.md`
- Append dong ngan vao `memory/semantic/lessons/system/<MODULE-or-GENERAL>.jsonl` (1 JSON/line: date, object, type, bullets).

Cap nhat nhe `LEARNING_PROGRESS.md` neu topic moi (1 dong) — khong ghi de tien do cu.

### Buoc 4 — Checklist ket thuc (bat buoc in ra)

Copy checklist day du tu `skills/sap-learn-from-system/CHECKLIST.md` (hoac tom tat):

- [ ] Ping OK truoc khi doc
- [ ] ≤ 5 object; da doc that qua MCP
- [ ] Lesson chi pattern, khong bulk source
- [ ] File nam trong `<agent-home>/memory/...`
- [ ] Notion: **chua** auto — user tu copy neu muon chia se
- [ ] Goi y: `sap-daily-learner` neu muon tip/quiz tiep

## Notion (tuong lai — chua implement)

Ke hoach (khong code o day): scrub lesson → page "SAP Skills" / collection team, giong muc 3b cua `sap-daily-learner`. Ban nay chi de checkbox "San sang share" tren checklist.

## Lien ket

- `sap-daily-learner` — tip, quiz, Notion 2-way, curator
- `sap-bootstrap-system-context` — do quy uoc truoc scaffold (khac muc tieu hoc)
- `sap-clean-code` / `sap-released-classes` — doi chieu pattern Cloud
- MCP Core: `mcp-sap-connect`, dict-bridge, cds-kb, mcp-sap-docs-btp
