---
name: sap-btp-connectivity
description: Kien thuc SAP BTP Connectivity — Destination (types, JSON config, auth), Cloud Connector (ACL, mapping), Connectivity Service, Principal Propagation, troubleshooting. Nguon tham chieu day du cho agent sap-btp-admin-consultant-cloud va cac module tich hop BTP khac; tong hop tu secondsky/sap-skills, lemaiwo/btp-sap-odata-to-mcp-server.
effort: low
model: haiku
---

# SAP BTP Connectivity — Cloud Knowledge Note

Nguon tham chieu day du cho contributor/agent can tra cuu pattern ket noi BTP ↔ on-prem /
S/4HANA. Duoc dispatch qua agent `sap-btp-admin-consultant-cloud` (khai bao
`skills: [..., sap-btp-connectivity, ...]`); cac module `reference/modules/*-integration/
SKILL.md` khac (HCM, GTS, CA, Fiori role, BW, PS, TR, WM-EWM) tro ve day o muc "BTP
architecture". Tu 2026-07-31, day la nguon duy nhat cho chu de nay — noi dung tu
`skills/sap-btp-connectivity/SKILL.md` (destination JSON examples, bang auth type,
troubleshooting) da duoc gop vao day, xem
`docs/audits/2026-Q3-skill-consolidation-part2.md`.

## 1. Tổng quan 3 lớp

```
┌──────────────────────────────────────────────────┐
│ BTP Subaccount                                    │
│  ├── Destination (URL + auth)                     │  ← Khai báo kết nối
│  ├── Connectivity Service (instance)              │  ← Proxy on-prem
│  └── Cloud Connector (on-prem)                    │  ← Reverse proxy + allowlist
└──────────────────────────────────────────────────┘
                            ↓
            ┌──────────────────────────────┐
            │ On-prem (S/4HANA, ECC, ...)  │
            └──────────────────────────────┘
```

## 2. Destination

| Thành phần   | Mục đích                                      |
|--------------|-----------------------------------------------|
| `Name`       | Tên logical do user đặt                        |
| `URL`        | Endpoint hệ thống đích                         |
| `Type`       | `HTTP` / `RFC` / `MAIL` / `LDAP` / `TCP`      |
| `ProxyType`  | `Internet` / `OnPremise` / `PrivateLink`       |
| `Auth`       | Xem bảng Authentication Types (mục 3)          |
| `Properties` | `sap-application-data` (isSensitive), headers |

**On-prem thường kèm `CloudConnectorLocationId` + `CloudConnectorProperties`.**

### Destination Types (theo Type + Proxy)

| Type | Proxy | Use Case |
|------|-------|----------|
| **HTTP** | Internet | S/4HANA Cloud, external APIs |
| **HTTP** | OnPremise | S/4HANA on-prem (qua Cloud Connector) |
| **RFC** | OnPremise | BAPI/RFC calls (on-prem) |
| **LDAP** | OnPremise | LDAP authentication |

### HTTP Internet Destination (ví dụ)

```json
{
  "Name": "S4HANA-Cloud",
  "Type": "HTTP",
  "URL": "https://mytenant.s4hana.cloud.sap",
  "ProxyType": "Internet",
  "Authentication": "OAuth2ClientCredentials",
  "clientId": "sb-xxx",
  "clientSecret": "xxx",
  "tokenServiceURL": "https://<tenant>.authentication.<region>.hana.ondemand.com/oauth/token",
  "tokenServiceURLType": "Dedicated"
}
```

### HTTP OnPremise Destination (ví dụ)

```json
{
  "Name": "S4HANA-OnPrem",
  "Type": "HTTP",
  "URL": "http://s4hana.internal.com:443/sap/opu/odata",
  "ProxyType": "OnPremise",
  "Authentication": "BasicAuthentication",
  "User": "sapuser",
  "Password": "xxx",
  "CloudConnectorLocationId": "dc1",
  "sap-client": "100"
}
```

## 3. Authentication Types

| Type | Mo ta | Dung khi |
|------|-------|----------|
| `NoAuthentication` | Public endpoints | Open APIs |
| `BasicAuthentication` | Username + Password | Legacy systems |
| `OAuth2ClientCredentials` | Client ID + Secret (SAP BTP OAuth) | S/4HANA Cloud |
| `OAuth2SAMLBearerAssertion` | SAML token (principal propagation) | SSO scenarios |
| `OAuth2UserTokenExchange` | User token exchange | App-to-app delegation |
| `ClientCertificateAuthentication` (mTLS) | Client certificate | High security |

## 4. Cloud Connector (chạy on-prem)

- **Reverse proxy + TLS termination** từ BTP tới hệ thống internal.
- **Allowlist**: chỉ host:port được khai báo mới đi qua.
- **Mapping**: ảo hóa internal host thành virtual host trên BTP.

```
BTP → virtual-host:port → Cloud Connector → internal-host:port
```

### Installation

```bash
# Download from SAP BTP Cockpit -> Connectivity -> Cloud Connector
# Install on Windows/Linux VM (on-prem)
# Java 11 required (OpenJDK or SAP JVM)

# Default ports:
HTTP: 8080  (UI)
HTTPS: 8443 (Admin)
```

Khi cấu hình:
- Tạo **Subaccount** mapping (tới BTP Subaccount ID).
- Tạo **Cloud-to-On-Premise Mapping** với Resource Type = `ABAP System` hoặc backend HTTP.
- Test connection từ Cockpit phía BTP.

### ACL Config (Access Control List) — ví dụ

```xml
<!-- Allowed resources trong Cloud Connector UI -->
Virtual Host: s4hana.internal.com  Port: 443
└─ /sap/opu/odata/sap/API_SALES_ORDER_SRV (Allow)
└─ /sap/bc/srt/scs_ext (Allow)
```

## 5. Principal Propagation

Quy trinh propagation user identity tu BTP -> on-prem:

```text
1. BTP App authenticates user (via XSUAA)
2. App calls Destination (OAuth2SAMLBearerAssertion)
3. Cloud Connector receives SAML assertion
4. Cloud Connector maps to on-prem user (via mapping rules)
5. On-prem app receives on-prem user context
```

## 6. Connectivity Service

- Tạo 1 instance `connectivity` cho mỗi subaccount.
- Bind vào app trên CF/Kyma (`cf bind-service my-app connectivity`).
- App dùng `connectivity-proxy` để route on-prem traffic.

## 7. Cloud Foundry env vars hay dùng

| Env var                    | Mục đích                            |
|----------------------------|--------------------------------------|
| `VCAP_SERVICES`            | Toàn bộ bound services (JSON)        |
| `VCAP_APPLICATION`         | Metadata app (name, instance_id, urls) |
| `CF_INSTANCE_*`            | Internal CF runtime info             |
| `SAP_GATEWAY_HTTP_*`       | (Steampunk) Gateway config          |

## 8. Skeleton ABAP consume on-prem HTTP qua Destination (Steampunk)

```abap
DATA(lo_destination) = cl_http_destination_provider=>create_by_cloud_destination(
  i_name = 'MY_ON_PREM_API'
).

" Hoặc qua Communication Arrangement (S/4HANA):
" DATA(lo_destination) = cl_http_destination_provider=>create_by_comm_arrangement(
"   i_arrangement_name = 'MY_SCENARIO'
"   i_scenario_id      = 'Z_MY_SCENARIO'
" ).

DATA(lo_client) = cl_web_http_client_manager=>create_by_http_destination( lo_destination ).
DATA(lo_response) = lo_client->execute( ).  " cl_http_response
```

## 9. Connectivity Service cho Side-by-Side (CAP / Node.js)

```bash
# Bind vào app
cf bind-service my-cap-app connectivity

# Hỗ trợ multi-region qua connectivity-proxy env:
#   "destinations": [{ "name": "...", "proxyType": "OnPremise" }]
```

Trong code:

```javascript
const xsenv = require('@sap/xsenv');
const services = xsenv.getServices({ connectivity: { name: 'connectivity' } });

// SCC (SAP Cloud Connector) location-id được inject tự động qua VCAP_SERVICES.
```

CAP tiêu thụ API S/4HANA qua destination (projection, không round-trip ABAP thủ công):

```cds
// CAP service consuming S/4HANA API
using { API_SALES_ORDER_SRV as S4 } from 's4-api';

service ExtensionService {
  entity SalesOrders as projection on S4.A_SalesOrder;
}
```

## 10. Troubleshooting

| Issue | Check |
|-------|-------|
| Destination timeout | Proxy type dung? Cloud Connector running? |
| 401 Unauthorized | Auth type dung? Token expired? |
| 403 Forbidden | ACL allowed resource? |
| 404 Not Found | URL path exact? Dest config correct? |
| Connection refused | Cloud Connector port mo? |
| SSL error | Trust certificate? mTLS config? |
| RFC call fail | Cloud Connector RFC protocol enabled? |

## 11. Best Practice

- ✅ Tách Destination cho từng môi trường (dev/test/prod) — không share secret.
- ✅ Dùng `OAuth2ClientCredentials` thay vì Basic khi có thể.
- ✅ Đặt `sap-application-data: true` khi Destination chạm dữ liệu business nhạy cảm.
- ✅ Bật audit log Cloud Connector (cần license).
- ✅ Không hardcode URL on-prem — luôn qua Destination.

## 12. Liên kết với các agent/skill khác

- **Consultant**: `sap-btp-admin-consultant-cloud` (agent tư vấn thật, sở hữu file này qua
  frontmatter `skills:`).
- **Released class**: `sap-released-classes` mục "Email & Communication"
  (`cl_http_destination_provider`, `cl_web_http_client_manager`).
- **Setup wizard**: `sap-btp-setup`.
- **BTP admin platform** (CF/Kyma/Security/CI-CD): `reference/modules/sap-btp-admin-cloud/`
  (core+deep) — file này chỉ chuyên sâu về connectivity, phần còn lại của BTP admin nằm ở đó.

## 13. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module BTP Connectivity.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server) —
  minh họa consume OData qua Connectivity thật.
- SAP Help: SAP Connectivity service, Cloud Connector Admin Guide, BTP Cockpit → Connectivity →
  Destination documentation.
