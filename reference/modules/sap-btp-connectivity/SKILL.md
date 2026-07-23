---
name: sap-btp-connectivity
description: Knowledge note tổng hợp từ `secondsky/sap-skills`, `lemaiwo/btp-sap-odata-to-mcp-server` — SAP BTP Connectivity (Destination, Cloud Connector, Connectivity Service). Dùng để tra cứu nhanh. Knowledge note (không phải instruction skill), đồng nhất cấu trúc với `reference/modules/<module>-cloud/SKILL.md`.
effort: low
model: haiku
---

# SAP BTP Connectivity — Cloud Knowledge Note

Module con của plugin, dùng khi contributor cần tra nhanh pattern kết nối BTP ↔ on-prem / S/4HANA.
Không thay thế skill `sap-btp-connectivity` (skill instruction) và
`sap-btp-admin-consultant-cloud` (agent consult thật).

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
| `Auth`       | `NoAuthentication`, `Basic`, `OAuth2ClientCredentials`, `OAuth2AuthorizationCode`, `SAMLAssertion`, `ClientCertificateAuthentication` |
| `Properties` | `sap-application-data` (isSensitive), headers |

**On-prem thường kèm `CloudConnectorLocationId` + `CloudConnectorProperties`.**

## 3. Cloud Connector (chạy on-prem)

- **Reverse proxy + TLS termination** từ BTP tới hệ thống internal.
- **Allowlist**: chỉ host:port được khai báo mới đi qua.
- **Mapping**: ảo hóa internal host thành virtual host trên BTP.

```
BTP → virtual-host:port → Cloud Connector → internal-host:port
```

Khi cấu hình:
- Tạo **Subaccount** mapping (tới BTP Subaccount ID).
- Tạo **Cloud-to-On-Premise Mapping** với Resource Type = `ABAP System` hoặc backend HTTP.
- Test connection từ Cockpit phía BTP.

## 4. Connectivity Service

- Tạo 1 instance `connectivity` cho mỗi subaccount.
- Bind vào app trên CF/Kyma (`cf bind-service my-app connectivity`).
- App dùng `connectivity-proxy` để route on-prem traffic.

## 5. Cloud Foundry env vars hay dùng

| Env var                    | Mục đích                            |
|----------------------------|--------------------------------------|
| `VCAP_SERVICES`            | Toàn bộ bound services (JSON)        |
| `VCAP_APPLICATION`         | Metadata app (name, instance_id, urls) |
| `CF_INSTANCE_*`            | Internal CF runtime info             |
| `SAP_GATEWAY_HTTP_*`       | (Steampunk) Gateway config          |

## 6. Skeleton ABAP consume on-prem HTTP qua Destination (Steampunk)

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

## 7. Connectivity Service cho Side-by-Side (CAP / Node.js)

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

## 8. Best Practice

- ✅ Tách Destination cho từng môi trường (dev/test/prod) — không share secret.
- ✅ Dùng `OAuth2ClientCredentials` thay vì Basic khi có thể.
- ✅ Đặt `sap-application-data: true` khi Destination chạm dữ liệu business nhạy cảm.
- ✅ Bật audit log Cloud Connector (cần license).
- ✅ Không hardcode URL on-prem — luôn qua Destination.

## 9. Liên kết với các skill khác

- **Skill instruction**: `sap-btp-connectivity` (công thức 4-step trong skill này).
- **Consultant**: `sap-btp-admin-consultant-cloud`.
- **Released class**: `sap-released-classes` mục "Email & Communication"
  (`cl_http_destination_provider`, `cl_web_http_client_manager`).
- **Setup wizard**: `sap-btp-setup`.

## 10. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module BTP Connectivity.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server) —
  minh họa consume OData qua Connectivity thật.
- SAP Help: SAP Connectivity service, Cloud Connector Admin Guide.
