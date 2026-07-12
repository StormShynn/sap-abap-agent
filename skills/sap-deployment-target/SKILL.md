---
name: sap-deployment-target
description: |
  Xac dinh package deploy tren he thong that + rao chan an toan (KHONG bao gio tao/sua/xoa object
  ngoai Z/Y hoac ngoai package da xac nhan) truoc khi scaffold. Hoi user package co san hay tao moi
  package Z rieng cho ticket, gate lai moi buoc can thao tac thu cong bang cau hoi xac nhan.
  Dung SAU sap-write-technical-spec, TRUOC sap-scaffold-rap/sap-scaffold-cds/
  sap-scaffold-cds-analytics/sap-cloud-dictionary.
  KHONG dung neu TECHNICAL_SPEC.md da co muc "Package deploy" ghi san va con hieu luc.
when_to_use: |
  "deploy vao package nao", "tao package moi cho ticket nay", "chua biet package tren he thong that",
  "xac nhan truoc khi tao object that tren he thong", "can thao tac thu cong gi truoc khi tiep tuc".
argument-hint: "[ten ticket]"
model: sonnet
effort: medium
tools: [Read, Write, Bash]
---

# SAP Deployment Target — Xac dinh package + rao chan an toan

## Khi nao dung

- ✅ Sau `sap-write-technical-spec` (da co TECHNICAL_SPEC.md), TRUOC khi chay bat ky skill tao
  object nao (`sap-cloud-dictionary`, `sap-scaffold-rap`, `sap-scaffold-cds`,
  `sap-scaffold-cds-analytics`).
- ✅ Chua biet deploy vao package nao tren he thong that.
- ❌ TECHNICAL_SPEC.md da co muc "Package deploy" ghi san va con hieu luc — dung lai, khong hoi lai.

## Quy trinh

### Buoc 1: Hoi user package deploy

Hoi thang, KHONG tu doan:

> "Ticket nay se tao object tren package nao? (ten package co san trong he thong, hoac go 'tao
> moi' de toi de xuat 1 package Z rieng cho ticket nay)"

### Buoc 2a: Neu user cho ten package co san — xac minh that

- Dung MCP ADT (`SearchObjects`/tuong duong, xem skill `mcp-sap-adt`) kiem tra package **ton tai
  that** va **thuoc namespace customer** (khong phai package chuan SAP — vd khong bat dau `SAP*`).
- Neu package KHONG ton tai hoac la package chuan SAP -> BAO user, KHONG tu tao/tu doi huong sang
  package khac, hoi lai ten khac.
- Neu hop le -> ghi vao TECHNICAL_SPEC.md muc "Package deploy", tiep tuc scaffold.

### Buoc 2b: Neu user chua co / muon tao moi

1. De xuat ten package theo quy uoc `sap-clean-code` (prefix `Z`, vd `ZTICKET_<ma-ticket>` hoac
   `Z<MODULE>_<TICKET>`), kem mo ta ngan (mo ta ticket).
2. **Hoi xac nhan ro rang** truoc khi tao that: "Tao package `<ten de xuat>` — '<mo ta>' — xac
   nhan? (co/khong/doi ten khac)". CHI tao sau khi user xac nhan — KHONG tu tao package ma khong
   hoi.
3. Sau khi user xac nhan -> tao qua MCP ADT (neu MCP dang dung ho tro tao package) hoac huong dan
   user tu tao thu cong trong ADT (New -> ABAP Package), ghi ten package vao TECHNICAL_SPEC.md.

### Buoc 3: Rao chan an toan (ap dung xuyen suot tu day den sap-finish-ticket)

- **TUYET DOI KHONG** tao/sua/xoa object **ngoai namespace `Z`/`Y`** hoac **ngoai package da xac
  nhan o Buoc 2** — ke ca khi user yeu cau, PHAI hoi lai ro rang neu 1 yeu cau co ve dung cham toi
  object chuan SAP hoac package khac: *"Yeu cau nay dung cham object `<ten>` khong thuoc Z/Y hoac
  nam ngoai package da xac nhan — ban co chac muon lam vay va co quyen thuc hien khong?"*
- **TUYET DOI KHONG xoa/sua object o package Z/Y khac** (vd cua team/ticket khac) ma khong hoi lai
  — pham vi mac dinh la CHI package da xac nhan o Buoc 2 cho ticket dang lam.
- **Doc/SELECT/association toi object khac package hoac released API van OK** (day la cach dung
  chuan cua ABAP Cloud) — rao chan chi ap dung cho hanh dong **tao moi/sua/xoa**, khong ap dung
  cho doc du lieu qua released API/CDS.
- **Backstop ky thuat**: `hooks/zy_namespace_guard.py` (PreToolUse) tu dong chan cac tool goi
  `*create*/*update*/*delete*` DDIC/CDS/RAP (vd `sap_create_table`, `CreateDomain`...) neu tham
  so ten khong bat dau `Z`/`Y`/`/namespace/` — day la lop bao ve ky thuat bo sung, KHONG thay the
  ky luat hoi user o tren (hook fail-open khi khong chac chan, van can lam dung Buoc 1-3).

### Buoc 4: Khi co buoc bat buoc thu cong (khong tu dong hoa duoc qua MCP)

Vi du: approve transport qua GUI, nhap credential that, click Activate trong Eclipse khi khong co
MCP ADT ket noi, cai extension, dang nhap OAuth popup...

1. Dung lai, mo ta **chinh xac** thao tac user can lam (tung buoc, ro rang, khong mo ho).
2. Hoi: *"Ban da lam xong buoc tren chua? (co / chua / gap loi — mo ta loi)"*.
3. **CHI tiep tuc** buoc tu dong hoa tiep theo SAU KHI user xac nhan "co"/"xong". Neu user bao loi
   -> dung lai xu ly loi do, KHONG tu doan da xong roi lam tiep buoc sau.

## Luu y

- ⚠️ Neu he thong da co package rieng cho module/ticket tuong tu truoc do (phat hien qua
  `sap-bootstrap-system-context`) — de xuat tai su dung package do thay vi tao moi, tranh phinh so
  luong package khong can thiet.
- 💡 Muc tieu tong the: giam thao tac thu cong lap lai cho user (hoi 1 lan, ghi lai, tai su dung
  xuyen suot pipeline) nhung KHONG duoc tu y hanh dong khi chua co xac nhan cho nhung viec anh
  huong that len he thong (tao package, tao object, dung cham object ngoai pham vi).
- 🔗 Ket qua (package + rao chan) ghi vao TECHNICAL_SPEC.md de `sap-scaffold-rap`/
  `sap-scaffold-cds`/`sap-scaffold-cds-analytics`/`sap-cloud-dictionary` dung lai, khong hoi lai
  tu dau.
- 🔗 `sap-finish-ticket` Buoc 5 (Transport check) doi chieu lai dung package da xac nhan o day.
- 🔗 Dung chung nguyen tac voi `sap-verification-before-completion` (bang chung chay that) va
  `sap-extensibility` (bac thang extensibility — KHONG bao gio de xuat sua duoc core).
