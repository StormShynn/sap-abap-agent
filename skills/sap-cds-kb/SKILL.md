---
name: sap-cds-kb
description: Tra cuu CDS view released cho SAP S/4HANA Cloud Public Edition qua MCP server cds-kb-mcp. Dung khi user can tim CDS view theo business meaning/ten SAP/module, can xem definition/fields/associations/source cua 1 CDS view cu the, hoac can kham pha taxonomy BO.
when_to_use: |
  "tim CDS view cho overdue invoices", "xem field cua view I_SalesDocument",
  "co CDS view nao cho purchase order khong".
effort: medium
model: haiku
---

# SAP CDS Knowledge Base (cds-kb-mcp)

Skill nay huong dan su dung **5 tools** cua MCP server `cds-kb-mcp` de tra cuu **7,355 CDS views**
released cho SAP S/4HANA Cloud Public Edition.

## Yeu cau

MCP server `cds-kb` phai duoc cau hinh (xem README.md -> Dang ky MCP servers). Server duoc host
remote, khong can cai dat local.

## Tools & Cach dung

### 1. search_cds — Tim CDS view theo business meaning

Day la tool chinh. Nhap query tu nhien hoac tu khoa SAP co dien (VBAK, BSEG...).

```json
search_cds({ query: "overdue customer invoices", module: "FI" })
```

| Tham so | Bat buoc | Mo ta | Vi du |
|---------|----------|-------|-------|
| `query` | ✓ | Tu khoa hoac cau hoi tu nhien | `"open purchase orders"` |
| `module` | | Loc module: FI, SD, MM, hoac ten: Finance, Sales | `"Sales"` |
| `lob` | | Line of Business (partial match) | `"finance"` |
| `bo` | | Business Object (partial match) | `"salesorder"` |
| `limit` | | So ket qua (1-50, mac dinh 10) | `15` |

**Vi du thuc te:**

```
User: "Tim CDS view cho customer invoices qua han"
Agent: search_cds({ query: "overdue customer invoices", module: "FI" })
```

**Module aliasing** (co the dung ten tu nhien thay vi code SAP):
| Ten code | Ten tu nhien |
|----------|-------------|
| FI | Finance |
| SD | Sales |
| MM | Procurement |
| CO | Controlling |
| PP | Production |
| HR | Workforce |
| WM | Logistics |
| CA | Cross-Application |

### 2. get_cds_view — Lay definition day du cua 1 CDS view

Dung sau khi search_cds tra ve ket qua, hoac khi biet chinh xac ten view.

```json
get_cds_view({ name: "I_SalesDocument", sections: ["metadata", "fields"] })
```

| Tham so | Bat buoc | Mo ta |
|---------|----------|-------|
| `name` | ✓ | Ten view chinh xac (khong phan biet hoa thuong) |
| `sections` | | Array: ["metadata", "fields", "associations", "source"]. Mac dinh = all |

**Pattern khuyen dung:**
1. `search_cds` → tim duoc view `I_CAOPENITEMLIST`
2. `get_cds_view({ name: "I_CAOPENITEMLIST", sections: ["metadata", "fields"] })` → xem field list
3. Neu can source: `get_cds_view({ name: "I_CAOPENITEMLIST", sections: ["source"] })`

### 3. get_views_by_tag — Liet ke view theo tag

Dung khi can danh sach xac dinh (khong mo ho nhu search).

```json
get_views_by_tag({ tag: "bo:salesorder", limit: 20 })
```

Tag pho bien:
| Loai tag | Vi du |
|----------|-------|
| `bo:<name>` | `bo:salesorder`, `bo:purchaseorder`, `bo:businesspartner` |
| `lob:<name>` | `lob:finance`, `lob:sales`, `lob:procurement` |
| `module:<code>` | `module:fi`, `module:sd`, `module:mm` |

### 4. get_taxonomy — Kham pha ban do ngu nghia

Tra ve 12 Lines of Business → 829 Business Objects, kem keywords + synonyms.

Dung khi:
- Can dinh huong truoc khi search
- Muon biet 1 BO co nhung view nao
- Muon tim tag hop le cho `get_views_by_tag`

```json
get_taxonomy()
```

### 5. kb_info — Kiem tra trang thai KB

Xem ban build, so view, nguon du lieu.

```json
kb_info()
```

## Pattern tra cuu theo nhu cau

### Khi user hoi "co CDS view nao cho X khong?"
1. Goi `search_cds({ query: "<mo ta nghiep vu>" })` hoac `get_views_by_tag({ tag: "bo:<name>" })`
2. Neu can chi tiet → `get_cds_view({ name: "<ten_view>" })`

### Khi user hoi "cho toi xem field list cua view ABC"
1. Goi `get_cds_view({ name: "ABC", sections: ["metadata", "fields"] })`

### Khi user hoi "SAP co CDS view nao cho Sales Order?"
1. `get_taxonomy()` → tim tag `bo:salesorder`
2. `get_views_by_tag({ tag: "bo:salesorder" })` → danh sach view lien quan
3. `get_cds_view({ name: "<ten_view>", sections: ["fields"] })` cho view chinh

### Khi user viet code ABAP can CDS view de SELECT
1. `search_cds({ query: "<nghiep vu can doc>" })` 
2. `get_cds_view({ name: "<ten_view>", sections: ["metadata", "fields"] })`
3. Ket hop voi kiem tra released API tren `api.sap.com`

## Luu y

- **CDS view khong phai released API** — chi la CDS view co dinh nghia. Kiem tra them tren `api.sap.com`
  neu can xac nhan 1 view co duoc phep dung trong ABAP Cloud hay khong.
- **Ten view phan biet hoa thuong** trong CDS (I_SalesDocument vs I_SALESDOCUMENT), nhung tool
  get_cds_view xu ly khong phan biet.
- **Du lieu duoc cache** local (ETag-based). Co the out-of-date so voi SAP release moi nhat.
- Neu can kiem tra version KB: `kb_info()`.
