---
name: sap-docs-research
description: Tra cuu tai lieu SAP tong hop qua MCP server mcp-sap-docs — SAP Help, SAP Community, SAP Accelerator Hub, SAP Fiori App Library, Clean Core Released Objects, ABAP feature matrix. Dung khi user can tra cuu SAP notes, SAP Community Q&A, kham pha API tren Accelerator Hub, xem Fiori app reference, hoac kiem tra ABAP syntax support.
when_to_use: |
  "tra cuu SAP note ve loi X", "tim API tren Accelerator Hub cho Y", "Fiori app nao cho Z",
  "FOR TABLE ITERATION co tu ban ABAP nao".
effort: medium
model: haiku
---

# SAP Docs Research (mcp-sap-docs)

Skill nay huong dan su dung MCP server `mcp-sap-docs` de tra cuu tai lieu SAP tong hop tu nhieu
nguon: offline docs, SAP Help Portal, SAP Community, SAP Accelerator Hub, SAP Fiori App Reference
Library, Clean Core Released Objects, va ABAP feature matrix.

## Yeu cau

MCP server `mcp-sap-docs-btp` phai duoc cau hinh (xem README.md -> Dang ky MCP servers). Server duoc
host remote, khong can cai dat local.

Neu co `SAP-API-HUB-KEY`, cac tool `sap_accelerator_hub_*` se hoat dong day du. Neu khong co, cac
tool khac van chay binh thuong.

## Tools & Cach dung

### 1. search — Tra cuu SAP Help Portal + offline docs

Tim kiem tai lieu SAP Help chinh thong va offline docs (SQLite BM25 + semantic embeddings).

```json
search({ query: "how to create sales order with reference", maxResults: 5 })
```

| Tham so | Bat buoc | Mo ta | Vi du |
|---------|----------|-------|-------|
| `query` | ✓ | Tu khoa hoac cau hoi tu nhien | `"ABAP Cloud CDS view"` |
| `maxResults` | | So ket qua (mac dinh 5) | `10` |

### 2. fetch — Lay chi tiet 1 document

```json
fetch({ path: "/docs/abap-cloud/abap-cloud.html" })
```

| Tham so | Bat buoc | Mo ta |
|---------|----------|-------|
| `path` | ✓ | Duong dan tu SAP Help (lay tu ket qua search) |

### 3. sap_community_search — Tim kiem SAP Community

Tra cuu SAP Community Q&A va blog posts de tim giai phap cho cac van de thuc te.

```json
sap_community_search({ query: "error when activating CDS view", maxResults: 5 })
```

| Tham so | Bat buoc | Mo ta |
|---------|----------|-------|
| `query` | ✓ | Cau hoi hoac van de can tim | 
| `maxResults` | | So ket qua (mac dinh 5) |

**Dung khi:** user gap loi, can tim huong giai quyet tu cong dong SAP.

### 4. sap_search_objects — Tra cuu Clean Core Released Objects

Tra cuu cac ABAP object duoc SAP release cho ABAP Cloud (class, interface, CDS view, function
module, BAPI...).

```json
sap_search_objects({ query: "cl_abap_context_info", maxResults: 5 })
```

| Tham so | Bat buoc | Mo ta |
|---------|----------|-------|
| `query` | ✓ | Ten hoac pattern object ABAP |
| `maxResults` | | So ket qua (mac dinh 5) |

**Dung khi:** user can kiem tra 1 class/interface co duoc release cho ABAP Cloud khong, hoac can tim
API thay the cho 1 cu phap bi cam.

### 5. abap_feature_matrix — Kiem tra ABAP syntax support

Kiem tra 1 ABAP statement / feature co duoc support tu ABAP version nao.

```json
abap_feature_matrix({ query: "FOR TABLE ITERATION" })
```

| Tham so | Bat buoc | Mo ta |
|---------|----------|-------|
| `query` | ✓ | ABAP statement hoac feature name |

**Dung khi:** user can biet 1 cau lenh ABAP co tu ABAP 7.40 / 7.50 / 7.54 hay khong.

### 6. sap_accelerator_hub_* — Kham pha SAP API Hub

Tools: `sap_accelerator_hub_search`, `sap_accelerator_hub_get_api`, `sap_accelerator_hub_get_artifact`

Tim kiem API, OData service, SOAP, REST tren SAP Accelerator Hub.

```json
sap_accelerator_hub_search({ query: "SalesOrder", type: "API" })
```

| Tham so | Mo ta |
|---------|-------|
| `query` | Tu khoa tim kiem |
| `type` | Loai: API, Integration, Event |

### 7. sap_fiori_library_* — Tra cuu Fiori App Reference

Tools: `sap_fiori_library_search`, `sap_fiori_library_get_app`

Tra cuu thong tin standard Fiori apps — app ID, tile, semantic object, OData service dependency.

```json
sap_fiori_library_search({ query: "Manage Sales Order" })
sap_fiori_library_get_app({ appId: "F2249" })
```

### 8. sap_discovery_center_* — BTP Services & Pricing

Tools: `sap_discovery_center_search`, `sap_discovery_center_get_service`

Kham pha BTP services, regions, pricing.

```json
sap_discovery_center_search({ query: "HANA Cloud" })
```

### 9. abap_lint — Kiem tra chat luong code ABAP

Phan tich tinh ABAP code (ABAP variant) — kiem tra naming, performance, security.

```json
abap_lint({ code: "SELECT * FROM mara INTO TABLE @data(lt_mara)." })
```

## Pattern tra cuu theo nhu cau

### SAP Notes / loi runtime
```json
sap_community_search({ query: "<mo ta loi / SAP Note number>", maxResults: 5 })
```

### Kiem tra 1 class co duoc release cho cloud khong
```json
sap_search_objects({ query: "<ten_class>" })
```

### Tim API cho tich hop
1. `sap_accelerator_hub_search({ query: "<nghiep vu>", type: "API" })`
2. `sap_accelerator_hub_get_api({ ... })` de xem chi tiet

### Kiem tra ABAP statement co hop le khong
```json
abap_feature_matrix({ query: "<statement>" })
```

### Tim Fiori app thay the cho transaction
```json
sap_fiori_library_search({ query: "<ten transaction hoac nghiep vu>" })
```

## Luu y

- **SAP-API-HUB-KEY khong bat buoc** — neu thieu, `sap_accelerator_hub_*` tools bi gioi han nhung
  cac tool khac van dung.
- **Offline docs** duoc index san trong SQLite database, co the khong phan anh release moi nhat
  (SAP ra 4 ban/nam).
- **sap_community_search** tra ve Q&A tu SAP Community — khong phai SAP Note chinh thong.
- **sap_search_objects** chi tra ve released objects — neu 1 object khong xuat hien, co nghia la
  chua duoc release cho ABAP Cloud.
