---
name: sap-btp-admin-cloud
description: Kien thuc BTP Platform Administration chi tiet — account structure, naming convention, CLI commands, CF manifest, Kyma k8s config, destination setup, security config (XSUAA/xs-security.json), CI/CD pipeline (MTA descriptor), App Router, performance & cost, troubleshooting.
effort: medium
model: haiku
---

# BTP Admin — DEEP — Platform

[Seed set — kiem chung qua SAP Help Portal, SCC BTP, SAP Community BTP tag. Muc 1 va 9 gop tu
`skills/sap-btp-best-practices/SKILL.md` (2026-07-31, xem
`docs/audits/2026-Q3-skill-consolidation-part2.md`) — noi dung security/CI-CD trung lap da
duoc hop nhat vao muc 5/6 thay vi lap lai.]

## 1. Account Structure & Naming Conventions

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

| Resource | Convention | Vi du |
|----------|-----------|-------|
| Subaccount | `<PROJECT>-<ENV>` | `myproject-dev` |
| CF Org | `<PROJECT>-<ENV>-org` | `myproject-dev-org` |
| CF Space | `<COMPONENT>-<TYPE>` | `backend-dev` |
| App name | `<COMPONENT>-<FUNCTION>` | `order-service` |
| Service instance | `<COMPONENT>-<SERVICE>` | `order-hana` |
| Destination | `<SYSTEM>-<CONTEXT>` | `S4HANA-SalesOrder` |
| Role collection | `<SCOPE>-<ROLE>` | `Sales-Processor` |

## 2. Cloud Foundry (CF)

### Key CLI Commands

```bash
# Login
cf login -a <api-endpoint> -u <user> -o <org> -s <space>
cf api https://api.cf.<region>.hana.ondemand.com

# Apps
cf push <app-name>            # Deploy app
cf apps                       # List apps
cf scale <app> -i <instances> # Scale
cf env <app>                  # View env vars
cf logs <app>                 # Live logs

# Services
cf marketplace                # List available services
cf create-service <name> <plan> <instance>
cf bind-service <app> <instance>
cf services                   # List service instances

# Other
cf target -s <space>          # Switch space
cf target -o <org>            # Switch org
cf help                       # Help
```

### manifest.yml

```yaml
applications:
- name: my-app
  path: ./
  memory: 256M
  buildpacks:
    - nodejs_buildpack
  services:
    - my-hana-instance
    - my-uaa-instance
  env:
    NODE_ENV: production
```

## 3. Kyma (Kubernetes)

### Key kubectl Commands

```bash
# Namespace
kubectl get namespaces
kubectl create namespace my-namespace

# Deployment
kubectl apply -f deployment.yaml
kubectl get pods -n my-namespace
kubectl logs -f <pod> -n my-namespace
kubectl describe pod <pod> -n my-namespace

# Services
kubectl get services -n my-namespace
kubectl get ingress -n my-namespace
```

### Kyma Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: my-app
        image: my-registry/my-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: SAP_BTP_SERVICE
          valueFrom:
            secretRef:
              name: my-secret
```

## 4. Destination & Cloud Connector

> Chi tiet day du (Destination Types, JSON config, ACL, 6 loai authentication, principal
> propagation, troubleshooting, code pattern CAP/ABAP Cloud): `reference/modules/
> sap-btp-connectivity/SKILL.md` (khai bao trong `skills:` cua agent nay).

Tom tat nhanh:
- 4 loai destination: HTTP (Internet hoac OnPremise), RFC (OnPremise), LDAP (OnPremise).
- Setup Cloud Connector: install (on-prem VM) -> connect subaccount -> config ACL
  (virtual host + allowed resource) -> test destination trong BTP Cockpit.
- Best practice: dat ten destination theo convention muc 1 (`<SYSTEM>-<CONTEXT>`, VD
  `S4HANA-SalesOrder`); uu tien `OAuth2ClientCredentials` cho S/4HANA Cloud thay vi Basic —
  khong hardcode credential trong code, luon goi qua ten destination.

## 5. Security

### IAS (Identity Authentication Service)

- External IdP -> IAS -> BTP (Trust configuration)
- Social login (Google, LinkedIn, SAML, OpenID Connect)
- Custom login screen branding

### XSUAA

- BTP-native auth (OAuth2 client_credentials / password)
- Role: read vs write admin
- Scope: `$XSAPPNAME.read`, `$XSAPPNAME.write`
- Authority: `$XSAPPNAME(application).<scope>`

`xs-security.json` (vi du):

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

Authentication flow:

```
Browser -> App Router -> XSUAA (OAuth2) -> App
                └─ Destination (forward token)
                    └─ Backend (S/4HANA / CAP)
```

### Role / Role Collection

```bash
# Roles: Read, Write, Admin (app-specific)
# Collections: SAP_BR_SALES_MANAGER, SAP_BR_ADMINISTRATOR
```

## 6. CI/CD

| Tool | Giong | Use case |
|---|---|---|
| **Project Piper** | Jenkins pipeline | SAP-native CI/CD |
| **GitHub Actions** | GA | SAP + non-SAP |
| **Azure DevOps** | ADO | Enterprise |

### GitHub Actions pipeline (vi du)

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

### MTA (Multi-Target Application) — cau truc project

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

### MTA Build & Deploy

```bash
npm install -g mbt            # MTA Build Tool
mbt build -t my-app.mta.tar   # Build MTA archive
cf deploy my-app.mta.tar      # Deploy to CF
```

## 7. App Router

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

## 8. SAP Services (Marketplace)

| Service | Plan | Use case |
|---|---|---|
| `hana` | hana-free / hana-cloud | HANA database |
| `xsuaa` | application | Auth |
| `destination` | lite | Destination (auto-config) |
| `connectivity` | lite | Cloud Connector |
| `portal` | standard | Work zone |
| `workflow` | standard | Business workflow |
| `integration-flow` | standard | CPI iFlow |

## 9. Performance & Cost

| Practice | Mo ta |
|----------|-------|
| **Lightweight containers** | Node.js: 128-256M, Java: 512M-1G |
| **Auto-scaling** | CF: `cf scale -i min-max`, Kyma: HPA |
| **Session affinity** | CF: Khong co, app must be stateless |
| **Database pooling** | CAP `@cap-js/hana` pool |
| **CDN** | Fiori static file qua CDN |
| **Stop dev instances** | Cf stop app dev ngoai gio |

## 10. Monitoring

| Cong cu | Moi truong | Ghi chu |
|---|---|---|
| SAP Cloud ALM | CF + Kyma | Cong cu monitoring chinh thuc cua SAP cho BTP |
| Kibana | Cloud Foundry | Log/monitoring cho CF |
| Prometheus | Kyma | Metrics/monitoring cho Kyma |

## 11. Troubleshooting

| Van de | Kiem tra |
|---|---|
| App khong start | `cf logs <app> --recent` |
| Destination fail | Kiem tra proxy / auth / Cloud Connector (chi tiet: `sap-btp-connectivity` muc 10) |
| CF API timeout | Region API endpoint dung chua? |
| App crash OOM | `cf scale <app> -m 512M` |
| Certificate error | Trust configuration / Cloud Connector cert |
| MTA deploy error | `cf mta <app> --version` kiem tra format |

## 12. Nguon tham khao

- SAP BTP Help: `https://help.sap.com/docs/btp`
- SAP BTP Guidance Framework
- SAP Discovery Center: BTP best practices
- SAP Community: BTP development patterns
- Cloud Foundry CLI: `https://docs.cloudfoundry.org/cf-cli/` (CLI docs)
- Kyma: `https://kyma-project.io/`
- Project Piper: `https://github.com/SAP/jenkins-library`
- MTA: `https://cap.cloud.sap/docs/advanced/deploy-to-cloud-foundry`
