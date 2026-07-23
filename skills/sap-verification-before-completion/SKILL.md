---
name: sap-verification-before-completion
description: |
  Nguyen tac bat buoc truoc khi bao "xong"/"da fix"/"hoat dong": phai co bang chung chay
  that (output lenh, log test, activation status), khong duoc suy tu viec "doc code thay hop ly".
  Dung cho moi loai: ABAP scaffold, MCP server (Python), script, cau hinh BTP.
when_to_use: |
  Truoc khi bao cao hoan thanh 1 task/feature/fix. Ap dung ca khi task "nho"/"chi sua 1 dong".
argument-hint: "[mo ta task vua lam]"
model: haiku
effort: low
tools: [Bash, Read, Grep]
---

# SAP Verification Before Completion

## Ly do

Du an nay tung co truong hop code "doc qua thi hop ly" nhung chua bao gio duoc chay that: MCP
stdio transport khong ton tai (chi in CLI help), thieu `await` trong Playwright auto-login,
`await` thua truoc ham dong bo — tat ca chi lo ra khi chay that qua 1 subprocess/JSON-RPC that,
khong phai luc doc lai code. Runtime va "doc thay on" la 2 thu khac nhau, dac biet voi code
async (Python) va code chi bao loi luc activate (ABAP).

## Quy tac

KHONG bao "xong"/"da sua"/"hoat dong roi" chi vi:
- Code bien dich/khong bao loi cu phap luc viet.
- Doc lai logic thay "co ve dung".
- Test tuong tu da tung pass truoc do (context khac co the khac).

PHAI co it nhat 1 trong:
- Output that cua lenh/script vua chay (khong phai suy doan output se the nao).
- Ket qua ABAP Unit test / ATC check that (khong phai "chac se pass").
- Activation status that trong ADT (khong phai "code nhin dung syntax la activate duoc").
- Voi MCP/Python: goi thu that qua CLI/subprocess, khong chi doc ham roi ket luan no chay dung.

## Vien co thuong gap

| # | Vien co | Phai lam |
|---|---|---|
| V1 | "Code nhin dung roi, chac chay duoc" | Chay that, dan output vao bao cao |
| V2 | "Sua 1 dong nho, khong can test lai" | Van chay lai it nhat luong lien quan truc tiep |
| V3 | "Async/await nhin co ve dung cu phap" | Chay that 1 request/subprocess that, xem co exception khong |
| V4 | "ABAP: file khong bao do gach loi trong editor" | Van phai activate that trong ADT — loi activation khac loi syntax editor |
| V5 | "Test da viet la du, khong can chay" | Chay test that, dan ket qua PASS/FAIL that vao bao cao |

## Ap dung theo loai task

| Loai | Bang chung can co |
|---|---|
| Scaffold ABAP (RAP/CDS) | Activate that trong ADT + `sap-atc-review` PASS |
| ABAP Unit test | Chay that qua ABAP Unit runner, dan ket qua |
| MCP server / Python | Chay subprocess/CLI that, xem output/exception that |
| Sua cau hinh BTP | `sap_ping`/lenh tuong ung chay that voi profile that |
| Fix bug (bat ky loai) | Tai hien loi truoc khi sua, xac nhan het loi sau khi sua — bang chay that ca 2 lan |

## Tich hop

- Skill `sap-finish-ticket` — dung skill nay o buoc cuoi truoc khi dong ticket.
- Skill `sap-systematic-debugging` — buoc "xac nhan het loi" cua debugging cung la ap dung
  nguyen tac nay.
