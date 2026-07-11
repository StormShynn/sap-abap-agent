---
name: sap-context-module-routing
description: |
  Pattern 2-layer cho reference/modules: tach thanh CORE (luôn load khi dispatch module) + DEEP
  (chi load khi agent can chi tiet SSCUI/API/Fiori/gotcha). Giam context token khi 18 module
  consultant duoc dispatch song song (sap-ask-consultant).
  Dung khi refactor reference/modules/sap-[module]-cloud/SKILL.md hien tai (da co full content)
  thanh 2 file: SKILL.md (core) + deep/SKILL.md (full cu).
  KHONG dung cho module moi chua co content (viet core truc tiep tu dau).
when_to_use: |
  "tach module thanh core+deep", "context module consultant dang phinh",
  "refactor reference module FI/MM/SD sang 2 layer".
argument-hint: "[ten-module]"
model: haiku
effort: low
---

# SAP Context Module Routing - 2-layer cho reference modules

## Ly do

Hien tai 18 module consultant (`sap-*-consultant-cloud`) moi agent reference 1 file
`reference/modules/sap-<m>-cloud/SKILL.md`. File nay thuong 100-400 dong chua SSCUI, Fiori app,
released API, extensibility guidance, gotcha, nguon tham khao.

Khi `sap-ask-consultant` dispatch **song song nhieu module** (vd "cau hinh cost center va GL"
→ CO + FI), tong token nap vao context = tong cac SKILL.md. Routing discipline chi load full
SKILL.md theo agent, KHONG the biet agent nao can full, agent nao chi can 1 dong summary.

Pattern 2-layer giai quyet:
- **CORE**: ~15-30 dong, chi chua diem ky thuat bat buoc nho + route map den DEEP. Luon load.
- **DEEP**: file goc, full content. Chi load khi agent can chi tiet cu the.

## Cau truc

```
reference/modules/sap-<m>-cloud/
├── SKILL.md        # CORE - luôn load khi agent duoc dispatch
└── deep/
    └── SKILL.md    # DEEP - load khi can tra cuu chi tiet
```

## Quy trinh tach 1 module (vi du: FI)

### Buoc 1: Xac dinh diem ky thuat bat buoc nho (CORE §1)

Tu `deep/SKILL.md`, rut trich 3-7 diem ma consultant FI can nho NGAY khi nhan cau hoi (truoc khi
search SAP Help / API Hub). Vi du:
- Universal Journal (ACDOCA) la GL duy nhat
- Business Partner la model duy nhat cho customer/supplier
- Ledger quan trong cho closing
- Moi doc/ghi deu qua released API/CDS view API

### Buoc 2: Route map (CORE §2)

Bang mapping tu "loai cau hoi user" → "section cua DEEP can doc". Day la noi agent chon
section can load thay vi doc full DEEP:

| Cau hoi user | Di den |
|---|---|
| "hach toan GL" | deep/SKILL.md §2 (Fiori) + §3 (API) |
| "them field" | deep/SKILL.md §4 (extensibility) |
| "dong so" | deep/SKILL.md §1 (Ledger) |

### Buoc 3: Lenh goi (CORE §3)

Agent duoc chi dinh load `deep/SKILL.md` nhu the nao:
1. Doc `deep/SKILL.md` voi line range (dung `Grep` de vi tri section).
2. Cross-check release tren `api.sap.com` neu can.
3. Ap dung skill khac truoc khi de xuat (vd `sap-extensibility` bac thang).

### Buoc 4: Tich hop (CORE §4)

Liet ke cac skill lien quan (`sap-extensibility`, `sap-clean-code`, `sap-docs-researcher`,
`sap-cds-kb`) de agent biet phoi hop.

### Buoc 5: Move file cu + ghi file moi

```powershell
Move-Item 'reference/modules/sap-<m>-cloud/SKILL.md' 'reference/modules/sap-<m>-cloud/deep/SKILL.md' -Force
# Tao file core moi
```

## Vi du FI (da trien khai)

`reference/modules/sap-fi-cloud/`:
```
├── SKILL.md        # 2.4 KB - CORE (route map + diem ky thuat)
└── deep/
    └── SKILL.md    # 5.3 KB - DEEP (full cu: SSCUI, Fiori app, API, gotcha)
```

Agent `sap-fi-consultant-cloud` (system prompt skills: `sap-fi-cloud`) load core (~20 dong), chi
load deep khi user hoi cu the ve SSCUI/API/Fiori.

## Checklist khi tach 1 module moi

- [ ] CORE khong qua 30 dong (~2KB) — neu dai hon, tach them phan vao DEEP.
- [ ] Route map phu het cac loai cau hoi pho bien (test bang 5-10 cau hoi mau cua module).
- [ ] Khong co thong tin trung lap giua CORE va DEEP (CORE chi la index, DEEP moi la detail).
- [ ] Tu khoa nhay cam (released API, SSCUI ID, Fiori app ID) khong xuat hien trong CORE - de agent khong "tra loi tu CORE" ma phai load DEEP.
- [ ] Agent definition da duoc kiem tra: van tro den `skills: [sap-<m>-cloud, ...]` (khong can doi).

## Lợi ich

- **Token khi dispatch song song 3 module**: giam ~60-70% (vi moi module chi load core).
- **Agent khong "tra loi tu CORE"** nham (vi CORE khong chua thong tin co the tra loi sai).
- **Backwards compatible**: DEEP file giu nguyen ten `SKILL.md`, agent van doc duoc bang `Read`.
- **De tach them**: 17 module con lai ap dung pattern giong FI.

## Tich hop

- Skill `sap-ask-consultant` - hien khong biet ve 2-layer, can update o Tier 2 tiep theo de
  routing engine chi dispatch core cho cac module da tach.
- Skill `sap-routing-discipline` - co the bo sung rule: "neu module chua tach, canh bao context
  load full".

## Luu y

- ⚠️ KHONG tu y sua DEEP file khi tach — chi move + ghi CORE moi.
- 💡 Ap dung lan luot cho 17 module con lai (uu tien: FI, MM, SD, CO vi hay duoc dispatch).
- 🔗 Track progress tach module trong `LEARNING_PROGRESS.md` (skill `sap-daily-learner`).