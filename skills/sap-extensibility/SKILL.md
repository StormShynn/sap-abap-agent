---
name: sap-extensibility
description: Huong dan extensibility & rang buoc ABAP Cloud theo tung service type SAP
  (s4hc_(private)/s4hc_(public)/btp/onprem) — §1-§6 chi tiet cho S/4HANA Cloud Public Edition,
  §8 tom tat khac biet cho 3 edition con lai. Dung khi user hoi nen dat custom logic o dau
  (SSCUI/Key User/side-by-side BTP/SPRO classic), co dung duoc BAdI/SPRO/table truc tiep khong,
  hoac gap loi cu phap ABAP Cloud (RAP, released API). Goi `sap-service-type-context` truoc
  neu chua biet edition trong phien nay.
when_to_use: |
  "custom logic nay nen dat o dau", "co dung SELECT truc tiep vao bang standard khong",
  "object chua released thi lam sao", "CALL SCREEN co dung duoc tren Cloud khong".
effort: medium
model: haiku
---

# SAP Extensibility & Rang buoc ABAP Cloud — theo tung Service Type

[Chua xac minh song tung chi tiet — kien truc tong quan da kiem chung qua SAP Help/Learning/Community
(xem muc Nguon tham khao cuoi file); ten SSCUI/scope item/Fiori app cu the thay doi theo tung ban
release quy (SAP ra 4 ban/nam: vd 2502/2505/2508/2511) nen luon nhac user xac minh lai truoc khi dua
vao san xuat.]

## Buoc 0: Xac dinh edition truoc khi ap dung bang duoi

Noi dung §1-§6 duoi day viet cho **`s4hc_(public)`** (S/4HANA Cloud Public Edition). Neu chua
biet he thong dang lam viec la edition nao trong phien nay, chay `sap-service-type-context`
truoc. Ket qua:

- `s4hc_(public)` -> dung nguyen §1-§6 nhu duoi.
- `s4hc_(private)` / `onprem` / `btp` -> xem **§8. Khac biet theo edition** o cuoi file de dieu
  chinh truoc khi tra loi — DUNG ap dung nguyen si rang buoc §1-§6 cho 3 edition nay (vd cam
  SELECT bang chuan chi dung tren `s4hc_(public)`/`btp`, khong dung tren `onprem`).

## 1. Cau hinh & truy cap he thong tren Public Cloud

- **Cau hinh** qua **SSCUI** (Self-Service Configuration UI), mo tu app Fiori **Manage Your Solution**.
- **Khong the truy cap bang truc tiep.** Moi thao tac du lieu di qua **released API** (OData V2/V4, CDS view "API") hoac Fiori app.
- **Mo rong** chi qua **Key User Extensibility** (Custom Fields & Logic, Custom Business Objects, Cloud BAdI — dung "ABAP for Key Users" don gian hoa) hoac **side-by-side tren BTP**.
- **Giao dien nguoi dung** toan bo la **Fiori app**.
- **Tich hop** chi qua **released API** — luon kiem tra tinh trang release/cloud-qualified tren `api.sap.com` truoc khi su dung 1 API/BAPI/Function Module bat ky.
- **Upgrade** theo **release quy bat buoc** (2502 → 2505 → 2508 → 2511...) — luon nhac user xac minh 1 SSCUI/app/API cu the co ton tai tren release hien tai khong.

## 2. Bac thang Extensibility (luon danh gia tu tren xuong)

Uu tien bac cao nhat phu hop yeu cau — cang xuong duoi cang phuc tap va cang nhieu thu phai tu bao tri:

1. **Cau hinh chuan qua SSCUI** — chi la 1 switch/setting SAP da co san.
2. **Key User Extensibility (in-app, khong can dev)**:
   - *Custom Fields and Logic* — them 1 field vao business object/report/Fiori UI chuan, co the kem logic don gian.
   - *Custom Business Objects* — tao 1 business object hoan toan moi (bang rieng, UI rieng, tu dong co OData API) ma khong can dev.
   - *Custom Logic (Cloud BAdI)* — key user dung BAdI SAP da release san (khong tu tao BAdI definition), viet logic bang cu phap rut gon ABAP for Key Users. Co che Cloud BAdI + goc nhin Developer: skill `sap-badi-enhancement`; thao tac tung buoc cho key user: skill `sap-key-user-toolkit` §3.2.
   - *Adaptation Transactions* — an/di chuyen/doi nhan field tren Fiori app co san.
3. **Developer Extensibility (on-stack)** — **chi co tren 3-system landscape**; dev ABAP ngay trong tenant dev cua he thong core (vi du: tao class implement 1 Cloud BAdI definition da released — xem skill `sap-badi-enhancement`), van chi dung released API/extension point, khong sua duoc object chuan.
4. **Side-by-side tren BTP** — he thong/runtime rieng (thuong la BTP ABAP Environment, dung RAP). Chi goi nguoc lai core qua released API — KHONG co extension point nao ma in-app chua co san.

**Nguyen tac fail-fast**: neu 1 yeu cau khong khop bac nao trong 4 bac tren — DUNG bia ra 1 cach lam khong ton tai. Xac dinh xem yeu cau thuc su thuoc bac nao va de xuat dung bac do; neu khong bac nao dap ung, noi thang la chua lam duoc.

## 3. Clean Core — khong phai tuy chon, ma la he qua bat buoc

Vi khong co cach nao sua duoc core, moi custom asset chi co the la (a) 1 artifact Key User nam trong tenant extension rieng, hoac (b) 1 app side-by-side goi qua released API. Nghia la:
- Moi de xuat dung theo bac thang o muc 2 **tu dong tuan thu Clean Core**.
- Loi thuong gap nhat khong phai la vi pham Clean Core, ma la **de xuat 1 thu khong ton tai tren Public Cloud** (1 BAdI, 1 bang truy cap truc tiep, 1 BAPI chua duoc release, 1 man hinh khong phai Fiori). Luon xac minh moi de xuat co thuc su kha thi tren Public Cloud truoc khi dua ra.

## 3b. Khi 1 object CAN DUNG nhung CHUA released — cay quyet dinh mitigation

Dung khi qua trinh sinh code/tim CDS nguon phat hien 1 view/BO/API can dung nhung **chua released**
hoac **khong ton tai** cho ABAP Cloud. DUNG dead-end bang cach ghi `[Unverified]` roi dung lai —
di theo cay quyet dinh nay (thu tu uu tien tren xuong):

```
Object X can dung nhung xac minh la KHONG released / khong ton tai
   │
   ├─① Co RELEASED ALTERNATIVE khong? (view/API khac tra ve cung du lieu)
   │      → tra cuu qua sap-docs-research / skill sap-cds-kb / agent consultant phan he
   │      → co → DUNG cai released. Xong.
   │
   ├─② Co STANDARD OData/SOAP API (whitelist Public Cloud) khong?
   │      → api.sap.com filter "SAP S/4HANA Cloud Public Edition" → tim API_* SRV
   │      → goi qua HTTP client + Communication Arrangement (KHONG can released ABAP object)
   │      → phu hop khi: BO EML khong du / can so chung tu ngay (late numbering) / action cross-LUW
   │
   ├─③ Chi can THEM FIELD / logic nho tren object standard?
   │      → Key User Extensibility (Custom Fields & Logic) / released BAdI enhancement spot
   │      → khong can code core (xem muc 2, bac 2 o tren)
   │
   └─④ Khong co duong nao o tren
          → [Unverified] + ghi vao INTAKE muc 6 (cau hoi can lam ro) + escalate cho KH/tech lead.
          → TUYET DOI KHONG: bia ten released, dung object on-prem, direct SQL vao bang standard SAP.
```

**Bang mitigation nhanh:**

| Tinh huong | Lam gi | Ghi chu |
|---|---|---|
| CDS view can chua released | Tim view released tuong duong; hoac build ZI_* select from view released khac | KHONG select from view chua released |
| BO interface (EML) chua released/thieu | Standard OData API (②) hoac released BO khac | — |
| BO EML released nhung **late numbering** (khong lay duoc so trong handler) | **OData API** commit LUW rieng → tra so ngay | Cam COMMIT ENTITIES trong behavior; EML MODIFY chi co `%pid` |
| Object on-prem quen thuoc (BAPI/table DDIC raw) | Released CDS/API tuong duong | Object on-prem = ATC reject tren Public Cloud |
| Chi them field vao chung tu standard | Key User Custom Fields, hoac released BAdI | Khong can dev core |
| Khong co gi | `[Unverified]` + escalate KH | Dung bia, dung cat goc |

Xem them: skill `sap-atc-review` (bang anti-rationalization, dong R7 "Object chua released") va
skill `sap-write-technical-spec` (buoc 3 — chon CDS/API nguon).

## 4. Rang buoc cu phap ABAP Cloud (khi code thuc su chay trong side-by-side / on-stack)

Cu phap bi cam tren ABAP Cloud va cach thay the:

| Nhom | Cu phap KHONG duoc dung | Dung thay bang |
|---|---|---|
| File system | `OPEN/CLOSE/READ/GET DATASET` | Khong co |
| DB access | `EXEC SQL`, `SELECT ... CLIENT SPECIFIED` | Khong co |
| Man hinh | Dynpro (`CALL SCREEN`, `PF-STATUS`...) | Fiori Elements / RAP |
| Enhancement | `ENHANCEMENT-POINT` | Key User / Developer Extensibility |
| Event block | `LOAD-OF-PROGRAM`, `START-OF-SELECTION`... | Viet thanh Class Method / Function Module |
| Debug | `BREAK-POINT` | ADT Debugging |
| Bien he thong ngay/gio | `sy-datum`, `sy-uzeit` | `cl_abap_context_info=>get_system_date/time( )` |
| Song song hoa | `CALL FUNCTION ... STARTING NEW TASK` | `CL_ABAP_PARALLEL` |
| So hoc | `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE` | `+`, `-`, `*`, `/` (toan tu chuan) |
| Bao cao doc lap | Report dung event block | Class implement `if_oo_adt_classrun`, ghi qua `out->write( )` |

Vi du class toi thieu hop le tren ABAP Cloud:

```ABAP
CLASS ztest_class DEFINITION
  PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS ztest_class IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    out->write( 'Hello world!' ).
  ENDMETHOD.
ENDCLASS.
```

**Danh sach tren chi la rut gon** — xem bang day du (arithmetic, calendar, XML, Excel upload, batch
job, lock, number range...) tai SAP Help `xco_cp` libraries truoc khi khang dinh 1 API co replacement
hay khong.

## 5. Landscape 2-system vs 3-system

- **2-system** (da so khach hang Public Cloud): Starter/Customizing tenant + Production tenant. Chi co Key User + side-by-side.
- **3-system**: co them Development tenant → mo khoa Developer (on-stack) Extensibility ngay trong core.
- Khi khong chac landscape nao, mac dinh gia dinh 2-system (an toan hon) va hoi user truoc khi de xuat Developer Extensibility.

## 6. Ap dung khi review / sinh code (dung chung voi skill `sap-clean-code`)

- `sap-clean-code` lo phan **dat ten** (Z/Y namespace, snake_case, bo Hungarian...).
- Skill nay lo phan **kien truc/extensibility** — code do co duoc phep ton tai o layer nay khong, va cu phap co hop le voi ABAP Cloud khong.
- Khi review 1 doan code cho Public Cloud, kiem tra CA HAI: dat ten dung chuan VA kien truc dung bac thang extensibility + khong dung cu phap bi cam.

## 7. Nguon tham khao

- [Extensibility Approaches in SAP S/4HANA Cloud Public Edition](https://community.sap.com/t5/technology-blog-posts-by-sap/extensibility-approaches-in-sap-s-4hana-cloud-public-edition/ba-p/13793885)
- [Explaining the Extensibility Possibilities — SAP Learning](https://learning.sap.com/courses/expanding-sap-s-4hana-using-key-user-side-by-side-extensibility/explaining-the-extensibility-possibilities-depending-on-the-sap-s-4hana-version)
- [Extensibility | SAP Help Portal](https://help.sap.com/docs/SAP_S4HANA_CLOUD/0f69f8fb28ac4bf48d2b57b9637e81fa/533228e1e854433ab16d013f161ca509.html)
- SAP API Business Hub — `https://api.sap.com` (danh muc released API, kiem tra tinh trang release/cloud-qualified truoc khi dung)
- SAP Best Practices Explorer — danh muc scope item theo tung release

## 8. Khac biet theo edition (Private Edition / On-premise / BTP ABAP Environment)

[Dua tren kien truc tong quan da biet, chua xac minh song tung chi tiet cho ban release hien
tai — cung muc do tin cay nhu §1-§6. Luon xac minh lai voi tech lead/SAP Help truoc khi ap
dung cung nhac, dac biet compat scope cua Private Edition (tuy du an chon, khong co 1 quy tac
chung duy nhat).]

### s4hc_(private) — S/4HANA Cloud Private Edition

- Bac thang extensibility §2 van ap dung nhung **Developer Extensibility (bac 3) rong hon** —
  khong bi gioi han chi 3-system landscape nhu Public Edition, va tuy **compat scope** du an
  chon luc setup landscape ma co the con dung duoc BAdI/enhancement classic ben canh ABAP
  Cloud. HOI user/tech lead compat scope cu the truoc khi khang dinh 1 ky thuat classic dung
  duoc hay khong — dung tu suy dien tu Public Edition sang.
- Cu phap cam o §4 (bang ABAP Cloud) **khong bat buoc tuyet doi** neu du an chon compat scope
  cho phep classic ABAP — nhung SAP van khuyen dung ABAP Cloud cho code moi de de nang cap.
- Released-API-only (§3b) van la best practice khuyen dung (upgrade-safety) nhung khong bi ATC
  chan cung nhu Public Edition trong moi truong hop — kiem tra ATC variant that dang bat tren
  he thong (`sap-atc-review`) thay vi gia dinh.

### onprem — On-premise / RISE with SAP (khong ep ABAP Cloud)

- Toan bo bac thang §2 **khong bat buoc** — co the dung truc tiep: SPRO/IMG (cau hinh classic),
  customer exit, BAdI classic (SE18/SE19), enhancement point/enhancement framework, SE38/SE80
  dev truc tiep tren object chuan (van qua Z/Y namespace cho object cua khach hang).
- **SELECT truc tiep bang chuan** (MARA, VBAK, EKKO...) la binh thuong, khong can qua CDS/API
  released nhu §1/§3b mo ta.
- Cu phap cam o §4 **khong ap dung** tru khi du an tu nguyen theo huong ABAP Cloud de de dang
  migrate len Cloud sau nay.
- Clean Core (§3) la **khuyen nghi**, khong phai rang buoc ky thuat bat buoc — de xuat van nen
  uu tien released API/Key User khi hop ly, nhung khong fail-fast nhu Public Edition neu user
  chu dinh muon sua truc tiep tren object cua chinh ho (van ap dung rao chan Z/Y cua
  `sap-deployment-target`).

### btp — SAP BTP ABAP Environment (Steampunk)

- Day la 1 **runtime/he thong rieng**, khong phai "S/4HANA Cloud" — ban than no chinh la
  **bac 4 (side-by-side)** trong thang §2 nhin tu phia he thong core (du core la
  `s4hc_(public)`, `s4hc_(private)`, hay `onprem`).
- Cu phap cam o §4 **bat buoc** (day la ABAP Cloud restricted 100%, khong co ngoai le).
- **Khong doc/ghi truc tiep** bat ky he thong core nao — luon goi qua released API/RFC/OData du
  core dang ket noi la edition gi. Neu can du lieu tu core, ap dung cay quyet dinh §3b nhung
  buoc ① luon la "co released API/CDS tu he thong core khong" (khong co khai niem "table chuan"
  o day vi BTP ABAP Environment khong so huu du lieu nghiep vu core).
- Khong co SSCUI/Key User Extensibility rieng (do khong phai he thong nghiep vu) — cau hinh
  chu yeu la BTP cockpit/destination/Communication Arrangement, xem `sap-btp-connectivity`.
