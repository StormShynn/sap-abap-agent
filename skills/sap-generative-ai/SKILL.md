---
name: sap-generative-ai
description: |
  Huong dan Generative AI Hub, Joule, ISLM / prompt template, va goi AI API tu ABAP Cloud
  (S/4HANA Cloud Public Edition / BTP ABAP). Dung khi user hoi Joule, GenAI Hub, prompt,
  ISLM, LLM tu ABAP, AI side-by-side tren BTP.
when_to_use: |
  "Joule ABAP", "Generative AI Hub", "ISLM prompt", "goi LLM tu ABAP Cloud",
  "AI Hub destination", "prompt template ABAP", "GenAI side-by-side CAP".
argument-hint: "[cau hoi ve GenAI Hub / Joule / ISLM / prompt / ABAP AI]"
effort: medium
model: sonnet
---

# Generative AI Hub / Joule / ISLM — ABAP Cloud

## 1. Phan biet nhanh

| Surface | Vai tro | Khi dung |
|---------|---------|----------|
| **Joule** | Digital assistant SAP (UI) | End-user hoi trong Fiori / Launchpad |
| **ISLM** | Intelligent Scenario Lifecycle Management — prompt / scenario lifecycle | Quan ly prompt template, version, ground scenario |
| **Generative AI Hub (BTP)** | Model gateway (orchestration, grounding) | Side-by-side: CAP/Node/Java goi model; ABAP goi qua destination/API |
| **In-app ABAP AI APIs** | Class/API released tren ABAP Cloud (neu co tren tenant) | Logic trong RAP/class goi AI **chi** qua API released |

**Nguyen tac Clean Core:** uu tien released API / Communication Arrangement / Destination.
Khong goi HTTP “tran” toi vendor LLM tu ABAP neu SAP da cung cap Hub/orchestration.

## 2. Khi nao Joule vs GenAI Hub

- **Joule**: UX chat, insights san pham — khong thay the custom RAP logic.
- **GenAI Hub**: ban can model cho use-case rieng (tom tat PO, classify ticket, generate text)
  tu CAP **hoac** ABAP qua Hub orchestration.
- **ISLM**: ban can quan ly prompt template / scenario lifecycle trong landscape SAP
  (khong hardcode prompt dai trong class).

Neu user hoi “viet skill Joule plugin” — day la product SAP, khong pham vi scaffold ABAP.
Neu “goi AI tu ZCL_*” → Hub + destination + released consumer pattern (duoi).

## 3. Luong goi AI tu ABAP Cloud (khuyen dung)

```text
ABAP Cloud (class / RAP determination)
  → Destination (BTP / Comm. Arrangement)
  → Generative AI Hub orchestration
  → Model response
  → Map vao RAP field / message / outbound event
```

Checklist:

1. Xac nhan edition: `s4hc_(public)` / BTP ABAP — xem `sap-deployment-target`.
2. Tao / dung Destination toi GenAI Hub (BTP Cockpit) — `sap-btp-setup` neu loi auth.
3. Prompt: uu tien ISLM template (versioned) thay vi string hardcode trong class.
4. Input: chi gui du lieu can thiet; **cam** PII/secret trong prompt log.
5. Output: validate / schema-check truoc khi ghi DB (RAP validation).
6. Fail-open nghiep vu: AI fail → message ro, khong silent corrupt data.
7. ATC / security: xem `sap-security-review` (khong log full prompt co du lieu nhay cam).

## 4. Side-by-side (CAP) vs in-app

| Pattern | Stack | Ghi chu |
|---------|-------|---------|
| Side-by-side | CAP + GenAI Hub SDK / orchestration | Scaffold: `sap-scaffold-cap`; kien truc: `sap-cap-consultant-cloud` |
| In-app | ABAP Cloud + Destination + Hub | Chi dung API/released object tren tenant |
| Event-driven | RAP event → Mesh → CAP AI worker | Xem `sap-rap-events` |

## 5. Prompt / ISLM thuc hanh

- Mot prompt = mot nhiem vu (classify / summarize / extract) — khong “god prompt”.
- Dat ten template theo ticket/module (`ZMM_PO_SUMMARY_V2`).
- Grounding: uu tien data da authorize (OData/CDS user context), khong dump toan bang.
- Doi A/B version qua ISLM; ghi version vao log nghiep vu (khong ghi raw prompt neu cam).

## 6. Released API

Chi liet ke class/API **da xac nhan released** tren tenant (ADT / Cloudification Repository /
`sap-docs-research`). Neu chua verify: **hoi user** + tra cuu docs — khong doan ten class.

Cap nhat danh muc chung: `sap-released-classes` (muc AI — chi khi da verify).

## 7. Anti-patterns

- Goi OpenAI/Anthropic truc tiep tu ABAP bang API key hardcode.
- Bo authorization check vi “AI se loc”.
- Ghi ket qua AI vao DB khong validation.
- Dung Joule thay the ATC / unit test / finish evidence.

## Cross-links

- Ket noi BTP / destination: `sap-btp-setup`
- Extensibility Clean Core: `sap-extensibility`
- Tra cuu Help/Notes: `sap-docs-research`
- CAP scaffold: `sap-scaffold-cap`
- RAP events toi AI worker: `sap-rap-events`

## Nguon

- SAP Help: Generative AI Hub, Joule, ISLM
- SAP Community: ABAP Cloud + GenAI patterns
- `sap-docs-research` / MCP `mcp-sap-docs-btp` khi can URL moi nhat
