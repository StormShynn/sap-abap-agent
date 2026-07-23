# `released-objects-index.json` — Tra cứu released objects S/4HANA Cloud Public

Index pre-computed của **toàn bộ 37,918 object** (released/deprecated/notToBeReleased)
được SAP công bố cho ABAP Cloud development, lấy từ [SAP/abap-atc-cr-cv-s4hc](https://github.com/SAP/abap-atc-cr-cv-s4hc)
(Apache-2.0).

Phục vụ verify câu hỏi: **"Object X có released cho ABAP Cloud dev trên S/4HANA Cloud Public không?"**
mà KHÔNG cần MCP / Eclipse ADT — chỉ 1 dict lookup ≈ 100 token.

## Sinh / refresh

```bash
# Lần đầu (auto download 12 MB raw từ SAP GitHub)
python scripts/build_released_objects_index.py

# Refresh khi SAP push release mới (sau ~6 tháng)
python scripts/build_released_objects_index.py --refresh
```

Raw data lưu `scripts/data/` (gitignored). Index compact (~5 MB) commit vào git.

## Khi nào dùng

| Câu hỏi | Trả lời |
|---|---|
| FS gọi view `I_JournalEntry`, có released ở 2602 không? | Lookup `DDLS:I_JOURNALENTRY` → `state=released` |
| Class `CL_BCS` còn dùng được không? | Lookup `CLAS:CL_BCS` → `state=notToBeReleased`, `succ:[CL_BCS_MAIL_MESSAGE]` → dùng successor |
| `I_COMPANYCODE` thuộc application component nào? | `ac=FI-GL-GL-N-2CL` → phân hệ FI-GL |
| BAdI để extend journal entry, BAdI nào released? | Lookup `BADI_DEF:<name>` |
| BO interface (RAP) tạo material doc? | Lookup `BDEF:I_MATERIALDOCUMENT*` |

## Format

```jsonc
{
  "schema_version": 1,
  "generated_at": "2026-06-30",
  "source": {
    "repo": "SAP/abap-atc-cr-cv-s4hc",
    "url": "https://github.com/SAP/abap-atc-cr-cv-s4hc",
    "license": "Apache-2.0",
    "files": ["src/objectReleaseInfoLatest.json", "src/objectClassifications_SAP.json"]
  },
  "stats": {
    "total_objects": 37918,
    "by_state": { "released": 33503, "notToBeReleased": 653, "deprecated": 519 },
    "by_type_top10": { "TABL": 11404, "DDLS": 7566, ... },
    "classic_api_merged": 3968,
    "classic_api_added": 4043
  },

  "objects": {
    // Key format: "<TADIR_TYPE>:<OBJECT_NAME_UPPERCASE>"
    "DDLS:I_COMPANYCODE": {
      "state": "released",            // released | deprecated | notToBeReleased | unknown
      "ot": "CDS_STOB",                // optional: detail object type (chỉ có nếu khác TADIR)
      "ac": "FI-GL-GL-N-2CL",          // applicationComponent (= phân hệ SAP)
      "sc": "SAPSCORE",                // softwareComponent
      "sc_class": "oneObject",         // chỉ có nếu deprecated: oneObject | severalObjects | none
      "succ": [                         // chỉ có nếu deprecated/notToBeReleased với replacement
        { "type": "DDLS", "name": "I_NEW_VIEW" }
      ],
      "classic_api": true,             // optional flag: object cũ trong CLASSIC API list
      "internal_api": true             // optional: SAP-internal, không cho dev
    }
  },

  "name_index": {
    // Reverse: name → list of full keys (name không kèm type)
    "I_COMPANYCODE": ["DDLS:I_COMPANYCODE"]
  }
}
```

## Pattern lookup (Python / CLI)

**Cách 1 — CLI helper `acme_lookup.py`** (recommended cho agent):

```bash
python scripts/acme_lookup.py I_CompanyCode            # auto-probe cả 2 index
python scripts/acme_lookup.py I_COMPANYCODE --type DDLS  # filter theo TADIR type
python scripts/acme_lookup.py I_JOURNAL --search        # substring search
```

**Cách 2 — Inline Python** (1 dòng trong agent):

```python
import json
idx = json.load(open("docs/sap-knowledge/released-objects-index.json", encoding="utf-8"))

# Verify CDS view released?
key = f"DDLS:{name.upper()}"
rec = idx["objects"].get(key)
if rec is None:
    print(f"{name}: NOT in catalog — likely NOT released or doesn't exist")
elif rec["state"] == "released":
    print(f"{name}: ✅ released, application={rec.get('ac','?')}")
elif rec["state"] == "deprecated":
    succs = [s['name'] for s in rec.get('succ', [])]
    print(f"{name}: ⚠ deprecated, use: {succs}")
else:
    print(f"{name}: ❌ {rec['state']}")
```

## Convention quan trọng — UPPERCASE

SAP TADIR (table registry) lưu mọi tên object dạng **UPPERCASE**. Lookup
phải `.upper()` tên trước khi tra. CLI `acme_lookup.py` tự normalize; pattern inline trên cũng làm.

Tên SAP help docs hiển thị CamelCase (`I_CompanyCode`) là cho người đọc — internal vẫn là `I_COMPANYCODE`.

## TADIR types phổ biến

| TADIR | Tên | Số lượng | Khi nào agent quan tâm |
|---|---|---:|---|
| `DDLS` | CDS DDL source view | 7,566 | Mọi FS đọc dữ liệu SAP standard |
| `TABL` | DDIC table | 11,404 | Hiếm — dùng CDS, không read trực tiếp table |
| `DTEL` | Data element | 5,463 | Khi tạo Z table custom cần reference type |
| `INTF` | Interface | 3,278 | Class implements interface |
| `TTYP` | Table type | 2,462 | Type tham số method |
| `CLAS` | ABAP class | 1,448 | Verify class released, gọi static method |
| `BADI_DEF` | BAdI definition | 1,206 | Extend SAP standard logic |
| `BDEF` | Behavior definition | 311 | RAP — tạo chứng từ qua EML |
| `DOMA` | Domain | 205 | Z data element cần reference domain |
| `FUNC` | Function module | 368 | Legacy — ưu tiên class/API |

## Giới hạn (cần biết)

- Cảnh báo **không có cột "release contract"** (C0/C1/C2/C3 — stable contract levels) trong file gốc.
  SAP công bố contract trong tài liệu riêng. Index này chỉ phân biệt: released / deprecated / notToBeReleased.
- File raw 9.8 MB cập nhật mỗi release SAP (~6 tháng). Re-run `--refresh` để đồng bộ.
- Không có **field-level info** (key fields của CDS, parameter list của method). Cần tra trên
  [api.sap.com](https://api.sap.com/) hoặc Eclipse ADT View Browser cho chi tiết schema.
- Custom Z* / ACME objects KHÔNG nằm ở đây — đó là [pub-naf-index.json](pub-naf-index-README.md).

## Quan hệ với index khác

```
Agent câu hỏi "Object X dùng được không?"
  ├─ Z* / ZI_ACME_* / ZCL_* → pub-naf-index.json (project-internal, 333 views)
  └─ I_*, C_*, P_*, CL_*, BD_* → released-objects-index.json (SAP standard, 37,918 objects)

CLI acme_lookup.py probe CẢ 2 → trả full picture.
```
