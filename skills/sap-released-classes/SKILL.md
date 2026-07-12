---
name: sap-released-classes
description: Danh muc cac class ABAP released cho ABAP Cloud tren SAP S/4HANA Cloud Public Edition va BTP ABAP Environment (Steampunk). Dung khi can biet class nao duoc phep dung cho UUID, JSON, email, logging, parallel processing, encryption, date/time.
when_to_use: |
  "class nao de tao UUID trong ABAP Cloud", "JSON serialize trong ABAP",
  "send email trong cloud", "lap lich job ABAP", "ma hoa du lieu trong ABAP Cloud".
argument-hint: "[chuc nang can tim: UUID, JSON, email, logging, parallel, encryption, date]"
effort: medium
model: sonnet
tools: [Read, Grep, Glob, WebFetch]
---

# Released ABAP Classes — ABAP Cloud

Danh muc cac class ABAP duoc SAP release cho ABAP Cloud. Khi viet code tren S/4HANA Cloud Public Edition
hoac BTP ABAP Environment, CHI duoc dung cac class trong danh muc nay.

## UUID

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_uuid_factory` | `create_system_uuid_x16( )` | Tao UUID 16 byte (raw) |
| `cl_uuid_factory` | `create_system_uuid_c32( )` | Tao UUID 32 ky tu |
| `cl_uuid_factory` | `create_system_uuid_c36( )` | Tao UUID 36 ky tu (co dau gach) |
| `cl_abap_uuid` | `create_uuid_x16( )` | Alternative (static) |
| `cl_abap_uuid` | `create_uuid_c32( )` | Alternative (static) |

## JSON

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_abap_json` | `parse( json )` | Parse JSON string -> ABAP data |
| `cl_abap_json` | `serialize( data )` | Serialize ABAP data -> JSON |
| `xco_cp_json` | `parse( )` / `stringify( )` | XCO alternative |
| `/ui2/cl_json` | `deserialize( )` / `serialize( )` | UI JSON (truyen thong, khuyen dung XCO) |

## Email & Communication

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_bcs_mail_message` | `create( )` | Tao email message |
| `cl_bcs_mail_message` | `add_recipient( )`, `set_subject( )`, `set_body( )` | Cau hinh email |
| `cl_bcs_mail_send_manager` | `send_to_mta( )` | Gui email qua MTA |
| `cl_bcs_convert` | `convert_string_to_bcs_binary( )` | Convert attachment |
| `cl_http_destination_provider` | `create_by_comm_arrangement( )` | HTTP destination tu Communication Arrangement |
| `cl_http_destination_provider` | `create_by_cloud_destination( )` | HTTP destination tu BTP destination |
| `cl_web_http_client_manager` | `create_by_http_destination( )` | HTTP client tu destination |

## Logging

| Class | Method | Mo ta |
|-------|--------|-------|
| `if_abap_behv_log` | interface | Application log cho RAP BO |
| `cl_abap_log` | `add( )` / `open( )` / `close( )` | Simple log |
| `if_abap_bp_screen_log` | interface | Log cho Business Partner screen |

## Parallel Processing

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_abap_parallel` | `run( )` | Run tasks song song |
| `cl_abap_parallel` | `run_on_server_group( )` | Run tren server group |
| `cl_abap_task` | `run( )` | Single task (internal session) |
| `cl_abap_task_chain` | `add( )`, `run( )` | Chain tasks |

## Encryption & Security

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_abap_encrypt` | `encrypt( )` / `decrypt( )` | AES encryption |
| `cl_abap_hash` | `hash( )` | SHA-1 / SHA-256 / MD5 |
| `cl_abap_base64` | `encode( )` / `decode( )` | Base64 encode/decode |
| `cl_abap_pgp` | `encrypt( )` / `sign( )` | PGP encryption |

## Date & Time

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_abap_context_info` | `get_system_date( )` | System date (thay `sy-datum`) |
| `cl_abap_context_info` | `get_system_time( )` | System time (thay `sy-uzeit`) |
| `cl_abap_context_info` | `get_user_time_zone( )` | User time zone |
| `cl_abap_utclong` | utilities | UTCLONG timestamp operations |
| `xco_cp_system` | `get_date( )` / `get_time( )` | XCO date/time |

## Number Range

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_numberrange_runtime` | `number_get( )` | Lay so tu number range object |
| `cl_numberrange_runtime` | `number_check( )` | Kiem tra so |

## File Handling

| Class | Method | Mo ta |
|-------|--------|-------|
| `cl_abap_string_utilities` | `split( )`, `join( )` | String operations |
| `cl_abap_string_utilities` | `to_upper( )`, `to_lower( )` | Case conversion |
| `xco_cp_string` | methods | XCO string utilities |

## RAP Runtime

| Class / Interface | Mo ta |
|-------------------|-------|
| `if_abap_behv_runtime` | Base RAP runtime |
| `if_abap_behv_entity_data` | Entity data access |
| `if_abap_behv_context` | Context info (user, date) |
| `cl_abap_behv_behavior_handler` | Behavior handler base |
| `cl_abap_behv_superclass` | Superclass cho RAP BO classes |

## Nguon tham khao

- ABAP Cloud documentation on SAP Help Portal
- `xco_cp` library reference
- API Business Hub: `https://api.sap.com`
