---
name: sap-btp-connectivity
description: SAP BTP Connectivity — Cloud Connector, Destination service, HTTP/RFC/LDAP destinations, authentication methods, connection troubleshooting, on-premise connectivity patterns.
when_to_use: |
  "BTP Cloud Connector", "destination cau hinh", "ket noi on-prem S/4HANA",
  "RFC destination BTP", "connectivity troubleshooting", "proxy type internet vs on-premise".
argument-hint: "[cau hoi ve BTP connectivity / Cloud Connector / destination]"
effort: medium
model: sonnet
---

# SAP BTP Connectivity

## 1. Kien truc Connectivity

```
BTP App (CAP/UI5)
  │
  ├─ Internet (direct) ─── S/4HANA Cloud Public APIs
  │
  └─ On-Premise ─── Cloud Connector (on-prem agent)
                       ├─ S/4HANA On-Prem
                       ├─ ECC
                       └─ 3rd party system
```

## 2. Cloud Connector

Cloud Connector la proxy agent chay tren on-prem, cho phep BTP goi vao he thong ben trong mang noi bo.

### Installation

```bash
# Download from SAP BTP Cockpit -> Connectivity -> Cloud Connector
# Install on Windows/Linux VM (on-prem)
# Java 11 required (OpenJDK or SAP JVM)

# Default ports:
HTTP: 8080  (UI)
HTTPS: 8443 (Admin)
```

### Configuration Steps

1. **Install**: Cloud Connector tren on-prem VM
2. **Connect**: BTP Subaccount -> Virtual Host (VD: `s4hana.internal.com`)
3. **ACL**: Add allowed resources (VD: `/sap/opu/odata/sap/API_*`)
4. **Principal Propagation**: Map on-prem user <-> BTP user

### ACL Config (Access Control List)

```xml
<!-- Allowed resources trong Cloud Connector UI -->
Virtual Host: s4hana.internal.com  Port: 443
└─ /sap/opu/odata/sap/API_SALES_ORDER_SRV (Allow)
└─ /sap/bc/srt/scs_ext (Allow)
```

## 3. Destination Types

| Type | Proxy | Use Case |
|------|-------|----------|
| **HTTP** | Internet | S/4HANA Cloud, external APIs |
| **HTTP** | OnPremise | S/4HANA on-prem (qua Cloud Connector) |
| **RFC** | OnPremise | BAPI/RFC calls (on-prem) |
| **LDAP** | OnPremise | LDAP authentication |

### HTTP Internet Destination

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

### HTTP OnPremise Destination

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

## 4. Authentication Types

| Type | Mo ta | Dung khi |
|------|-------|----------|
| `BasicAuthentication` | Username + Password | Legacy systems |
| `OAuth2ClientCredentials` | Client ID + Secret (SAP BTP OAuth) | S/4HANA Cloud |
| `OAuth2SAMLBearerAssertion` | SAML token (principal propagation) | SSO scenarios |
| `OAuth2UserTokenExchange` | User token exchange | App-to-app delegation |
| `ClientCertificate` | mTLS | High security |
| `NoAuthentication` | Public endpoints | Open APIs |

## 5. Principal Propagation

Quy trinh propagation user identity tu BTP -> on-prem:

```text
1. BTP App authenticates user (via XSUAA)
2. App calls Destination (OAuth2SAMLBearerAssertion)
3. Cloud Connector receives SAML assertion
4. Cloud Connector maps to on-prem user (via mapping rules)
5. On-prem app receives on-prem user context
```

## 6. Troubleshooting

| Issue | Check |
|-------|-------|
| Destination timeout | Proxy type dung? Cloud Connector running? |
| 401 Unauthorized | Auth type dung? Token expired? |
| 403 Forbidden | ACL allowed resource? |
| 404 Not Found | URL path exact? Dest config correct? |
| Connection refused | Cloud Connector port m? |
| SSL error | Trust certificate? mTLS config? |
| RFC call fail | Cloud Connector RFC protocol enabled? |

## 7. Common Patterns

### CAP + S/4HANA Destination

```cds
// CAP service consuming S/4HANA API
using { API_SALES_ORDER_SRV as S4 } from 's4-api';

service ExtensionService {
  entity SalesOrders as projection on S4.A_SalesOrder;
}
```

### Destination Lookup (ABAP Cloud)

```abap
DATA(lo_dest) = cl_http_destination_provider=>create_by_cloud_destination(
  i_name = 'S4HANA-API'
).
```

## Nguon tham khao

- SAP Help Portal: Connectivity, Cloud Connector
- SAP Community: BTP destination patterns
- BTP Cockpit -> Connectivity -> Destination documentation
