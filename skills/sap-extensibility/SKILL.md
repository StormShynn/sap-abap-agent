---
name: sap-extensibility
description: Huong dan extensibility & rang buoc ABAP Cloud cho SAP S/4HANA Cloud Public Edition. Dung khi user hoi nen dat custom logic o dau (SSCUI/Key User/side-by-side BTP), co dung duoc BAdI/SPRO/table truc tiep khong, hoac gap loi cu phap ABAP Cloud (RAP, released API).
effort: medium
model: haiku
---

# SAP Public Cloud — Extensibility & Rang buoc ABAP Cloud

[Chua xac minh song tung chi tiet — kien truc tong quan da kiem chung qua SAP Help/Learning/Community
(xem muc Nguon tham khao cuoi file); ten SSCUI/scope item/Fiori app cu the thay doi theo tung ban
release quy (SAP ra 4 ban/nam: vd 2502/2505/2508/2511) nen luon nhac user xac minh lai truoc khi dua
vao san xuat.]

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
   - *Custom Logic (Cloud BAdI)* — cac diem mo rong SAP da cong bo san cho key user.
   - *Adaptation Transactions* — an/di chuyen/doi nhan field tren Fiori app co san.
3. **Developer Extensibility (on-stack)** — **chi co tren 3-system landscape**; dev ABAP ngay trong tenant dev cua he thong core, van chi dung released API/extension point, khong sua duoc object chuan.
4. **Side-by-side tren BTP** — he thong/runtime rieng (thuong la BTP ABAP Environment, dung RAP). Chi goi nguoc lai core qua released API — KHONG co extension point nao ma in-app chua co san.

**Nguyen tac fail-fast**: neu 1 yeu cau khong khop bac nao trong 4 bac tren — DUNG bia ra 1 cach lam khong ton tai. Xac dinh xem yeu cau thuc su thuoc bac nao va de xuat dung bac do; neu khong bac nao dap ung, noi thang la chua lam duoc.

## 3. Clean Core — khong phai tuy chon, ma la he qua bat buoc

Vi khong co cach nao sua duoc core, moi custom asset chi co the la (a) 1 artifact Key User nam trong tenant extension rieng, hoac (b) 1 app side-by-side goi qua released API. Nghia la:
- Moi de xuat dung theo bac thang o muc 2 **tu dong tuan thu Clean Core**.
- Loi thuong gap nhat khong phai la vi pham Clean Core, ma la **de xuat 1 thu khong ton tai tren Public Cloud** (1 BAdI, 1 bang truy cap truc tiep, 1 BAPI chua duoc release, 1 man hinh khong phai Fiori). Luon xac minh moi de xuat co thuc su kha thi tren Public Cloud truoc khi dua ra.

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
