---
name: sap-ibp-cloud
description: Kien thuc IBP (Integrated Business Planning — demand, supply, inventory, S&OP, control tower) cho SAP IBP Cloud — planning area, key figure, algorithm, integration voi S/4HANA. Dung khi user hoi ve planning processes, du bao, toi uu chuoi cung ung.
effort: medium
model: haiku
when_to_use: Khi user hoi ve lap ke hoach chuoi cung ung (demand planning, supply planning, S&OP, inventory optimization) hoac tich hop IBP voi S/4HANA Cloud.
---

# IBP (Integrated Business Planning) tren SAP Cloud

[Seed set — IBP la cloud service rieng, kien thuc duoi day ap dung cho SAP IBP for Supply Chain
(2025+). Kiem cheo tren SAP Help/Ite o SAP Community truoc khi ap dung. Moi release quy co the
thay doi planning area template / key figure / algorithm.]

## 1. Tong quan kien truc

IBP la giai phap planning **standalone** (khong phai module S/4HANA), giao tiep voi S/4HANA qua
SAP Integration Suite (CPI). Cac planning area chinh:

| Planning Area | Muc dich | Algorithm chinh |
|--------------|----------|----------------|
| S&OP | Can bang cung-cau, dieu phoi cross-functional | Heuristic / Optimizer |
| Demand | Du bao nhu cau (time-series) | Statistical / ML / Demand Sensing |
| Supply | Lap ke hoach cung ung (order-based) | Heuristic / Optimizer |
| Inventory | Toi uu ton kho an toan (safety stock) | Optimizer (multi-echelon) |
| Response | Phan ung nhanh voi bien dong cung- cau | Heuristic |

## 2. Cac khai niem cot loi

| Khai niem | Mo ta |
|-----------|-------|
| **Planning Area** | Khong gian chua key figures + master data + logic |
| **Key Figure** | Chi so do luong (Forecast, Sales, Inventory, Service Level) |
| **Master Data Type** | Loai du lieu nen (Product, Location, Customer, Product-Location) |
| **Time Profile** | Cau truc thoi gian (Year/Quarter/Month/Week/Day) |
| **Version** | Plan version (Active / Simulation / What-If) |
| **Algorithm** | Thuat toan planning (Statistical Forecast, Heuristic, Optimizer) |

## 3. Fiori apps & cong cu chinh

| Cong cu | Muc dich | Giong |
|---------|----------|-------|
| **Excel Add-in** | Cong cu chinh de planner nhap/xem key figures | Excel-based planning |
| **Planner Workspaces** | Fiori app cho S&OP, Demand, Supply review | Web-based planning board |
| **Analytics - Advanced** | Phan tich du lieu planning | SAC-based analytics |
| **Manage Forecast Models** | Cau hinh mo hinh du bao (AI/ML) | Machine Learning |
| **IBP Administration Console** | Cau hinh planning area, key figure, user | Config UI chuyen dung |
| **Alert Management** | Thiet lap canh bao Control Tower | Alert monitoring |

## 4. Tich hop S/4HANA

| Communication Scenario | Mo ta |
|----------------------|-------|
| `SAP_COM_0009` | Product Master (S/4HANA → IBP) |
| `SAP_COM_0008` | Business Partner integration |
| `SAP_COM_0931` | IBP Inbound (IBP ← S/4HANA) |
| `SAP_COM_0531` | CDS Extraction (ABAP CDS → Datasphere) |

## 5. Huong mo rong

- **Custom Key Figure**: Them key figure moi vao planning area (IBP in-app)
- **Custom Master Data Type**: Them master data type moi (can SAP su dung hoac side-by-side)
- **Side-by-side BTP**: Tinh toan planning phuc tap ben ngoai (ML models, optimization engine)

## 6. Luu y

- IBP **KHONG** co SSCUI kieu S/4HANA — cau hinh Planning Area trong Admin Console
- IBP **KHONG** phai MRP — MRP la execution planning trong S/4HANA (PP)
- Du lieu planning dua vao IBP qua Integration Suite, sau do ket qua planning day ve S/4HANA

## 7. Nguon tham khao

- [SAP IBP Help Portal](https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING)
- [SAP Best Practices Explorer — IBP](https://me.sap.com/processnavigator)
- [SAP API Business Hub](https://api.sap.com)
- [SAP Community — IBP](https://community.sap.com/topics/ibp)

> 📚 Xem `deep/SKILL.md` (trong cung thu muc) de biet chi tiet ve planning areas, key figures,
> algorithm master data types, integration scenarios, va extbility options cho IBP.
