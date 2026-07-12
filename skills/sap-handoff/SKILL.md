---
name: sap-handoff
description: |
  Compact phien lam viec hien tai (hoi thoai + git state + artifact da tao) thanh 1 file
  HANDOFF.md de session Claude Code moi (context rong hoac sau khi bi compact) doc vao va
  tiep tuc ngay, khong can doc lai toan bo lich su chat.
  Dung khi context sap day, sap chuyen may/nghi giua chung, hoac truoc khi dong may ma ticket
  chua xong.
  KHONG dung khi ticket da xong (dung sap-finish-ticket) hoac task qua ngan (<10 luot chat,
  chua co state gi dang ke de ban giao).
when_to_use: |
  "handoff", "ban giao phien lam viec", "tom tat lai de session sau lam tiep", "context sap day
  qua roi", "tao HANDOFF.md", "resume lai ticket X tu session truoc".
argument-hint: "[ten-ticket-hoac-chu-de] [in-chat (mac dinh) | save]"
model: sonnet
effort: medium
tools: [Read, Write, Bash, Glob, Grep]
---

# SAP Handoff - Ban giao phien lam viec giua cac session

## Khi nao dung

- ✅ Context window sap day (>70-80%), can ket thuc session nhung ticket/task chua xong.
- ✅ Sap ngung lam viec (het gio, chuyen sang task khac), muon quay lai chinh xac cho da dung.
- ✅ Truoc khi chay `/compact` hoac dong Claude Code ma con viec dang do dang.
- ❌ Ticket da PASS het checklist (`sap-finish-ticket` READY) - khong can handoff, ticket xong roi.
- ❌ Task ngan (<10 luot chat), chua co quyet dinh/state nao dang gia tri de mat.

## Nguyen tac

Ap dung `sap-verification-before-completion`: HANDOFF.md phai ghi **trang thai that** (da
activate/chua, test da chay/chua), khong suy doan "chac la xong". Session sau doc HANDOFF.md
phai tin duoc noi dung, khong phai doi chieu lai tu dau.

Tham chieu artifact co san **bang duong dan**, KHONG copy paste lai noi dung (tranh trung lap
voi `TECHNICAL_SPEC.md`, `ATC_REVIEW.md`, `manifest.yaml` cua `sap-scaffold-context-summary`,
git diff/commit). HANDOFF.md la lop dieu huong (index), khong phai lop luu tru.

**Mac dinh KHONG ghi file** - chi in toan bo noi dung handoff ngay trong cau tra loi (chat).
Ly do: skill nay duoc phan phoi qua plugin cho nhieu user khac nhau; field `tools`/
`allowed-tools` trong frontmatter KHONG chan duoc Write (chi la auto-approve, xem
code.claude.com/docs/en/skills muc "Pre-approve tools for a skill") - cach chan chac chan
DUY NHAT la khong goi Write trong luong mac dinh. Chi ghi ra file khi user yeu cau ro rang
("luu file", "save", "ghi ra de session sau doc").

## Vi tri luu file

`<agent-home>` = thu muc co dinh theo may (KHONG phai project dang mo), mac dinh
`%USERPROFILE%\.sap-abap-agent\` (Windows) / `~/.sap-abap-agent/` (macOS/Linux), override qua
`SAP_ABAP_AGENT_HOME`. Lay duong dan da resolve bang
`python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" <subpath>`.

| Truong hop | Duong dan |
|---|---|
| Dang lam 1 ticket (co `out/<ticket>/`) | `<agent-home>/sessions/<ticket>/HANDOFF.md` |
| Lam viec chung (dev plugin, khong co ticket) | `<agent-home>/handoff/<YYYY-MM-DD>-<slug>.md` |

Ca 2 truong hop nam trong `<agent-home>` - state ca nhan cua nguoi dung plugin (khong phai cua
project SAP dang mo), va khi dev/test ngay trong repo nay (`SAP_ABAP_AGENT_HOME` tro vao
`.sap-abap-agent/` cua repo) thi da co san trong `.gitignore`.

## Quy trinh

### Buoc 1: Kiem tra HANDOFF.md da ton tai chua

`Glob`/`Read` duong dan o tren. Neu da co - doc truoc, cap nhat (append tien do moi + sua
"Buoc tiep theo"), KHONG ghi de mat lich su "Da thu & fail" cu (van con gia tri).

### Buoc 2: Thu thap git state that

```bash
git status
git diff --stat
git log --oneline -10
```

Dung output that (khong doan) cho muc "Tien do hien tai".

### Buoc 3: Xac dinh artifact da co - chi ghi duong dan

Kiem tra (tuy ticket): `out/<ticket>/TECHNICAL_SPEC.md`, `out/<ticket>/ATC_REVIEW.md`,
`out/<ticket>/FINISH_CHECKLIST.md`, `<agent-home>/sessions/<ticket>/scaffold/manifest.yaml`.
Neu co - chi ghi 1 dong tham chieu, KHONG paste noi dung.

### Buoc 4: Redact du lieu nhay cam

TRUOC khi ghi file - quet noi dung dinh ghi, loai bo: client_secret, token, password, cookie,
API key, thong tin ca nhan khach hang. Neu khong chac chan 1 chuoi co phai secret khong -
redact (thay bang `<redacted>`), khong doan la an toan.

### Buoc 5: In noi dung handoff ngay trong chat (mac dinh - KHONG ghi file)

In toan bo template ben duoi truc tiep trong cau tra loi, trong 1 code block markdown de user
de copy. KHONG goi `Write` o buoc nay tru phi da sang Buoc 6.

```markdown
# Handoff - <ten-ticket-hoac-chu-de>

**Ngay**: <YYYY-MM-DD>
**Session**: <so luot chat uoc tinh, model dang dung>

## Muc tieu
<1-3 dong: dang lam gi, cho ai, tai sao>

## Tien do hien tai (bang chung that, xem git state Buoc 2)
- [x] <viec da xong, co bang chung>
- [ ] <viec dang do dang - noi ro dang o buoc nao>
- [ ] <viec chua bat dau>

## Da thu & that bai (KHONG lap lai)
| Cach da thu | Ket qua | Ly do fail |
|---|---|---|
| <approach 1> | Fail | <nguyen nhan cu the> |

## Buoc tiep theo (thu tu uu tien)
1. <buoc cu the, kem file/lenh can chay>
2. ...

## Artifact lien quan (duong dan, KHONG paste noi dung)
- `out/<ticket>/TECHNICAL_SPEC.md`
- `<agent-home>/sessions/<ticket>/scaffold/manifest.yaml`
- Git: `<commit hash gan nhat lien quan>`

## Skill/agent goi y cho session sau
- `sap-<module>-consultant-cloud` - <ly do>
- `sap-atc-review` - <ly do>

## Resume prompt (paste vao session moi)
> Doc `<agent-home>/sessions/<ticket>/HANDOFF.md` roi tiep tuc tu "Buoc tiep theo".
```

### Buoc 6: Chi ghi file khi user yeu cau ro rang

Neu (va chi neu) user noi ro "luu file"/"save"/"ghi ra file"/"luu lai de session sau doc" -
luc do moi `Write` vao duong dan o muc "Vi tri luu file" (Buoc 4 da redact xong noi dung).
Neu user chi noi "handoff giup minh" / "tom tat lai di" ma khong noi ro luu file - dung o
Buoc 5, khong tu y ghi file.

### Buoc 7: Bao duong dan cho user (chi khi co ghi file)

Neu da ghi file o Buoc 6 - in ra duong dan file vua ghi + "Resume prompt" de user copy vao
session moi. Neu chi in chat (Buoc 5) - "Resume prompt" da nam san trong noi dung in ra roi,
khong can lam gi them.

## Vien co thuong gap

| # | Vien co | Phai lam |
|---|---|---|
| H1 | "Tom tat ca hoi thoai vao HANDOFF" | Chi tom tat, tham chieu artifact bang duong dan, khong duplicate noi dung day |
| H2 | "Ghi 'da xong' vi code nhin on" | Ap dung `sap-verification-before-completion` - phai co bang chung chay that |
| H3 | "Copy nguyen secret/token vao cho de nho" | Luon redact - HANDOFF.md khong phai noi luu secret |
| H4 | "Ghi de HANDOFF.md cu hoan toan" | Doc truoc, giu lai "Da thu & fail" cu, chi cap nhat phan tien do/next step |
| H5 | "Cu goi Write luon cho tien, user can gi thi da co san" | KHONG - mac dinh chi in chat (Buoc 5); chi Write khi user noi ro "luu file"/"save" (Buoc 6) |
| H6 | "`tools:`/`allowed-tools` trong frontmatter da 'khoa' Write roi, yen tam" | Sai - field nay chi auto-approve, KHONG chan. Kiem soat that nam o prose (Buoc 5/6), khong phai frontmatter |

## Tich hop

- Skill `sap-scaffold-context-summary` - neu dang scaffold, tham chieu `manifest.yaml` co san
  thay vi ghi lai summary layer trong HANDOFF.md.
- Skill `sap-finish-ticket` - neu checklist da READY, dung skill do de dong ticket, khong can
  handoff nua.
- Skill `sap-verification-before-completion` - nguyen tac "bang chung chay that" ap dung cho
  muc "Tien do hien tai".
- Skill `sap-daily-learner` - co the ghi 1 dong episodic (`memory/episodic/index.jsonl`) danh
  dau session bi ngat quang, giup truy vet sau nay.

## Luu y

- ⚠️ KHONG bao gio ghi secret/token/password vao HANDOFF.md, ke ca "tam thoi" - file nay co the
  bi doc boi session/nguoi khac.
- 💡 Neu ticket dung `out/<ticket>/`, dat handoff cung ten `<ticket>` de cross-reference toan bo
  pipeline (INTAKE -> TECHNICAL_SPEC -> scaffold -> review -> test -> finish -> handoff neu ngat
  quang giua chung).
- 🔗 HANDOFF.md la file tam/ca nhan (`<agent-home>`, xem muc "Vi tri luu file"), khong phai
  deliverable, khong commit, khong dua vao `out/<ticket>/` (thu muc do la deliverable cho khach hang).
