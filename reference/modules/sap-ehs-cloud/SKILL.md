---
name: sap-ehs-cloud
description: Kien thuc EHS (Environment, Health & Safety — waste management, hazardous substances, industrial hygiene, safety, product safety, MSDS) cho SAP S/4HANA Cloud Public Edition. Dung khi user hoi ve moi truong, an toan lao dong, hoa chat, chat thai.
effort: low
model: haiku
---

# EHS (Environment, Health & Safety) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Help. **Luu y**: EHS tren Public Cloud co pham vi hep hon on-premise.
EHS Management (formerly SAP EHS, now part of Product Compliance) co the la side-by-side tren BTP.]

## 1. Cac chuc nang chinh

| Chuc nang | Mo ta |
|-----------|-------|
| **Product Safety** | MSDS (Material Safety Data Sheet), label, classification |
| **Hazardous Substance Management** | Quan ly hoa chat nguy hiem, UN number, transport classification |
| **Waste Management** | Quan ly chat thai, disposal, tracking |
| **Industrial Hygiene & Safety** | An toan lao dong, PPE, exposure monitoring |
| **Occupational Health** | Kham suc khoe dinh ky, medical surveillance |
| **Incident Management** | Bao cao su co lao dong, dieu tra |

## 2. Fiori app

| Nghiep vu | Fiori app |
|-----------|-----------|
| MSDS | Manage Material Safety Data Sheets |
| Nhan hoa chat | Manage Label |
| Khai bao chat thai | Manage Waste Disposal |
| An toan lao dong | Industrial Hygiene & Safety Dashboard |
| Su co lao dong | Manage Incident |
| Kham suc khoe | Manage Occupational Health |

## 3. Tich hop

| Module | Tich hop voi EHS |
|--------|----------------|
| MM | Material master, hazardous material classification |
| PP | Production process safety, exposure monitoring |
| QM | Quality inspection for hazardous substances |
| WM | Storage of hazardous materials |

## 4. API

- `API_PRODUCT_SAFETY_SRV`
- CDS view: `I_ProductSafety`, `I_Waste`
- Kiem tra tren `api.sap.com` cho release hien tai

## 5. Nguon tham khao

- [SAP Help — EHS](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- SAP API Business Hub
