---
name: sap-ibp-cloud-deep
description: Kien thuc IBP (Integrated Business Planning) chi tiet — planning area, key figure, algorithm, master data type, integration scenario, extensibility. Dung khi can thong tin chuyen sau ve IBP cloud planning.
effort: high
model: haiku
---

# IBP (Integrated Business Planning) — Deep Knowledge

## 1. Planning Areas chinh (Standard Templates)

SAP IBP cung cap san cac planning area template cho tung module:

| Planning Area | Module | Key Figures chinh | Algorithm mac dinh |
|--------------|--------|------------------|-------------------|
| `SAP_SOP_DEFAULT` | S&OP | Sales, Capacity, Inventory, Revenue | Heuristic smoothing |
| `SAP_DEMAND_DEFAULT` | Demand Planning | Historical Sales, Statistical Forecast, Final Forecast | Automatic (ETS) |
| `SAP_SUPPLY_DEFAULT` | Supply Planning | Demand, Supply, Projected Stock, Shortage | Heuristic / Optimizer |
| `SAP_INVENTORY_DEFAULT` | Inventory | Safety Stock, Cycle Stock, Service Level | Multi-echelon optimizer |

## 2. Loai Key Figures

| Loai | Mo ta | Vi du |
|------|-------|-------|
| **Time-series** | Du lieu theo chuoi thoi gian (tuan/thang) | Forecast, Sales History, Inventory |
| **Order-based** | Du lieu theo don hang cu the | Sales Order, Purchase Order |
| **Numeric** | So don thuan | Quantity, Amount, Weight |
| **Derived** | Tinh toan tu key figure khac (formula) | `Inventory = Supply - Demand` |
| **Cumulated** | Cong don theo thoi gian | YTD Sales, Rolling Forecast |

## 3. Algorithms pho bien

| Algorithm | Module | Mo ta |
|-----------|--------|-------|
| **Statistical Forecast** | Demand | Phuong phap thong ke (ETS, ARIMA, Croston) |
| **Demand Sensing** | Demand | ML ngap han (nhan dien xu huong hang ngay) |
| **Supply Heuristic** | Supply | Tinh toan cung ung dua tren rut rang buoc (constrained – forward/backward) |
| **Supply Optimizer** | Supply | Toi uu hoa toan cuc choi SCM (giai bai toan linear programming) |
| **Multi-Echelon Optimizer** | Inventory | Toi uu Safety Stock xuyen cac cap do warehouse (central → regional → DC) |
| **S&OP Heuristic** | S&OP | Can bang cung-cau: Demand → Supply → So le (gap) → Dieu chinh |

## 4. Master Data Types

IBP can master data `Product` + `Location` (va `Product-Location`) de chay:
- **Product**: Product ID, product hierarchy, weight, volume, shelf life
- **Location**: Plant, DC, customer location, region, country
- **Product-Location**: Lead time, safety days, min lot size, sourcing rule
- **Customer**: Customer hierarchy, region, service level target
- **Resource**: Production line, capacity, efficiency

## 5. Tich hop S/4HANA (Chi tiet)

| Scenario | SAP_COM | Huong | Noi dung |
|----------|---------|-------|----------|
| Product Master | 0009 | S/4HANA → IBP | Material master: product hierarchy, base unit, weight |
| BP Master | 0008 | 2-way | Customer, supplier: name, address, hierarchy |
| IBP Inbound | 0931 | S/4→IBP | Sales history, inventory, open orders, receipt |
| CDS Extraction | 0531 | S/4→Datasphere→IBP | CDS view extraction cho BI/analytics cho IBP |
| Planning Result | Custom | IBP→S/4 | Planned order, purchase requisition, forecast (qua CPI) |

## 6. Control Tower cap Phat

| Alert | Mo ta | Threshold dien hinh |
|-------|-------|--------------------|
| Stockout Risk | Ton kho sap ve 0 hoac duoi safety stock | <3 days coverage |
| Excess Inventory | Ton kho vuot qua muc cho phep | >60 days coverage |
| Forecast Accuracy | Do chinh xac du bao duoi nguong | MAPE > 50% |
| Service Level | Ty le dap ung don hang dap ung SL target | Fill rate < 95% |
| Supplier Delay | Nha cung cap cham giao hang | >=5 days late |

## 7. Nguon tham khao

- [SAP IBP Help Portal](https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING)
- [SAP IBP Algorithm Guide](https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING/2cf21ae5b5b6491f862a1e88487e07e7)
- [SAP IBP Integration Guide](https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING/7ed3d93655ec4cc58f78e317be8c2c87)
- [SAP API Business Hub — IBP APIs](https://api.sap.com)
- [SAP Learning — Exploring Planning Processes in SAP IBP](https://learning.sap.com/courses/exploring-planning-processes-in-sap-ibp)
