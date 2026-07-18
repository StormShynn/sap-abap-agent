# Chuẩn định dạng tài liệu gửi KHÁCH HÀNG (TS / tích hợp / .docx)

<!-- (memory: customer-doc-docx-template) -->


> ⭐ **BẮT BUỘC** khi được yêu cầu "dựa vào template mẫu viết tài liệu TS/tích hợp để gửi khách hàng".
> Tài liệu gửi KH KHÔNG chỉ đúng nội dung — phải **đúng hình thức doanh nghiệp**: font, size, màu sắc,
> **logo, header, footer** giống hệt template mẫu (FPT/ACME). Sai hình thức = không gửi được cho KH.

## Nguyên tắc nội dung (GIỮ GỌN — không nhồi linh tinh cho KH) 🔴

- 🔴 **KHÔNG tự convert MD → `.docx` — PHẢI có yêu cầu RÕ của user** ("xuất docx"/"sinh file docx"). KHÔNG
  tự re-render sau khi sửa converter / sửa `.md` / "cho đồng bộ". Mặc định `.md` là nguồn được sửa; `.docx`
  chỉ sinh khi được yêu cầu.
- 🔴 **KHÔNG tự regenerate/ghi đè `.docx` user đã hoàn thiện**: file `.docx` bàn giao là artifact cuối,
  user hay chỉnh TAY trên docx (điền credential/password thật, bấm F9 số trang, ký tên) — thứ KHÔNG có
  trong `.md`. Re-render từ `.md` = **xoá hết** các chỉnh tay đó, KHÔNG có backup local (chỉ khôi phục qua
  OneDrive/SharePoint Version history). Sửa converter **≠** được phép re-render tất cả docx cũ. Trước khi
  ghi đè file đích **đã tồn tại** → **hỏi user (AskUserQuestion)**. Thử converter → xuất ra file tạm
  (scratchpad), không đè file thật. Lỡ đè → báo thật ngay + hướng Version history, KHÔNG dựng lại giả.
  (memory: `no-overwrite-finished-docx`)
- **Chỉ đưa vào tài liệu những gì KH CẦN**: đúng nội dung nghiệp vụ/kỹ thuật FS yêu cầu. KHÔNG tự bịa
  thêm mục, ghi chú nội bộ, disclaimer thừa, "mẹo", hướng dẫn thao tác cho dev… vào bản gửi KH.
- **Không chắc / cần hỏi → ghi NOTE trong file `.md`, KHÔNG generate docx vội**: đặt câu hỏi/giả định dưới
  dạng **HTML comment** `<!-- HỎI: ... -->` (hoặc `<!-- GIẢ ĐỊNH: ... -->`) ngay tại chỗ liên quan trong
  `.md`. Converter **tự bỏ qua HTML comment** (không render vào docx) → note chỉ để user đọc & review trước.
- **Quy trình**: soạn/sửa `.md` → nếu có điểm cần xác nhận thì để note `<!-- -->` + báo user review →
  **CHỜ user OK** → mới `md_to_docx_template.py` sinh `.docx`. KHÔNG sinh docx khi còn câu hỏi treo.
- Placeholder hợp lệ (vẫn hiển thị cho KH): auth user/pass chưa cấp = `*(NMS/Admin điền — chưa cấp)*`;
  field FS yêu cầu nhưng chưa có nguồn = `⚠ placeholder`. Đây là thông tin KH cần biết, KHÁC note nội bộ.

## Nguyên tắc
1. **Dùng đúng file `.docx` template mẫu làm gốc** — KHÔNG tạo docx trắng từ đầu. Template mẫu chuẩn:
   `TS/ACME_SAP_2026_TH_TS_SD_ZSD04_TichHopCRM_BusinessPartner_v1.0.docx` (bản Word đã duyệt của KH).
   Giữ nguyên các phần: **logo**, **header**, **footer** (số trang, tên dự án), **font mặc định**,
   **màu heading**, **style bảng**, **trang ký**.
2. **Cách làm (preserve styling)**: copy template `.docx` → mở bằng python-docx → **xoá nội dung body**
   (paragraph + table trong `document.body`) NHƯNG **giữ header/footer/logo/section** (nằm ở part riêng,
   không đụng) → ghi nội dung mới bằng **đúng style name** của template (Heading 1/2, Normal, table style).
   KHÔNG hardcode font rời rạc — dùng style của template để đồng nhất.
3. **Font/size/màu**: theo template (thường Times New Roman / Arial 11–12pt, heading màu xanh doanh nghiệp).
   Nếu template có theme màu riêng → giữ nguyên, không đổi.
4. **Header/Footer**: giữ logo ở header, tên tài liệu + số trang ở footer y như template.
5. **Kiểm tra trước khi gửi**: mở lại docx xác nhận logo hiện, header/footer đúng, heading/bảng đúng màu,
   trang ký đầy đủ. Nếu convert từ markdown làm mất style → sửa lại theo template, KHÔNG gửi bản lệch.

## Quy trình chuyển md → docx (giữ template) — ĐÃ CÓ SCRIPT
- Nội dung soạn ở markdown (`TS/*.md`) → convert sang `.docx` dùng template ZSD04 làm base.
- ⭐ **Script sẵn**: `python scripts/md_to_docx_template.py <template.docx> <input.md> <output.docx>`
  — mở template bằng python-docx, **xoá body, giữ nguyên header/footer/logo/section/styles**, ghi md
  bằng đúng style (Heading 1/2/3, Table Grid + shading header row, Consolas cho code). Verified giữ
  `header1.xml`/`footer1.xml`/`media` (logo).
- Ví dụ (ZMM05/06/07 dùng template ZSD04):
  `python scripts/md_to_docx_template.py "TS/ACME_SAP_2026_TH_TS_SD_ZSD04_*.docx" "TS/<md>" "TS/<out>.docx"`
- Validate sau khi tạo: skill `docx` `scripts/office/validate.py`. Mở lại kiểm logo/header/footer.
- ⚠️ **GOTCHA đánh số đầu mục**: style `Heading1/2/3` của template ZSD04 **có sẵn auto-numbering (`numPr`)**.
  Nếu chỉ set `pStyle=Heading2` mà gõ số thủ công "1. Tổng quan" → **double-number/loạn** (auto-number của
  style cộng thêm số tay, đếm cả heading front-matter). **Fix**: mỗi heading phải **tắt số kế thừa** bằng
  `numPr numId=0` (hàm `suppress_heading_numbering` trong `md_to_docx_template.py`) → giữ số thủ công khớp
  mục lục. Front-matter (Thông tin tài liệu/Quản lý thay đổi/Trang ký/Nội dung/Phụ lục) → không số.
- ⚠️ **MỤC LỤC = TOC field Word THẬT, không list gõ tay**: mục "## Nội dung" trong md → converter chèn
  **TOC field** (`{ TOC \o "1-3" \h \z \u }` qua `w:fldChar`/`w:instrText`, hàm `add_toc`) → Word tự dựng
  mục lục phân cấp (1, 1.1, 1.1.1) + **dot leader** + **số trang** giống chuẩn Word. Bỏ qua list "1. Tổng quan…"
  gõ tay bên dưới. **Sau khi mở file phải Ctrl+A → F9** (Update Field) để điền số trang (field mặc định hiện
  placeholder tới khi F9). List gõ tay KHÔNG có số trang, không auto-update → không dùng.
- ⚠️ **Heading level ↔ TOC**: đầu mục **đánh số** (`## 1.`, `### 1.1`) mới dùng **Heading style** (## → Heading 1,
  ### → Heading 2) để **vào TOC**; front-matter (không số) render **bold navy paragraph** (`frontmatter_label`,
  Pt13) — KHÔNG Heading style → **không lọt vào mục lục**. Nhờ vậy TOC chỉ chứa 1..N nội dung nghiệp vụ.
- ⚠️ **Font đồng bộ (tránh loạn size)**: body/inline `code`/bảng = **11pt** (kế thừa Normal template, KHÔNG set
  Pt(9) cho inline code — trước đây gây "chỗ 9 chỗ 11"); code block = 10pt Consolas; front-matter label + subtitle
  = 13pt navy; title = 16pt navy. Đừng hardcode size lẻ cho từng run.
- **Màu chuẩn ZSD04** (đã verify từ XML): heading + **header bảng nền navy `244061`**, **chữ header trắng `FFFFFF`** bold;
  tiêu đề/subtitle/intro **canh giữa** (title 16pt, subtitle 13pt, navy). Font Times New Roman. Script đã hardcode đúng các giá trị này.
- Nếu template gốc `.docx` đang **bị mở trong Word** (khoá) → python không đọc được: repack bản đã giải nén
  (`skill docx pack.py`) thành template tạm rồi generate; hoặc đóng Word trước.

## Nội dung bắt buộc của TS tích hợp API (gửi KH/đối tác)
- Mục **Xác thực** phải có **bảng tham số Username/Password** (Communication User) như ZSD04 — không chỉ ghi
  "Basic Auth" chung chung. Điền comm user thật khi đã cấp (vd CRM = `ZNFG_CRM`); chưa cấp → placeholder
  "(NMS/Admin điền — chưa cấp)". Đủ mục: Thông tin kết nối · **Xác thực (+ bảng user/pass)** · Request ·
  Bảng mapping field · Mã HTTP · Tham khảo.
- ⚠️ **Bảo mật**: credential thật (password comm user) ghi trong doc = nằm trong repo → nếu commit/push
  (nhất là ACME_LOCAL/GitHub) sẽ lộ. Chỉ ghi khi user chấp nhận; chia sẻ qua kênh an toàn; đổi pass định kỳ.
  Cân nhắc để password ở doc bản giao KH, KHÔNG commit vào git chung.

## Áp dụng ở đâu
- `AGENTS_API` (sinh Word integration doc — bước cuối pipeline): tài liệu gửi đối tác/KH phải theo chuẩn này.
- Bất kỳ yêu cầu "viết TS/tài liệu tích hợp theo template để gửi KH".
- ⭐ **Template cấu trúc rỗng (dùng lại "y chang")**: `TS/_TEMPLATE_TS_TichHopAPI_v1.0.md` — copy ra rồi
  điền `<...>`, GIỮ NGUYÊN khung mục 1–10 + front-matter + Phụ lục. Có sẵn hướng dẫn từng mục dạng
  HTML comment (converter tự bỏ). Bản mẫu ĐÃ ĐIỀN tham khảo: `TS/ACME_SAP_2026_TH_TS_SD_ZSD04_*.md`.

## Checklist (trước khi giao KH)
- [ ] Logo hiển thị đúng ở header.
- [ ] Header/Footer (tên dự án, số trang) đúng template.
- [ ] Font + size + màu heading giống template.
- [ ] Style bảng (viền, màu header row) đúng template.
- [ ] Trang ký (FPT + ACME) đầy đủ.
- [ ] Nội dung theo cấu trúc mục của template mẫu (ZSD04).
