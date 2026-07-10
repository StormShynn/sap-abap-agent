---
name: sap-key-user-toolkit
description: Huong dan thuc hanh Key User Extensibility tren SAP S/4HANA Cloud Public Edition (2-system landscape). Dung khi key user/functional consultant muon tu them field, tao business object, viet custom logic don gian, hoac sua giao dien Fiori ma KHONG can developer. Phu hop cho Custom Fields and Logic, Custom Business Objects, Custom Logic (Cloud BAdI), Adaptation Transactions. KHONG dung khi yeu cau can ABAP developer / side-by-side BTP.
argument-hint: [tac vu key user: them field | tao BO | custom logic | adaptation UI]
model: haiku
---


# SAP Key User Toolkit (S/4HANA Cloud Public Edition)

[Noi dung chua duoc xac minh rieng cho tung release quy - SAP ra 4 ban/nam (2502/2505/2508/2511...) nen luon nhac user xac minh ten app/SSCUI/tooltip cu the tren release hien tai truoc khi dua vao san xuat.]


## 1. Vi tri cua skill nay trong bac thang Extensibility

Skill sap-extensibility da mo ta 4 bac (SSCUI -> Key User -> Developer on-stack -> side-by-side).
Skill nay di sau vao **bac 2 (Key User Extensibility)** - la bac ma key user/functional consultant co the tu lam ma KHONG can developer.

Khi nao dung skill nay:

- Them 1-2 field moi vao 1 business object co san (mua hang, ban hang, master data...)
- Them logic kiem tra / tu dong dien gia tri don gian (validation, derivation, default value)
- Tao 1 bang master data moi voi UI rieng de quan ly
- An/hien/doi nhan/di chuyen field tren Fiori app co san

Khi KHONG dung skill nay (phai chuyen len bac tren hoac can developer):

- Logic phuc tap, can truy van nhieu bang, can ABAP can thiet -> Developer Extensibility hoac side-by-side BTP
- Sua core SAP, chen code vao chuong trinh chuan -> KHONG duoc phep tren Public Cloud
- Thay doi batch job / IDoc / tich hop phuc tap -> Integration Suite / BTP


## 2. Quy tac ngon tay truoc khi bat dau

1. **Chi lam trong Customizing tenant**, KHONG lam trong Production.
   - Trong Fiori launchpad -> app **Manage Your Solution** -> **Configure Your Solution**.
2. **Dat ten truoc**: quy uoc nhat quan prefix `YY` hoac `Z_` cho moi custom artifact. Tranh dung prefix trung voi extension cua team khac trong cung tenant.
3. **Test tren test script / test plan** SAP cung cap (Best Practices Explorer) truoc khi release.
4. **Mot custom field/logic nen phuc vu 1 nhom nghiep vu**, khong nhet nhieu nhom vao cung 1 BO custom -> kho bao tri.
5. **Truoc khi publish**: kiem tra lai quyen (authorization) cua custom field co anh huong den role hien tai khong.


## 3. 4 tac vu hay gap nhat

### 3.1 Them Custom Field (Custom Fields and Logic)

Fiori app: **Custom Fields and Logic** (namespace tu Fiori launchpad Search).

Buoc thuc hien:

1. App **Custom Fields and Logic** -> **Custom Fields** -> **Create**.
2. Chon **Business Context** = business object can mo rong (vi du: `Purchase Order Item`, `Sales Order`, `Business Partner`).
3. Chon **Label** (tieng Viet OK o UI, nhung ten ky thuat nen ASCII), **Identifier** (ten truong), **Type** (text/number/date/checkbox/... ).
4. Neu muon hien thi len UI cua Fiori app tuong ung -> tab **UI** -> check **Display in UI**, co the chon vi tri (section/field group) neu SAP cho phep.
5. Publish -> release sang Production qua transport request (Q-system) hoac app **Export Software Collection** (2-system).

Rang buoc:

- Moi BO chi cho phep them 1 so luong field gioi han (thuong 30-50 tuy BO).
- Khong the chen vao section bat ky, chi cac section SAP mo san.
- Sau khi publish -> KHONG the xoa field, chi co the dung Usage de tat su dung.


### 3.2 Them Custom Logic (Cloud BAdI for Key Users)

Fiori app: cung la **Custom Fields and Logic** -> tab **Custom Logic**.

Hai loai logic:

- **Validation**: chan khong cho save/post neu khong thoa man dieu kien.
- **Determination**: tu dong dien gia tri cho field khi trigger.

Cu phap **ABAP for Key Users** (khac ABAP Cloud day du, da don gian hoa):


```abap
*
* Determination: tu dien ma kho neu user khong nhap
*
IF purchase_order_item-supplier_phone IS INITIAL.
  purchase_order_item-supplier_phone = '+84-'.
ENDIF.

*
* Validation: chan PO neu so tien qua lon
*
IF purchase_order_item-net_amount > 1000000000.
  RAISE EXCEPTION TYPE cx_custom_exception
    EXPORTING
      textid = cx_custom_exception=>custom_text
      text   = 'PO khong duoc qua 1 ty'.
ENDIF.
```

Rang buoc cu phap ABAP for Key Users:

- Khong truy van truc tiep bang (chi dung field cua BO do SAP cung cap san).
- Khong goi function module (chi dung statement ABAP for Key Users).
- Khong vong lap phuc tap, khong dynamic SQL.
- Gioi han so dong code (thuong 200-500 dong tuy release).


### 3.3 Tao Custom Business Object

Fiori app: **Custom Business Objects**.

Buoc thuc hien:

1. App **Custom Business Objects** -> **New**.
2. Dat ten BO, **Label** (UI), **Identifier** (ten ky thuat ky tu dau la chu, tieng Viet OK label).
3. Them **Node** (truong) cho BO: chon type (text/number/date/association...).
4. SAP tu dong: tao bang database trong namespace rieng, tao OData API CRUD day du, tao Fiori UI co ban (list + detail).
5. Co the publish thanh tile tren Fiori launchpad cho user su dung.

Vi du thuc te:

- Tao BO `YY_VehicleRecord`: truong license_plate, owner`, `registration_date`, `vehicle_type`.
- Tu dong co OData `/sap/opu/odata/sap/```YY_VEHICLERECORD_CDS`` de app khac goi (side-by-side, BTP, Power Platform...)

### 3.4 Adaptation Transactions (sua Fiori UI)

Fiori app: **Adaptation Transport** (neu muon transport qua Q-system) hoac truc tiep trong app (**Adapt UI** neu co quyen).

Cho phep:

- An/hien truong
- Doi nhan field
- Di chuyen field sang section khac
- Dat field thanh bat buoc / read-only

KHONG cho phep:

- Them field moi (dung Custom Field)
- Them nut / button moi (can UI extension hoac developer)
- Sua logic validation cua field chuan


## 4. Quy trinh release tu Customizing -> Production (2-system)

1. Tao / sua tren Customizing tenant.
2. Test tren Customizing tenant (smoke test bang test plan SAP cung cap).
3. **Export Software Collection** (Fiori app **Export Software Collection**) -> lay file .zip.
4. Import file .zip vao Production tenant (Fiori app **Import Software Collection**).
5. **Activate** tren Production (chay activation cho tung artifact).
6. Verify tren Production bang user kinh doanh thuc.

**Luu y**: tenant Public Cloud thuong chi co 2 (Customizing + Production). Quy trinh 3-system chi co khi mua them goi Developer Extensibility.


## 5. Loi thuong gap va cach xu ly

| Loi | Nguyen nhan thuong | Xu ly |
|---|---|---|
| Khong thay tab Custom Fields and Logic | Chua co quyen Key User | Lien he admin phan quyen role `SAP_BR_KEYUSER_*` |
| Tao field nhung khong hien thi tren UI | Business Context chua duoc enable UI display | Mo lai field, tab UI, check Display in UI + dung release moi nhat |
| Custom Logic khong chay khi save | Trigger sai event | Xem lai scope: Validation chi chay khi save, Determination chi chay khi field thay doi |
| Khong publish duoc | Field trung ten, hoac BO da qua gioi han | Doi ten prefix, hoac tach BO |
| Import Production fail | Software Collection khong khop release | Re-export tu Customizing sau khi cap nhat release |


## 6. Checklist truoc khi release (review voi skill sap-extensibility + sap-clean-code)

- [ ] Custom field dat ten theo convention `YY_*` hoac `Z_*` (xem `sap-clean-code`).
- [ ] Logic khong query truc tiep bang standard, chi dung field BO SAP cung cap.
- [ ] Custom BO da test create / read / update / delete qua OData service (Postman / Fiori Elements).
- [ ] Da export Software Collection moi nhat truoc khi release.
- [ ] Da thong bao cho key user khac de tranh trung ten prefix.
- [ ] Co tai lieu noi bo mo ta muc dich custom field/logic.

## 7. Nguon tham khao

- [Key User Extensibility (SAP Help)](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [Custom Fields and Logic (SAP Learning)](https://learning.sap.com/)
- [Custom Business Objects (SAP Community)](https://community.sap.com/)
- [Software Collection - Export/Import (SAP Help)](https://help.sap.com/docs/SAP_S4HANA_CLOUD)

Task: {{ARGUMENTS}}

