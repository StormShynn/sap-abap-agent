---
name: sap-cpi-cloud
description: Kien thuc CPI chi tiet — iFlow pattern, adapter config, mapping (XPath/XSLT/Groovy), API Management, Edge Cell, monitoring.
effort: medium
model: haiku
---

# CPI — DEEP — BTP

[Seed set — kiem chung qua SAP Help Portal, SAP Community CPI tag.]

## 1. iFlow Architecture Pattern

### Point-to-Point
```
Sender -> CPI iFlow -> Receiver
```
- Don gian, it phuc tap
- Khong mo rong duoc

### CPI Hub (khoa)
```
He thong A -> CPI -> He thong B
He thong A -> CPI -> He thong C
```
- Tai su dung iFlow
- Centralized monitoring

### Event Mesh
```
S/4HANA -> Event Mesh -> CPI -> Receiver
```
- Event-driven
- Giam coupling

### Edge Integration Cell
- CPI chay on-prem (data center rieng) — dung cho use case yeu cau data residency.

## 2. Adapter Config

| Adapter | Protocol | Use case |
|---|---|---|
| **HTTP** | REST/JSON | Ket noi REST API hien dai |
| **SOAP** | SOAP/XML | Ket noi SAP/PI cu |
| **OData** | OData V2/V4 | S/4HANA Cloud APIs |
| **IDoc** | IDoc XML | S/4HANA / ECC IDoc |
| **RFC** | RFC/BAPI | ECC BAPI (can Cloud Connector) |
| **SFTP** | SFTP | File transfer |
| **Mail** | IMAP/SMTP | Email trigger |
| **AMQP** | AMQP 1.0 | Event Mesh / RabbitMQ |
| **JMS** | JMS | IBM MQ / Solace |
| **JDBC** | SQL | Database direct |
| **Ariba** | Ariba API | Ariba Network |
| **SuccessFactors** | SF API | Employee Central |

### Adapter Config Template

```xml
<!-- HTTP Sender Adapter -->
<adapter:sender type="HTTP">
  <http:address path="/api/order" method="POST"/>
  <http:authentication type="Basic"/>
</adapter:sender>
```

## 3. Mapping

| Loai | Dung khi | Vi du |
|---|---|---|
| **Message Mapping** | 1-1 field mapping, fixed structure | XPath expression, constant |
| **XSLT Mapping** | Need XML transform | XSLT 2.0, template |
| **Groovy Script** | Need dynamic logic | Parse JSON, call API, transform |
| **Java** | Need complex logic | Legacy, CPI 1.0 |

## 4. API Management

- **API Provider**: Backend API can expose
- **API Proxy**: API Gateway (rate limiting, quota, authentication)
- **API Product**: Goi API cho consumer
- **Application**: Consumer app dang ky

## 5. CPI Security

- **BasicAuth**: Username/password
- **OAuth2**: Client Credentials, Password grant
- **Client Certificate**: mTLS
- **PGP Encryption**: File encryption
- **CSI (Cloud System Integration)**: Certificate store

## 6. Monitoring & Alerting

- **CPI Monitor**: Web UI (`/itspaces`)
- **Message Processing Log (MPL)**: Track tung message
- **SAP Cloud ALM**: Integration with Cloud ALM
- **Audit Log**: Audit trail cho integration

## 7. Limits & Quota

- **Message processing**: message size max 100MB, timeout 30s, 20000 messages/day (tuy subscription).

## 8. Nguon tham khao

- SAP Help Portal — CPI: `https://help.sap.com/docs/cloud-integration`
- SAP Community CPI: `https://community.sap.com/t5/cloud-integration/`
- SAP Integration Suite: `https://www.sap.com/products/technology-platform/integration-suite.html`
