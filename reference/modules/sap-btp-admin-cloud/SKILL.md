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
| "CF org/space/CLI" | deep §1 CF |
| "Kyma deployment" | deep §2 Kyma |
| "Destination + Cloud Connector" | deep §3 Destination |
| "Security / IAS" | deep §4 Security |
| "CI/CD / MTA" | deep §5 CI/CD |
| "Marketplace / Monitoring / Troubleshoot" | deep §6 + §7 + §8 |
## 3. Lenh goi agent
Doc `deep/SKILL.md` theo section lien quan (dung `Grep` de vi tri); cross-check SAP BTP Help Portal / Cockpit neu can xac nhan cau hinh hien hanh.
## 4. Tich hop
- `sap-cap-consultant-cloud` — CAP deployment
- `sap-basis-consultant-cloud` — S/4HANA system admin
- `sap-cpi-consultant-cloud` — CPI Cloud Connector
- `sap-fiori-consultant-cloud` — Work Zone, Fiori Launchpad
