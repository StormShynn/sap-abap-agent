---
name: sap-routing-discipline
description: |
  Nguyen tac luon kiem tra routing/skill phu hop truoc khi tra loi cau hoi lien quan SAP,
  thay vi tra loi truc tiep tu kien thuc chung. Duoc bom tu dong vao dau moi phien qua
  SessionStart hook (hooks/hooks.json) - khong can goi thu cong.
when_to_use: |
  Tu dong ap dung dau moi phien (session start/clear/compact). Doc lai khi nghi ngo minh
  dang tra loi truc tiep ma bo qua buoc routing qua sap-ask-consultant.
model: haiku
effort: low
---

# SAP Routing Discipline

## Quy tac

Truoc khi tra loi bat ky cau hoi nao co the lien quan nghiep vu/ky thuat SAP, chay qua bang
scoring cua skill `sap-ask-consultant` truoc - ke ca khi cau hoi "de", chi la follow-up, hoac
ban thay chac chan da biet cau tra loi. Agent module co `reference/modules/*.md` voi SSCUI,
API, Fiori app cu the ma kien thuc chung khong co.

## Vien co thuong gap - dung tra loi truc tiep khi thay 1 trong nhung dieu nay trong dau

| # | Vien co | Phai lam |
|---|---|---|
| R1 | "Cau hoi don gian, tra loi luon khoi check module" | Van chay qua scoring `sap-ask-consultant` |
| R2 | "Ro rang la cau hoi code/ABAP, khoi can agent tu van" | Kiem tra co lan nghiep vu khong (vd "sao GL nay khong post" = FI + code) |
| R3 | "User hoi follow-up, dung context cu la du" | Follow-up doi module (SD -> FI) van phai re-route |
| R4 | "Khong thay keyword ro, chac khong module nao ca" | Score duoi threshold: hoi lai user, khong tu suy dien tra loi |
| R5 | "Da biet dap an tu kien thuc chung" | Agent chuyen sau co SSCUI/API/Fiori app cu the - kien thuc chung khong co |
| R6 | "Context dang phinh, rut gon di" | Xem Tier 2 routing rules ben duoi TRUOC khi compact |
| R7 | "Module consultant load full SKILL.md luon" | Module FI da tach 2-layer (core+deep), chi load deep khi user hoi chi tiet - xem Tier 2 |
| R8 | "Output MCP tool nho, tra nguyen" | Neu >2K token, doc `reference/process/sap-context-tool-result-trim.md` va ap dung masking truoc khi paste vao context |

## Tier 2 routing rules (CONTEXT-INJECTION - ngon ngu tu context-optimization)

Phan nay ap dung cac pattern cua `context-optimization` skill (KV-cache + observation masking)
cho routing engine.

### Tier 2.1 - 2-layer module routing

Module consultant agent chi load CORE layer (~20-30 dong) cua `reference/modules/<m>-cloud/SKILL.md`
theo mac dinh. Chi load DEEP layer (`deep/SKILL.md`) khi:

- User hoi chi tiet SSCUI/Fiori app cu the (vd "SSCUI nao cau hinh dong so?").
- User hoi released API cu the (vd "API nao de doc Journal Entry?").
- User hoi extensibility bac thang cho 1 module cu the.
- Agent phai cross-check voi SAP Help / API Hub.

Module FI da tach (xem `reference/modules/sap-fi-cloud/SKILL.md` core + `deep/SKILL.md`). 17
module con lai se tach lan luot theo `reference/process/sap-context-module-routing.md`.

Khi dispatch nhieu module song song (vd SD + FI + CO), **tong token** = tong CORE layers (nho)
+ chi module nao load DEEP (neu can). Truoc day: tong FULL SKILL.md cua 3 module (~600 lines).

### Tier 2.2 - Output tool-result masking (KV-cache friendly)

Khi tool output (cds-kb-mcp, sap-docs, sap-btp-agent) > ~2K token (~8KB text):
1. KHONG paste full vao context.
2. Doc `reference/process/sap-context-tool-result-trim.md` va ap dung (Pattern A/B/C/D tuy tool).
3. Chi paste compact summary + path den cache file.
4. **KHONG** them "trim applied at <timestamp>" vao summary (rule KV-cache stable prefix -
   timestamp se pha cache hit rate).

### Tier 2.3 - Working memory cho long session

Khi session > 10 turn lien quan cung 1 ticket/project:
- Ap dung working memory: ghi summary vao `<agent-home>/sessions/<ticket>/` (`<agent-home>` =
  `%USERPROFILE%\.sap-abap-agent\`, xem `reference/process/sap-scaffold-context-summary.md`).
- Skill `sap-analyze-function-spec`: tach FS thanh 8 chunks.
- `reference/process/sap-scaffold-context-summary.md`: snapshot full source giua cac layer scaffold.

### Tier 2.4 - Memory tier routing

Khi user hoi ve "lich su" / "hom qua" / "truoc do":
- Load EPISODIC tier (chat history) - KHONG mac dinh load.
- KHONG load full episodic file - chi doc `index.jsonl` de biet session nao lien quan, sau do
  doc session file cu the.

## Ngoai le - khong can route

- Cau hoi ve **cach dung/cai dat plugin nay** (khong phai nghiep vu SAP) - vd loi cai dat, cau
  hinh BTP: dung truc tiep hoac skill `sap-btp-setup`.
- User da noi ro "tra loi truc tiep, khong can hoi agent" - instruction cua user luon uu tien
  hon quy tac nay.

## Tich hop

- Skill `sap-ask-consultant` - noi thuc hien scoring & dispatch that su (Tier 2.1 routing rule).
- Skill `sap-atc-review` - cung dung format bang vien co nay (R1-R7) cho tang code review.
- `reference/process/sap-context-tool-result-trim.md` - Pattern A/B/C/D cho masking (Tier 2.2).
- `reference/process/sap-context-module-routing.md` - pattern tach module 2-layer (Tier 2.1).
- `reference/process/sap-scaffold-context-summary.md` - snapshot giua cac layer scaffold (Tier 2.3).
- Skill `sap-daily-learner` - memory tier loading (Tier 2.4).
- `hooks/hooks.json` (SessionStart) - co che bom noi dung file nay vao dau phien. File nay
  phai on dinh (khong them timestamp, khong dynamic data) de giu KV-cache hit rate cao.
- Skill `sap-ask-before-guessing` - nguyen tac song song, bom qua cung hook: TONG QUAT hoa vien
  co R4 (hoi khi khong chac) ra MOI diem quyet dinh trong pipeline scaffold/deploy, khong chi
  routing module.