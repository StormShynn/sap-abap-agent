# Module Experts — index

Module-agent = chuyên gia **tri thức** 1 phân hệ (tìm CDS/BO/API chuẩn), KHÔNG sinh code.
Logic chung: `../module-expert-process.md`. Mỗi agent đọc/ghi pack riêng (cơ chế "học").

## Core đang triển khai (8)

| Agent | Phân hệ | Pack | Catalog |
|-------|---------|------|---------|
| `AGENTS_FI` | Financial Accounting | `modules/FI.md` | `Phan_He_SAP_MD/FI.md` |
| `AGENTS_CO` | Controlling | `modules/CO.md` | `Phan_He_SAP_MD/CO.md` |
| `AGENTS_MM` | Materials Management | `modules/MM.md` | `Phan_He_SAP_MD/MM.md` |
| `AGENTS_SD` | Sales & Distribution | `modules/SD.md` | `Phan_He_SAP_MD/SD.md` |
| `AGENTS_LE` | Logistics Execution | `modules/LE.md` | `Phan_He_SAP_MD/LE.md` |
| `AGENTS_PP` | Production Planning | `modules/PP.md` | `Phan_He_SAP_MD/PP.md` |
| `AGENTS_PM` | Plant Maintenance | `modules/PM.md` | `Phan_He_SAP_MD/PM.md` |
| `AGENTS_QM` | Quality Management | `modules/QM.md` | `Phan_He_SAP_MD/QM.md` |

## Expert đặc biệt — tài sản DỰ ÁN (không phải SAP standard)

| Agent | Vai trò | Pack | Nguồn tra |
|-------|---------|------|-----------|
| `AGENTS_REUSE` | Tìm CDS/class/pattern **đã dựng sẵn trong dự án** để reuse/tham khảo | `../reusable-team-assets.md` | `source code/`, `PUB_ACME_CODE/` (read-only), `docs/stories/` |

→ Luôn hỏi `AGENTS_REUSE` **trước** khi function-agent viết class mới (ưu tiên reuse/reference).

## Phân hệ mới (18 còn lại: AP, BC, CA, CM, CRM, EC, FIN, FS, FT, LO, PLM, PPM, PSM, RE, SCM, SLC, SUS, TM)

Chưa tạo agent sẵn. Khi FS phát sinh → agent chính chạy **vòng "học phân hệ mới"**
(`module-expert-process.md`): tạo pack từ `_template.md` + verify nguồn SAP chính thống →
đăng ký vào bảng trên → (tuỳ chọn) tạo thin agent từ mẫu `AGENTS_FI.md`.

## Agent chính điều hướng thế nào

```
FS → nhận diện phân hệ (cds-by-module.md §3)
   → spawn AGENTS_<MODULE> → facts CDS/BO/API (verified, reuse asset nếu có)
   → spawn function-agent (AGENTS_API | Excel | PDF | skill scaffold) + facts → build code
```
FS đa phân hệ → spawn nhiều module-agent song song, gộp facts.
