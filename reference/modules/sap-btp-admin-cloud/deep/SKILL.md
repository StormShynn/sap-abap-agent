---
name: sap-btp-admin-cloud
description: Kien thuc BTP Platform Administration chi tiet — CLI commands, CF manifest, Kyma k8s config, destination setup, security config, CI/CD pipeline, MTA descriptor, troubleshooting.
effort: medium
model: haiku
---

# BTP Admin — DEEP — Platform

[Seed set — kiem chung qua SAP Help Portal, SCC BTP, SAP Community BTP tag.]

## 1. Cloud Foundry (CF)

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

## 2. Kyma (Kubernetes)

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

## 3. Destination & Cloud Connector

> Chi tiet day du (Destination Types, ACL, 6 loai authentication, principal
> propagation, troubleshooting, code pattern CAP/ABAP Cloud): skill
> `sap-btp-connectivity` (da khai bao trong `skills:` cua agent nay).

Tom tat nhanh:
- 4 loai destination: HTTP (Internet hoac OnPremise), RFC (OnPremise), LDAP (OnPremise).
- Setup Cloud Connector: install (on-prem VM) -> connect subaccount -> config ACL
  (virtual host + allowed resource) -> test destination trong BTP Cockpit.

## 4. Security

### IAS (Identity Authentication Service)

- External IdP -> IAS -> BTP (Trust configuration)
- Social login (Google, LinkedIn, SAML, OpenID Connect)
- Custom login screen branding

### XSUAA

- BTP-native auth (OAuth2 client_credentials / password)
- Role: read vs write admin
- Scope: `$XSAPPNAME.read`, `$XSAPPNAME.write`
- Authority: `$XSAPPNAME(application).<scope>`

### Role / Role Collection

```bash
# Roles: Read, Write, Admin (app-specific)
# Collections: SAP_BR_SALES_MANAGER, SAP_BR_ADMINISTRATOR
```

## 5. CI/CD

| Tool | Giong | Use case |
|---|---|---|
| **Project Piper** | Jenkins pipeline | SAP-native CI/CD |
| **GitHub Actions** | GA | SAP + non-SAP |
| **Azure DevOps** | ADO | Enterprise |

### MTA Build & Deploy

```bash
npm install -g mbt            # MTA Build Tool
mbt build -t my-app.mta.tar   # Build MTA archive
cf deploy my-app.mta.tar      # Deploy to CF
```

## 6. SAP Services (Marketplace)

| Service | Plan | Use case |
|---|---|---|
| `hana` | hana-free / hana-cloud | HANA database |
| `xsuaa` | application | Auth |
| `destination` | lite | Destination (auto-config) |
| `connectivity` | lite | Cloud Connector |
| `portal` | standard | Work zone |
| `workflow` | standard | Business workflow |
| `integration-flow` | standard | CPI iFlow |

## 7. Monitoring

| Cong cu | Moi truong | Ghi chu |
|---|---|---|
| SAP Cloud ALM | CF + Kyma | Cong cu monitoring chinh thuc cua SAP cho BTP |
| Kibana | Cloud Foundry | Log/monitoring cho CF |
| Prometheus | Kyma | Metrics/monitoring cho Kyma |

## 8. Troubleshooting

| Van de | Kiem tra |
|---|---|
| App khong start | `cf logs <app> --recent` |
| Destination fail | Kiem tra proxy / auth / Cloud Connector |
| CF API timeout | Region API endpoint dung chua? |
| App crash OOM | `cf scale <app> -m 512M` |
| Certificate error | Trust configuration / Cloud Connector cert |
| MTA deploy error | `cf mta <app> --version` kiem tra format |

## 9. Nguon tham khao

- SAP BTP Help: `https://help.sap.com/docs/btp`
- Cloud Foundry CLI: `https://docs.cloudfoundry.org/cf-cli/`
- Kyma: `https://kyma-project.io/`
- Project Piper: `https://github.com/SAP/jenkins-library`
- MTA: `https://cap.cloud.sap/docs/advanced/deploy-to-cloud-foundry`
