---
name: sap-btp-admin-cloud
description: Kien thuc SAP BTP Platform Administration — Cloud Foundry, Kyma, Destination, Connectivity, Security, CI/CD, Monitoring, Service Marketplace. Dung khi user hoi ve BTP admin, CF, Kyma, cockpit.
effort: low
model: haiku
---

# BTP Admin — CORE — Platform
> **Core layer**. Chi tiet command, config, CLI, monitoring nam o `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- **BTP Platform khac hoan toan Basis**: BTP la PaaS (CF/Kyma), Basis la S/4HANA system admin.
- **3 Global Account structure**: Directory -> Subaccount -> Environment (CF/Kyma).
- **Destination**: Cau hinh ket noi den S/4HANA / he thong khac. OnPremise can Cloud Connector.
## 2. Route map
| Cau hoi user | Di den |
|---|---|
| "Account structure/naming, CF org/space/CLI" | deep §1 + §2 |
| "Kyma deployment" | deep §3 Kyma |
| "Destination + Cloud Connector" | deep §4 (chi tiet: `sap-btp-connectivity`) |
| "Security / IAS / XSUAA" | deep §5 Security |
| "CI/CD / MTA / App Router" | deep §6 + §7 |
| "Marketplace / Performance / Monitoring / Troubleshoot" | deep §8-§11 |
## 3. Lenh goi agent
Doc `deep/SKILL.md` theo section lien quan (dung `Grep` de vi tri); cross-check SAP BTP Help Portal / Cockpit neu can xac nhan cau hinh hien hanh.
## 4. Tich hop
- `sap-cap-consultant-cloud` — CAP deployment
- `sap-basis-consultant-cloud` — S/4HANA system admin
- `sap-cpi-consultant-cloud` — CPI Cloud Connector
- `sap-fiori-consultant-cloud` — Work Zone, Fiori Launchpad
