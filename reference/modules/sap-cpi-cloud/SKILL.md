---
name: sap-cpi-cloud
description: Kien thuc CPI (Cloud Platform Integration / Integration Suite) — iFlow, adapter, mapping, API Management, Event Mesh, tich hop S/4HANA voi non-SAP. Dung khi user hoi ve CPI, integration, tich hop he thong.
effort: low
model: haiku
---

# CPI (Cloud Platform Integration) — CORE
> **Core layer**. Chi tiet iFlow/adapter/mapping/API/security/monitoring/quota nam o `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- **CPI la trung tam tich hop** — moi ket noi S/4HANA Cloud voi he thong ngoai deu qua CPI.
- **iFlow** la don vi trien khai co ban, ho tro nhieu loai adapter (SOAP, OData, HTTP, SFTP...).
- **Mapping** dung Message Mapping (XPath/XSLT) hoac Groovy script.
- **API Management** expose API qua proxy voi rate limiting/policy.

## 2. Route map
| Cau hoi user | Di den |
|---|---|
| "iFlow / kien truc tich hop / Edge Integration Cell" | deep §1 |
| "adapter OData/SOAP/SFTP/IDoc/RFC" | deep §2 |
| "mapping / Groovy script" | deep §3 |
| "API Management / proxy" | deep §4 |
| "security / monitoring / message size / quota" | deep §5, §6, §7 |

## 3. Lenh goi
1. Doc `deep/SKILL.md` theo section lien quan (dung `Grep`); cross-check SAP Help Portal / API Business Hub neu can.

## 4. Tich hop
`sap-sd-consultant-cloud`, `sap-mm-consultant-cloud`, `sap-ariba-consultant-cloud`, `sap-successfactors-consultant-cloud`, `sap-btp-admin-consultant-cloud`.
