---
name: sap-btp-best-practices
description: SAP BTP development best practices — account structure, naming conventions, CF guidelines, security patterns, CI/CD setup, MTA structure, multi-target application architecture.
when_to_use: |
  "BTP best practices", "cau truc BTP project", "BTP naming convention",
  "MTA structure", "BTP security pattern", "CF deploy practices".
argument-hint: "[cau hoi ve BTP best practices / conventions / patterns]"
effort: medium
model: sonnet
---

# SAP BTP Best Practices

## 1. Account Structure

```
Global Account
  └─ Directory (optional, for multi-subaccount grouping)
      └─ Subaccount (Dev / Test / Prod)
          ├─ Cloud Foundry Org
          │   └─ Spaces (dev, test, prod)
          └─ Kyma namespace
```

**Khuyen nghi**:
- 1 subaccount = 1 environment type (dev, test, prod)
- 1 subaccount = 1 region (eu10, us10, ap10)
- Quota: Dev < Test < Prod
- Tranh dung shared subaccount cho nhieu team

## 2. Naming Conventions

| Resource | Convention | Vi du |
|----------|-----------|-------|
| Subaccount | `<PROJECT>-<ENV>` | `myproject-dev` |
| CF Org | `<PROJECT>-<ENV>-org` | `myproject-dev-org` |
| CF Space | `<COMPONENT>-<TYPE>` | `backend-dev` |
| App name | `<COMPONENT>-<FUNCTION>` | `order-service` |
| Service instance | `<COMPONENT>-<SERVICE>` | `order-hana` |
| Destination | `<SYSTEM>-<CONTEXT>` | `S4HANA-SalesOrder` |
| Role collection | `<SCOPE>-<ROLE>` | `Sales-Processor` |

## 3. MTA (Multi-Target Application) Structure

```
my-mta-app/
+-- mta.yaml              # MTA deployment descriptor
+-- package.json           # Node.js / UI5
+-- pom.xml                # Java / CAP Java
+-- xs-security.json       # XSUAA security descriptor
+-- manifest.yml           # CF manifest (hoac trong mta.yaml)
+-- db/                    # Database artifacts
+-- srv/                   # Service (CAP Node.js/Java)
+-- app/                   # Fiori UI
+-- security/              # Authorization policies
```

## 4. Security Patterns

### XSUAA Configuration

```json
{
  "xsappname": "my-app",
  "tenant-mode": "dedicated",
  "scopes": [
    {
      "name": "$XSAPPNAME.read",
      "description": "Read access"
    },
    {
      "name": "$XSAPPNAME.write",
      "description": "Write access"
    }
  ],
  "role-templates": [
    {
      "name": "Viewer",
      "scope-references": ["$XSAPPNAME.read"]
    },
    {
      "name": "Editor",
      "scope-references": ["$XSAPPNAME.read", "$XSAPPNAME.write"]
    }
  ]
}
```

### Authentication Flow

```
Browser -> App Router -> XSUAA (OAuth2) -> App
                └─ Destination (forward token)
                    └─ Backend (S/4HANA / CAP)
```

## 5. CI/CD Pipeline (GitHub Actions + Cloud Foundry)

```yaml
name: Deploy to BTP
on: push
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: SAP/cloud-mta-build@v1
      - uses: SAP/cloud-cf-deploy@v1
        with:
          api: ${{ secrets.CF_API }}
          org: ${{ secrets.CF_ORG }}
          space: ${{ secrets.CF_SPACE }}
          credentials: ${{ secrets.CF_CREDS }}
```

## 6. Service Consumption

### Destination Pattern

```yaml
# BTP Cockpit -> Destination
Name: S4HANA-API
Type: HTTP
URL: https://mytenant.s4hana.cloud.sap
ProxyType: Internet
Authentication: OAuth2ClientCredentials
clientId: sb-xxx
clientSecret: xxx
tokenServiceURL: https://<tenant>.authentication.<region>.hana.ondemand.com/oauth/token
```

### App Router Configuration

```json
{
  "routes": [
    {
      "source": "/s4/api/(.*)",
      "target": "/sap/opu/odata4/sap/",
      "destination": "S4HANA-API",
      "authenticationType": "xsuaa"
    }
  ]
}
```

## 7. Performance & Cost

| Practice | Mo ta |
|----------|-------|
| **Lightweight containers** | Node.js: 128-256M, Java: 512M-1G |
| **Auto-scaling** | CF: `cf scale -i min-max`, Kyma: HPA |
| **Session affinity** | CF: Khong co, app must be stateless |
| **Database pooling** | CAP `@cap-js/hana` pool |
| **CDN** | Fiori static file qua CDN |
| **Stop dev instances** | Cf stop app dev ngoai gio |

## Nguon tham khao

- SAP BTP Guidance Framework
- SAP Discovery Center: BTP best practices
- SAP Community: BTP development patterns
- CF CLI documentation
