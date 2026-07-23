---
name: sap-service-type-context
description: |
  Xac dinh he thong dang lam viec la s4hc_(private) / s4hc_(public) / btp / onprem BANG CACH
  doc profiles/<id>/config.json cua sap-btp-agent (offline, khong goi MCP, khong dong secret)
  truoc khi tra loi cau hoi bi anh huong boi edition: doc du lieu (CDS/API released vs SELECT
  bang truc tiep), extensibility (SSCUI/Key User vs classic SPRO/BAdI), cu phap ABAP Cloud bi
  cam, ATC variant. Hoi user xac nhan neu chua xac dinh duoc (config chua co / gia tri mac dinh
  chua xac nhan). Dung TRUOC sap-ask-consultant/sap-extensibility/sap-clean-code/sap-abap-sql
  khi edition chua ro trong phien nay.
  KHONG dung de xac dinh package deploy (dung sap-deployment-target) hay quy uoc dat ten thuc
  te (dung sap-bootstrap-system-context) - day la truc khac (edition, khong phai package/naming).
when_to_use: |
  "he thong nay la private hay public edition", "extensibility the nao tren onprem",
  "co SELECT truc tiep bang duoc khong", "he thong dang connect la gi",
  truoc khi tra loi bat ky cau hoi nao anh huong boi edition ma chua biet trong phien hien tai.
argument-hint: "(khong can tham so - tu doc profile active)"
model: haiku
effort: low
tools: [Bash, Read]
---

# SAP Service Type Context — Xac dinh edition truoc khi tra loi

## Tai sao can skill nay

[Xem chi tiet dieu tra: cac skill "dat chinh sach" cua plugin nay (`sap-ask-consultant`,
`sap-extensibility`, `sap-clean-code`, `sap-abap-sql`) truoc gio deu viet cung cho **S/4HANA
Cloud Public Edition**, khong rẽ nhanh theo edition — trong khi ket noi MCP (`sap-btp-agent`)
tu 2026-07 da hoi va luu san field `service` theo taxonomy 4 nhanh
(`s4hc_(private)` / `s4hc_(public)` / `btp` / `onprem`) nhung khong skill nao doc lai gia tri
do. He qua: du he thong that la Private Edition/on-premise, cau tra loi van mac dinh theo rang
buoc Public Edition (chi CDS/API released, khong SELECT bang truc tiep...) hoac nguoc lai tuy
tinh huong — sai ngu canh theo ca 2 huong deu anh huong truc tiep den chat luong ket qua dua ra.]

## Khi nao dung

- ✅ Truoc khi tra loi cau hoi dung cham: doc du lieu (SELECT bang chuan vs CDS/API released),
  extensibility (SSCUI/Key User vs SPRO/BAdI classic), cu phap ABAP Cloud bi cam, ATC variant,
  landscape 2-system/3-system — ma **chua biet edition trong phien hien tai**.
- ✅ User hoi thang "he thong nay la private/public/btp/onprem".
- ❌ Da xac dinh edition trong phien nay roi (da hoi/da doc config 1 lan) — dung lai, dung ket
  qua cu, KHONG hoi lai hay chay lai script.
- ❌ Can biet **package** deploy tren he thong that -> dung `sap-deployment-target`.
- ❌ Can biet **quy uoc dat ten thuc te** (Domain/Data Element tai su dung duoc) -> dung
  `sap-bootstrap-system-context`. Skill do co the chay **sau** skill nay (biet edition truoc,
  do quy uoc thuc te sau).

## Quy trinh

### Buoc 1: Da biet trong phien nay chua?

Neu cau hoi truoc do trong CUNG phien da xac dinh edition (tu Buoc 2/3 duoi day) — dung ket
qua cu, khong lam lai tu dau.

### Buoc 2: Doc offline tu config.json (khong goi MCP)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/detect_service_type.py"
```

Tra ve JSON `{profile, service, source, configPath, note}`. Script chi doc
`profiles/<id>/config.json` cua `sap-btp-agent` (field khong nhay cam) — **khong** goi MCP,
**khong** dong vao `secrets.json`.

### Buoc 3: Xu ly theo `source`

| `source` | Y nghia | Hanh dong |
|---|---|---|
| `config` | Co gia tri `service` da duoc user xac nhan luc `sap-btp-agent setup` | Dung thang, thong bao ngan cho user (vd "Dang lam viec tren **s4hc_(public)** — profile `<id>`"), **KHONG hoi lai** |
| `config_default` | File config ton tai nhung thieu/sai field `service` (chua tung duoc xac nhan that) | Hoi lai user xac nhan truoc khi dung |
| `not_configured` | Khong co profile nao (chua chay `sap-btp-agent setup`, hoac dung MCP ADT khac/workflow abapgit-local thuan) | Hoi thang user, **giu nguyen taxonomy 4 nhanh**: *"He thong dang lam viec la s4hc_(private) / s4hc_(public) / btp / onprem?"* |

Neu co **nhieu profile** (`sap_list_profiles`) va cau hoi khong ro dang noi ve he thong nao —
hoi ro profile nao truoc khi dung ket qua cua profile active mac dinh.

**Khong ghi de** ket qua hoi duoc (khi `not_configured`/`config_default`) vao lai
`profiles/<id>/config.json` that — day la du lieu KET NOI that su cua `sap-btp-agent`, khong
phai nhan dinh cua 1 cau tra loi hoi thoai; sai o day co the anh huong hanh vi MCP that. Chi
ghi nho trong ngu canh phien hien tai.

### Buoc 4: Ap dung ket qua

| Khia canh | `s4hc_(public)` | `s4hc_(private)` | `onprem` | `btp` |
|---|---|---|---|---|
| Doc du lieu | Chi released CDS/API | Uu tien released, dev on-stack co the sau hon | SELECT bang chuan truc tiep binh thuong | Khong dung core truc tiep — luon goi qua API du core la edition nao |
| Extensibility | SSCUI + Key User + Developer(3-system) + side-by-side (`sap-extensibility`) | Ladder tuong tu nhung on-stack rong hon, co the con BAdI/exit classic tuy compat scope | Toan bo classic: SPRO/IMG, user-exit, BAdI classic, enhancement point | Chi co side-by-side (chinh no la 1 bac trong ladder) |
| Cu phap ABAP Cloud bi cam (`sap-extensibility` §4) | Bat buoc | Tuy compat scope du an chon | Khong ap dung tru khi tu nguyen theo | Bat buoc |
| Landscape mac dinh | 2-system | Thuong 3-system tro len | Thuong 3-system tro len | Rieng, khong ap dung |
| ATC / released-API check | Bat buoc strict | Co nhung it strict hon | Khong can tru khi muon cloud-ready | Bat buoc |
| `sap-ask-consultant` (SSCUI/Fiori app cu the) | Dung | SSCUI van co nhung nhieu phan dung classic transaction/SPRO song song | Da so la transaction code/SPRO, khong phai SSCUI | Khong ap dung (khong co UI nghiep vu rieng) |

[Chua xac minh song tung dong trong bang tren qua nguon SAP Help/Community cho phien ban
release hien tai — dua tren kien truc tong quan da biet, giong cach `sap-extensibility` tu ghi
chu o dau file no. Luon nhac user xac minh lai chi tiet SSCUI/API/compat scope cu the truoc khi
dua vao san xuat, dac biet voi Private Edition (compat scope tuy du an chon, khong co 1 quy tac
chung duy nhat).]

**Khong doi theo edition**: quy uoc namespace `Z`/`Y` — day la quy dinh cua SAP ap dung cho
**moi** edition (ke ca on-premise), khong phai dac thu ABAP Cloud. Tranh forking nham cho nay
khi ap dung bang tren.

## Luu y

- ⚠️ Ket qua o day chi la **dinh huong cau tra loi**, khong thay the viec verify that qua MCP
  (vd extensibility/API thuc su co dung duoc hay khong tren he thong that) — ap dung chung
  nguyen tac voi `sap-verification-before-completion`.
- ⚠️ `source: config` dua tren gia tri user da nhap luc `sap-btp-agent setup` — co the sai neu
  user nhap nham luc do. Neu cau tra loi dua ra co ve mau thuan voi thuc te he thong (vd bao
  "SELECT truc tiep duoc" nhung ATC that lai reject), nhac user kiem tra lai
  `sap-btp-agent profiles show`.
- 💡 Doc offline (Buoc 2) re hon va dang tin cay hon suy tu `sap_ping` (khong can he thong
  dang song, khong round-trip mang) — chi hoi user khi thuc su khong co du lieu.
- 🔗 `sap-routing-discipline` (R9) tro toi skill nay truoc khi tra loi cau hoi anh huong boi
  edition.
- 🔗 `sap-ask-consultant`, `sap-extensibility`, `sap-clean-code`, `sap-abap-sql` doc ket qua
  skill nay de rẽ nhanh/canh bao thay vi mac dinh Public Edition.
- 🔗 Khac truc voi `sap-deployment-target` (package deploy) va `sap-bootstrap-system-context`
  (quy uoc dat ten thuc te) — 3 skill co the chay noi tiep: skill nay (edition) ->
  `sap-bootstrap-system-context` (quy uoc that) -> `sap-deployment-target` (package).
