# Xử lý khi API / BO / CDS cần dùng CHƯA released (missing released API)

> Khi verify (`acme_lookup.py`) báo object **không released** hoặc **không tồn tại** → ĐỪNG dead-end
> bằng `[Unverified]` rồi dừng. Có **cây quyết định mitigation** chuẩn SAP. Đây là bước tiếp theo tự nhiên
> SAU bước "verify released" của module expert.

Nguồn tham chiếu SAP chính chủ: [rap640 — Mitigating Missing Released APIs](https://github.com/SAP-samples/abap-platform-rap640),
[nominated-apis-consumption (Tier-2 wrapper)](https://github.com/SAP-samples/abap-platform-nominated-apis-consumption),
[ABAP Extensibility Guide (clean core)](https://community.sap.com/t5/technology-blog-posts-by-sap/abap-extensibility-guide-clean-core-for-sap-s-4hana-cloud-august-2025/ba-p/14175399).

## Nguyên tắc theo loại tenant (QUAN TRỌNG — đừng nhầm)

- **S/4HANA Cloud PUBLIC Edition** (= tenant ACME `project3.s4hana.cloud.sap`): **strict released-only** +
  Developer Extensibility. **KHÔNG có** classic Tier-2 wrapper / nominated API. Object on-prem (T156,
  `BAPI_*` chưa released, table DDIC raw) **không dùng được** — ATC reject.
- **S/4HANA Cloud PRIVATE Edition / on-prem**: có thêm **nominated API + Tier-2 wrapper** (bọc API cổ điển
  thiếu C1 trong 1 class Tier-2 rồi expose lại). [Inference] Không áp dụng cho tenant Public của bạn.

→ Với tenant Public, đi cây quyết định dưới; **bỏ qua** nhánh Tier-2 (chỉ ghi chú cho dự án Private sau này).

## Cây quyết định (Public Cloud) — thứ tự ưu tiên

```
Object X cần dùng nhưng acme_lookup báo NOT released / not found
   │
   ├─① Có RELEASED ALTERNATIVE không? (view/API khác trả cùng data)
   │      → acme_lookup.py X --search  · pmc-reuse-by-module.md · Phan_He_SAP_MD/<MOD>.md
   │      → có → DÙNG cái released. Xong.
   │
   ├─② Có STANDARD OData/SOAP API (whitelist Public Cloud) không?
   │      → api.sap.com filter "SAP S/4HANA Cloud Public Edition" → tìm API_* SRV
   │      → gọi qua HTTP client + Communication Arrangement (KHÔNG cần released ABAP object)
   │      → phù hợp khi: BO EML không đủ / cần số chứng từ ngay (late numbering) / action cross-LUW
   │      → có → DÙNG OData API. (VD ZSD06 bên dưới.)
   │
   ├─③ Chỉ cần THÊM FIELD / logic nhỏ trên object standard?
   │      → Key-user extensibility (Custom Fields & Logic) / released BAdI enhancement spot
   │      → không cần code core.
   │
   └─④ Không có đường nào ở trên
          → [Unverified] + open question trong INTAKE §6 + ESCALATE khách hàng.
          → TUYỆT ĐỐI KHÔNG: bịa tên released, dùng object on-prem, direct SQL vào bảng standard.
```

## Bảng mitigation nhanh

| Tình huống | Public Cloud — làm gì | Ghi chú |
|---|---|---|
| CDS view cần chưa released | Tìm view released tương đương (`--search`); hoặc build ZI_* select from view released khác | KHÔNG select from view chưa released |
| BO interface (EML) chưa released / thiếu | Standard OData API (②) hoặc released BO khác | — |
| BO EML released nhưng **late numbering** (không lấy được số trong handler) | **OData API** commit LUW riêng → trả số ngay (VD ZSD06) | Cấm COMMIT ENTITIES trong behavior; EML MODIFY chỉ có %pid |
| BAPI on-prem quen (BAPI_GOODSMVT_CREATE, T156…) | Released CDS/API tương đương (I_GoodsMovementType, API_MATERIAL_DOCUMENT_SRV) | on-prem object = ATC reject |
| Chỉ thêm field vào chứng từ standard | Key-user Custom Fields, hoặc released BAdI | Không cần dev core |
| Không có gì | [Unverified] + escalate KH | Đừng bịa, đừng cắt góc (R2) |

## Ví dụ thật đã áp dụng trong dự án

- **ZSD06** (post Goods Issue): `I_MaterialDocumentTP` EML → **late numbering** (số gán ở save phase,
  handler chỉ có `%pid`, cấm `COMMIT ENTITIES`) → **chuyển nhánh ②**: gọi released OData
  `API_MATERIAL_DOCUMENT_SRV` (qua core `ZCL_CORE_GOODS_MVT_POSTER`) → commit LUW riêng, trả số Material
  Document synchronous. (ADR-0021.)
- **ZMM07** (đọc PR/SA): dùng released `I_*` CDS qua custom entity + query provider — nhánh ① (released alternative).

## Wiring trong harness

- **Module expert** (`module-expert-process.md` bước 4): khi verify báo chưa released → chạy cây quyết định
  này thay vì chỉ flag. Trả về mitigation đã chọn (nhánh ①–④) trong facts.
- **`/sap-atc-review`** dòng **R18**: "API chưa released → bỏ/bịa" là cắt góc → phải theo cây này.
- **AGENTS_DOC / AGENTS_Excel** khi tạo chứng từ: nếu BO EML vướng late numbering → nhánh ② (OData API).

## Đừng nhầm (anti-pattern)

- ❌ Bịa tên view "gần đúng" cho compile (R2).
- ❌ Dùng object on-prem vì "quen" (R3).
- ❌ Tier-2 wrapper trên Public Cloud (chỉ Private Cloud).
- ❌ Direct SQL INSERT/UPDATE bảng standard SAP.
