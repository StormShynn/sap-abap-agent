---
name: sap-basis-cloud
description: Kien thuc Basis / Technical Administration cho SAP S/4HANA Cloud Public Edition — user admin, roles, transports, system monitoring, job scheduling, ABAP system admin, Fiori admin, tenant management. Dung khi user hoi ve quan tri he thong, phan quyen, transport, job, performance.
effort: medium
model: haiku
---

# Basis (Technical Administration) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help (xem Nguon tham khao). Luu y: Public Cloud Basis
khac xa on-premise. Nhieu tac vu Basis truyen thong (kernel update, DB admin, STMS...) KHONG
the lam tren Cloud — SAP tu quan ly.]

## 1. Van hanh he thong Public Cloud

| Tac vu | Ai lam | Ghi chu |
|--------|--------|---------|
| Upgrade SAP | **SAP** (auto quarterly) | Khach hang KHONG the tu upgrade |
| Kernel / DB patch | **SAP** | Tu dong trong release |
| Backup / Restore | **SAP** (tu dong) | Khach hang khong can backup |
| Performance monitoring | **SAP** + Khach hang | SAP monitor, khach hang xem qua Fiori |
| Transport management | **Khach hang** | Dung Fiori app Manage Software Collection |
| User / Role admin | **Khach hang** | Dung Fiori app Maintain Business Users / Roles |
| Job scheduling | **Khach hang** | Dung Fiori app Manage Jobs / Manage Scheduler |
| Tenant management | **SAP** + Khach hang | Developer Extensibility tenant (3-system) |

## 2. Fiori app cho tac vu Basis

| Tac vu | Fiori app | Legacy transaction cu |
|--------|-----------|----------------------|
| Quan ly user | Maintain Business Users | SU01 |
| Phan quyen role | Maintain Business Roles | PFCG |
| Transport | Export Software Collection | STMS |
| Job background | Manage Jobs | SM37 |
| Lich dinh ky | Manage Scheduler | SM36 |
| Certificate | Manage Certificate Store | STRUST |
| Log / monitoring | Manage System Monitoring | ST03 / SM50 |
| Kiem tra he thong | System Status Dashboard | SM51 |
| Tuy chinh Launchpad | Manage Launchpad Content | /UI2/FLPD_CUST |
| Quan ly tenant | (Manage Your Solution) | — |

## 3. User admin & Role

| Loai user | Cach tao | Ghi chu |
|-----------|----------|---------|
| Business user | Fiori: Maintain Business Users | Dung cho nguoi dung kinh doanh, gan role |
| Technical user | SAP BTP cockpit | Cho integration, API calls |
| Communication user | Fiori: Maintain Communication Users | Cho RFC / OData giao tiep |
| Communication system | Fiori: Maintain Communication Systems | Dat ca he thong doi tac |
| Role | Maintain Business Roles | Role gan tu SAP Business Catalog |

**Cach phan quyen**: Business Role gom Business Catalog (Fiori app) va Restriction (data access).
Dung **Business Catalog** de quyet dinh app nao user duoc thay. Dung **Restriction** de gioi han
du lieu (company code, plant...).

## 4. Transport (Software Collection)

Transport tren Public Cloud khac on-premise (khong co STMS, khong co transport tracks):

1. Tao / cau hinh trong **Configure Your Solution** (Customizing tenant).
2. **Export Software Collection** tu Customizing tenant → file .zip.
3. **Import Software Collection** vao Production tenant.
4. Activation chay tu dong sau import.

**Rang buoc**:
- Chi transport toan bo collection, khong the transport tung request le.
- Collection version phai khop giua 2 tenant.
- Developer Extensibility (3-system) co the co transport rieng (RAP objects).

## 5. Job Scheduling

| Tac vu | Fiori app |
|--------|-----------|
| Tao job | Manage Jobs |
| Dat lich | Manage Scheduler |
| Theo doi job | Monitor Jobs |
| ABAP program | Manage Jobs -> ABAP Program |

**Note**: Khong the dung SM36. Tat ca job tao qua Manage Jobs / Manage Scheduler.

## 6. Quan ly tenant

| Landscape | So tenant | Ai quan ly |
|-----------|-----------|------------|
| **2-system** | Customizing + Production | SAP (tu dong) |
| **3-system** | Dev + Customizing + Production | Khach hang co them development tenant (Developer Extensibility) |

**Note**: Khong the tao tenant moi. Tenant da duoc SAP cung cap trong hop dong.

## 7. Luu y dac thu cho Basis tren Public Cloud

- **Basis tren Public Cloud la "zero administration"**: SAP lo kernel, DB, backup, network, uptime.
  Khach hang chi quan ly user, role, job, transport, content.
- **Khong the truy cap DB truc tiep**: Khong co SQL console, khong co DB login.
- **Khong the cai phan mem / add-on**: Chi dung SAP-released features.
- **Khong the sua SAP source code**: Clean Core.
- **CDS view / BAdI**: Chi dung custom objects, khong sua standard objects.
- **Performance**: Qua Fiori app Manage System Monitoring. Neu can co van SAP, mo SAP Incident.
- **Logging**: Security log, audit log qua Fiori app.

## 8. Nguon tham khao

- [SAP S/4HANA Cloud — User & Role Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [SAP S/4HANA Cloud — Software Collection](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [Business Role vs Business User](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
