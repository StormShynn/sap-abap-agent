---
name: sap-steampunk-cloud
description: Kien thuc SAP BTP ABAP Environment (Steampunk) — infrastructure, ADT setup, IAM, package structure, deployment, CI/CD, git integration, API consumption, database. Doc them khi agent BTP Admin can chi tiet ve ABAP Environment / Steampunk infrastructure.
effort: medium
model: haiku
---

# SAP BTP ABAP Environment (Steampunk)

## 1. Tong quan

SAP BTP ABAP Environment (Steampunk) la ABAP Platform-as-a-Service tren BTP Cloud Foundry.
**Khac voi S/4HANA Cloud**: Steampunk la ABAP runtime thuan, khong co module nghiep vu (SD, FI, MM...)
ma chi co ABAP language + framework (RAP, CDS, OData, AMDP).

**Dung de**: Side-by-side extension, custom app, integration service.
**KHONG dung de**: Thay the S/4HANA, chay module nghiep vu.

## 2. Infrastructure

```text
BTP Cockpit -> Subaccount -> Space
  └─ ABAP Environment service instance
      └─ ADT (Eclipse / VS Code) connect
          └─ Package structure (Z* / Y*)
```

### Tao ABAP Environment Instance

```bash
# cf CLI
cf create-service abap standard my-abap-env

# Kiem tra
cf service my-abap-env

# Restage
cf update-service my-abap-env -c '{"restartApp": true}'
```

## 3. Package Structure (Bat buoc)

Tren Steampunk, package structure la bat buoc:

```
$<TMP>           — Temporary objects (dev)
$<PRD>           — Production namespace
Z_MY_PACKAGE     — Custom package
  ├─ Z_MY_SUBPACKAGE_DB   — Database artifacts
  ├─ Z_MY_SUBPACKAGE_API  — API artifacts  
  └─ Z_MY_SUBPACKAGE_UI   -+ UI artifacts
```

**Quy tac**:
- Moi object PHAI nam trong 1 package
- Package name bat dau bang `Z_` hoac `$`
- Structure thuong theo layer: DB, Logic, API, UI

## 4. ADT Setup

### Eclipse
1. Install ADT plugin (SAP Development Tools)
2. Create ABAP Cloud project
3. Service Instance -> ABAP Environment -> Login (OAuth2)
4. Success: Package tab -> Z* packages

### VS Code
1. Install ADT extension (SAP)
2. Fiori: `SAP Business Application Studio`
3. abapGit: Clone -> Pull -> Push between systems

## 5. IAM (Identity & Access Management)

| Role | Mo ta |
|------|-------|
| `ABAP Developer` | Quyen tao/sua object ABAP |
| `ABAP Administrator` | Quyen admin package, transport |
| `SAP_BR_ADMINISTRATOR` | Business role |
| `Business Role` | End-user quyen truy cap app |

```bash
# BTP Cockpit -> Security -> Role Collections
# Gan Business Role -> Role -> User
```

## 6. Git Integration (abapGit)

Steampunk co git integration san (ADT -> Git):

```text
Local ADT -> Stage -> Commit -> Push -> GitHub/GitLab
           └─ Pull <- Remote repo
```

**Quy trinh**:
1. abapGit plugin trong ADT
2. Link package -> GitHub repo
3. Pull: Code tu github ve Steampunk
4. Push: Code tu Steampunk -> GitHub
5. CI/CD pipeline: GitHub Actions -> Deploy

## 7. CI/CD

```yaml
# .github/workflows/deploy-abap.yml
name: Deploy to Steampunk
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Push to ABAP Environment
        uses: SAP/abap-environment-java-cf-cli@v1
        with:
          host: ${{ secrets.ABAP_ENV_HOST }}
          username: ${{ secrets.ABAP_ENV_USER }}
          password: ${{ secrets.ABAP_ENV_PASS }}
          package: Z_MY_PACKAGE
```

## 8. Database

Tren Steampunk, database la **HANA Cloud** (SAP HANA as a Service).

| Tinh nang | Co san? |
|-----------|---------|
| HANA Cloud (column store) | ✅ |
| ABAP Dictionary (table) | ✅ |
| CDS View | ✅ |
| DCL (Access Control) | ✅ |
| AMDP | ✅ |
| Direct SQL (HANA) | ✅ (qua AMDP) |
| XCO library | ✅ |

## 9. API Consumption

Tren Steampunk, co the consume external APIs:

```abap
" 1. Tao Destination trong BTP Cockpit
" 2. Dung trong ABAP

DATA(lo_destination) = cl_http_destination_provider=>create_by_cloud_destination(
  i_name = 'MY_API_DESTINATION'
).

DATA(lo_client) = cl_web_http_client_manager=>create_by_http_destination( lo_destination ).
DATA(lo_response) = lo_client->execute( ).
```

## 10. License & Cost

| Plan | Gioi han | Gia (approx) |
|------|----------|------------|
| `standard` | 10 dev users, 10000 ABAP objects | $300-500/month |
| `premium` | Unlimited users, objects | Custom pricing |

## 11. Tich hop voi skill/agent khac

- So huu boi agent `sap-btp-admin-consultant-cloud` (BTP Platform Administration) — dispatch tu
  `sap-ask-consultant` khi cau hoi lien quan BTP admin/CF/Kyma; agent doc file nay them khi cau hoi
  cu the ve ABAP Environment / Steampunk infrastructure.
- `sap-extensibility` — bac thang extensibility chung (Custom Fields/Custom Business Objects/Cloud
  BAdI) van ap dung khi lam viec voi RAP tren ABAP Environment.
- `sap-clean-code` — naming convention Z/Y cho package, CDS view, class khi viet code tren Steampunk.
- `sap-cap-consultant-cloud` — de phan biet Steampunk (ABAP-native, chay thuan ABAP tren BTP) vs CAP
  (Node.js/Java, side-by-side) khi tu van kien truc extension tren BTP.
- `sap-abap-sql`, `sap-authorization`, `sap-rap-events` — kien thuc RAP/CDS/AMDP/authorization dung
  chung khi viet code ABAP tren Steampunk.

## 12. Nguon tham khao

- SAP Help: BTP ABAP Environment
- SAP Community: BTP Steampunk Node
- SAP Discovery Center: ABAP Environment service
- GitHub: SAP abap-environment-tooling
