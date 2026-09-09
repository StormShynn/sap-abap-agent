---
name: sap-bootstrap-system-context
description: |
  Do he thong ABAP that (qua MCP ADT — mcp-sap-adt) truoc khi scaffold, de lay quy uoc dat ten
  thuc te dang dung (khong doan) — package, prefix Z/Y sau ticket, Domain/Data Element da co the
  tai su dung, field admin convention rieng cua khach hang. Dung TRUOC sap-scaffold-rap/
  sap-scaffold-cds/sap-scaffold-cds-analytics/sap-cloud-dictionary khi chua biet quy uoc du an.
  KHONG dung khi da co system-context cache con moi (< 7 ngay) hoac du an da co convention ro rang
  trong TECHNICAL_SPEC.md.
when_to_use: |
  "kiem tra he thong dung quy uoc gi truoc khi tao", "co Domain nao dung duoc khong",
  "he thong nay dat ten Z the nao", "truoc khi scaffold can biet gi ve he thong khong".
argument-hint: "[ten package hoac module can kiem tra]"
model: sonnet
effort: medium
tools: [Read, Write, Glob, Bash]
---

# SAP Bootstrap System Context — Do he thong that truoc khi scaffold

## Tai sao can skill nay

[Bai hoc that tu chinh du an nay] Mot lan scaffold truoc do da dung sai ten data element admin (tu
bia `AB_CREATED_BY` thay vi ten chuan SAP `ABP_CREATION_USER`) va sai paradigm (XML DD01V kieu
on-premise thay vi source-code `define domain` cua ABAP Cloud) — vi suy tu kien thuc chung thay vi
kiem tra he thong/tai lieu that truoc. Skill nay bat buoc 1 buoc "do that" truoc khi cac skill
scaffold khac chay, giam rui ro doan sai lap lai.

## Khi nao dung

- ✅ Truoc khi chay `sap-scaffold-rap`/`sap-scaffold-cds`/`sap-scaffold-cds-analytics`/
  `sap-cloud-dictionary` lan dau tren 1 he thong/package chua quen.
- ✅ Nghi ngo quy uoc dat ten du an khac chuan chung (vd prefix theo ma khach hang thay vi `Z`).
- ❌ Da co cache system-context con moi (< 7 ngay, xem Buoc 4) — dung lai, khong do lai.
- ❌ Khong co MCP ADT nao duoc cau hinh — bao user cai 1 trong 3 lua chon o `reference/mcp-guides/mcp-sap-adt.md`
  truoc.

## Quy trinh

### Buoc 1: Xac nhan MCP ADT san sang

Kiem tra 1 trong 3 lua chon MCP tu `reference/mcp-guides/mcp-sap-adt.md` da ket noi (SAP Official / ARC-1 /
mcp-abap-adt / fr0ster fork). Neu chua — dung lai, huong dan user cai dat truoc khi tiep tuc.

### Buoc 2: Sample object Z*/Y* co san trong package muc tieu

Dung tool search cua MCP dang co (`SearchObjects`/`abap_search`/tuong duong) voi pattern `Z*`/`Y*`
gioi han theo package. Lay 5-10 object dai dien (uu tien Table, Domain, Data Element, CDS view da
activate) — **doc that** source/structure cua chung qua tool `Get*` tuong ung (khong doan tu ten).

### Buoc 3: Rut ra quy uoc thuc te

Doi chieu voi bang chuan trong `sap-clean-code` (`reference/abap-cloud-rules.md`), ghi nhan diem
**khac biet** neu co:

| Hang muc | Chuan chung (sap-clean-code) | Thuc te he thong nay |
|---|---|---|
| Prefix custom | `Z*` | ? |
| Field admin (created/changed) | `ABP_CREATION_USER`, `ABP_CREATION_TSTMPL`... | ? (du an co the da tu tao data element rieng) |
| Package structure | — | ? |
| Domain/Data Element tai su dung duoc | — | Liet ke object tim thay co the reference thay vi tao moi |

### Buoc 4: Ghi cache

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" cache/system-context
```

Ghi vao `<agent-home>/cache/system-context/<package-or-profile>.md` (duong dan tra ve tu lenh
tren), gom bang o Buoc 3 + timestamp. Cache **het han sau 7 ngay** — cac skill scaffold khac doc
file nay o Buoc 0 cua chung neu con moi, bo qua neu qua han hoac khong co.

## Luu y

- ⚠️ Day la **kiem tra tham khao**, khong thay the viec activate + xac nhan that trong ADT (skill
  `sap-verification-before-completion` van ap dung day du, khong duoc bo qua).
- ⚠️ Neu he thong khong co object Z*/Y* nao (du an moi tinh, package trong) — bao user, dung chuan
  chung (`sap-clean-code`) thay vi bia ra "quy uoc thuc te" tu 0 object mau.
- 🔗 Buoc tiep theo: `sap-scaffold-rap`, `sap-scaffold-cds`, `sap-scaffold-cds-analytics`,
  `sap-cloud-dictionary` — cac skill nay nen doc cache o day lam Buoc 0 neu con moi.
- 🔗 Dung chung MCP da cau hinh o `reference/mcp-guides/mcp-sap-adt.md`.
