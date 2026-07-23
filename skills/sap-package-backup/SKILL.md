---
name: sap-package-backup
description: |
  Backup source ABAP toan bo package Z* (de quy sub-package) va cac custom
  field/custom logic YY1* (Key User Extensibility) qua ADT REST, dung
  SapClient da co san trong sap-btp-agent - lay cam hung tu co che serialize
  cua abapGit (dat ten file "<ten>.<loai>.<phan>", thu muc theo package
  hierarchy) de ban backup de doc/diff bang git. KHONG PHAI 1 repo abapGit
  day du round-trip - chi doc-ra-file, khong sinh du XML metadata de abapGit
  thuc su pull nguoc lai duoc.
  Dung khi user muon "backup package Z", "sao luu custom code truoc khi sua",
  "export toan bo enhancement YY1", hoac can 1 snapshot code hien tai truoc
  1 thay doi lon/transport rui ro.
when_to_use: |
  "backup package Z...", "sao luu code truoc khi sua", "export enhancement
  YY1", "snapshot custom code", "backup custom field truoc khi xoa".
argument-hint: "[--packages Z1,Z2] [--include-yy1] [--inspect | --dry-run]"
effort: high
model: sonnet
tools: [Bash, Read]
---

# SAP Package Backup — Backup Z*/YY1 qua ADT REST (lay cam hung abapGit)

## Khi nao dung

- User can 1 ban backup source code (class/CDS/interface/table...) cua 1 hay
  nhieu package Z* **truoc khi** sua lon, chay transport, hoac xoa custom
  field/enhancement YY1*.
- User muon 1 snapshot dinh ky (thu cong) de doi chieu diff qua git, KHONG
  can cai abapGit thuc trong he thong SAP.
- **KHONG dung** skill nay de: tao object moi (dung `sap-cloud-dictionary`),
  migrate code (dung `sap-cloud-migration`), hay quan ly transport routing
  (ngoai pham vi plugin nay).

## Buoc 0 — luon lam truoc, KHONG bo qua

Day la thao tac **doc** (khong ghi/sua object SAP nao), nhung co the quet
nhieu object tren 1 he thong that — luon xac nhan pham vi voi user truoc:

1. Hoi ro **danh sach package Z\* goc** can backup (khong tu suy dien "toan
   bo he thong" tru khi user noi ro) — pham vi mo rong ra sub-package tu dong
   qua de quy nodestructure, khong can user liet ke tung sub-package.
2. Neu day la lan dau chay tren 1 tenant/profile cu the trong phien nay, chay
   `--inspect` **truoc** (xem Buoc 1) — cau truc XML tra ve tu ADT nodestructure
   CHUA duoc script nay test song, `--inspect` la buoc kiem tra re, an toan.
3. Xac nhan **noi ghi output** (mac dinh an toan — xem muc "Noi luu output").

## Buoc 1 — Inspect (kiem tra parser truoc khi tin tuong full-scan)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/backup_packages.py" \
  --packages <PACKAGE_GOC> --inspect
```

Chi dump raw response cua `list_packages(<PACKAGE_GOC>)` ra file
`_inspect_<package>.raw.txt` trong out dir, khong ghi backup that. In ra so
object/sub-package parser doc duoc. Neu ra `0 object, 0 sub-package` cho 1
package **chac chan co object** — mo file raw len doc, doi chieu voi ham
`parse_nodestructure()` trong script, va **bao lai cho nguoi dung** truoc khi
chay tiep (dung tu suy dien pham vi/format khac).

## Buoc 2 — Dry-run (xem truoc danh sach, chua goi read-source)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/backup_packages.py" \
  --packages ZFI_CUSTOM,ZSD_EXT --dry-run
```

In danh sach object se backup (package, loai, ten) — chua goi
`/source/main`, chua ghi file. Dung de user duyet lai pham vi truoc khi chay
that (dac biet khi so luong object lon tren tenant production).

## Buoc 3 — Backup that

```bash
# Chi Z* packages:
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/backup_packages.py" \
  --packages ZFI_CUSTOM,ZSD_EXT --label truoc-migration-fi

# Them ca custom field/logic YY1* (tim theo ten, ngoai pham vi --packages):
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/backup_packages.py" \
  --packages ZFI_CUSTOM --include-yy1 --yy1-pattern YY1
```

Sau khi chay xong, **doc file `_manifest.json`** trong out dir (in ra o cuoi
log) va tom tat lai cho user: so object OK/loi/bo qua, va **luon nhac lai**
noi dung mang `known_limitations` trong manifest (xem muc gioi han duoi day)
— dung bao "backup thanh cong 100%" neu manifest co object `error` hoac
`skipped_unsupported_type`.

## Noi luu output

Mac dinh: `<out dir cua sap-btp-agent>/backups/<label>_<timestamp>/` (thu
muc user home, **ngoai** repo git cua plugin nay — an toan mac dinh). Doi qua
`--out <duong-dan>`.

**Tuyet doi khong** dung `--out` tro vao trong repo `sap-abap-agent` (hoac bat
ky repo git nao se bi commit) — source code Z*/YY1 backup ra la **du lieu
khach hang that**, cung nguyen tac voi rule `tests/__Du_an` trong
`.gitignore` cua plugin nay (khong bao gio track du lieu khach hang thuc vao
git cua plugin). Script tu in canh bao ra stderr neu phat hien `--out` nam
trong repo nay, nhung van nen tu kiem tra truoc khi chay trong moi truong
khac.

Cau truc output (lay cam hung abapGit — xem muc "So sanh voi abapGit thuc"):

```
<label>_<timestamp>/
  _manifest.json                  <- tom tat: counts, loi, known_limitations
  <PACKAGE_GOC>/
    package.devc.xml              <- metadata package (raw ADT, best-effort)
    <ten_object>.<duoi_theo_loai> <- source (xem bang do tin cay duoi day)
    <ten_object>.<loai>.meta.json <- metadata tho tu nodestructure (OBJECT_TYPE, OBJECT_URI...)
    <SUB_PACKAGE>/...              <- de quy theo hierarchy that
  _yy1_enhancements/
    <ten_object>.<duoi_theo_loai>  <- object ten khop --yy1-pattern (--include-yy1)
```

## Do tin cay theo loai object

Script dispatch endpoint ADT REST rieng cho tung loai (KHONG dung
`sap_read_source` — tool do chi dung CLAS/PROG cho ca 2, sai path cho
INTF/DDLS/DDLX/DCLS/SRVD/DOMA/DTEL/TABL/BDEF). Muc do tin cay cua tung path
(quan trong — **luon noi ro cho user** khi bao cao ket qua, dung ngam dinh
tat ca deu "verified"):

| Loai | Path ADT | Do tin cay | Ghi chu |
|---|---|---|---|
| CLAS | `/sap/bc/adt/oo/classes` | **verified** | Cung path `sap_read_source` da dung thanh cong |
| INTF | `/sap/bc/adt/oo/interfaces` | high | Suy tu chieu tao (`dictionary.py`), chua tu verify chieu doc |
| DDLS | `/sap/bc/adt/ddic/ddl/sources` | high | nt |
| DDLX | `/sap/bc/adt/ddic/ddlx/sources` | high | nt |
| DCLS | `/sap/bc/adt/acm/dcl/sources` | high | nt |
| SRVD | `/sap/bc/adt/ddic/srvd/sources` | high | nt |
| BDEF | `/sap/bc/adt/bo/behaviordefinitions` | medium | Chinh buoc TAO BDEF cung chua xac nhan tren S/4HANA Cloud Public Edition |
| DOMA | `/sap/bc/adt/ddic/domains` | medium | abapGit thuc luu XML co cau truc (DD01V), khong phai DDL text — day la best-effort |
| DTEL | `/sap/bc/adt/ddic/dataelements` | medium | Tuong tu DOMA (DD04V) |
| TABL | `/sap/bc/adt/ddic/tables` | medium | Tuong tu DOMA (DD02V + field list) |
| SRVB | `/sap/bc/adt/businessservices/bindings` | medium | Khong co source — doc metadata truc tiep |
| PROG | `/sap/bc/adt/programs/programs` | low | Kien thuc ADT REST chung, chua co nguon nao trong repo nay xac nhan |
| MSAG, FUGR | — | khong ho tro | Chua xac dinh duoc endpoint doc — object loai nay bi bao `skipped_unsupported_type` |

## Gioi han da biet (luon nhac user, dung im lang bo qua)

1. **Cau truc XML/JSON tra ve tu nodestructure/quickSearch chua duoc test
   song** trong bat ky phien lam viec nao — ham parse trong script suy tu
   cau truc ADT pho bien, khong phai doc tu response that. Day la ly do
   Buoc 1 (`--inspect`) bat buoc lam truoc lan full-scan dau tien tren 1
   tenant moi.
2. **YY1 chi tim duoc phan "co TADIR entry"** (custom logic implementation
   class, CDS extend...) qua tim ten pattern (`quickSearch`) — **KHONG**
   backup duoc metadata "business context" cua app Fiori "Custom Fields and
   Logic" (nhan field, vi tri UI, custom Business Object) — phan do nam
   trong 1 repository rieng cua app, chua co tool/API nao trong MCP server
   nay doc duoc. Neu user can day du phan nay, noi ro gioi han va de xuat
   kiem tra thu cong qua app "Custom Fields and Logic" / "Extensibility" tren
   Fiori Launchpad.
3. **DOMA/DTEL/TABL/BDEF la best-effort** (do tin cay "medium") — xem bang
   tren.
4. **MSAG (Message Class) va FUGR (Function Group/Module) khong ho tro** —
   chua xac dinh duoc endpoint ADT REST doc cho 2 loai nay (xem
   `docs/sap-knowledge/abapgit-serialization-spec.md` muc MSAG — ngay abapGit
   thuc cung khong co API GHI message text qua ADT REST).

## So sanh voi abapGit thuc (nguon: docs.abapgit.org, xem Nguon tham khao)

| | abapGit thuc | Skill nay |
|---|---|---|
| Ten file | `<ten>.<loai>.<phan>.<ext>` (vd `.clas.locals_imp.abap`) | Tuong tu, don gian hoa — 1 file source + 1 file `.meta.json` |
| Package | `package.devc.xml` chi 3 field `CTEXT`/`LANGUAGE`/`MASTERLANG`, ten do folder quyet dinh | `package.devc.xml` = **raw** XML tu ADT (nhieu field hon, khong parse lai) |
| Metadata object (VSEOCLASS, DD02V...) | Sinh day du, co the round-trip pull lai vao SAP | **KHONG sinh** — chi co source text + JSON tho tu nodestructure |
| Muc tieu | Version control + deploy 2 chieu (push/pull) | Chi 1 chieu **doc-ra** — snapshot/backup, khong deploy lai duoc |

Neu can 1 ban backup **round-trip thuc su** (pull lai vao SAP qua abapGit
thuc), can dung abapGit thuc (cai trong he thong SAP) hoac tool sinh XML day
du theo `docs/sap-knowledge/abapgit-serialization-spec.md` — skill nay chi
phuc vu muc dich doc-luu-tham khao/diff, khong thay the abapGit thuc.

## Skill lien quan

- `sap-extensibility` — bac thang Key User Extensibility, giai thich YY1
  sinh ra tu dau (Custom Fields and Logic).
- `sap-key-user-toolkit` — thao tac tung buoc voi Custom Field/Custom Logic
  tren Fiori app (goc nhin key user, khong phai backup).
- `sap-cloud-dictionary` — chieu NGUOC lai (tao Domain/Data Element/Table
  moi qua ADT REST) — dung khi can TAO, khong phai backup.
- `sap-cloud-migration` — dung truoc khi migration code len cloud; backup
  (skill nay) nen chay truoc buoc Code Adaptation cua migration de co diem
  quay lui.

## Nguon tham khao

- [Folders & Files | abapGit Docs](https://docs.abapgit.org/user-guide/reference/folders-filenames.html)
- [File Naming and Formats | abapGit Docs](https://docs.abapgit.org/development-guide/serializers/file-formats.html)
- [Repository (.abapgit.xml) | abapGit Docs](https://docs.abapgit.org/user-guide/repo-settings/dot-abapgit.html)
- [Serializer Overview | abapGit Docs](https://docs.abapgit.org/development-guide/serializers/overview.html)
- `docs/sap-knowledge/abapgit-serialization-spec.md` — spec chi tiet field-by-field
  tung loai object (chieu nguoc — generate de abapGit thuc pull vao, nhung field
  list tai su dung duoc cho chieu doc).
- `reference/mcp-server/sap_btp_agent/tools/dictionary.py` — nguon xac nhan cac
  ADT REST path dung trong `TYPE_MAP` cua `backup_packages.py`.
