---
name: sap-abap-sql
description: Huong dan ABAP SQL and AMDP (ABAP Managed Database Procedures) hien dai cho ABAP Cloud — CDS-based access, window functions, CTE, SQLScript, performance patterns.
when_to_use: |
  "viet SQL trong ABAP Cloud", "dung window function", "ABAP SQL vs AMDP",
  "truy van performance ABAP", "SQLScript", "tan dung HANA features".
argument-hint: "[cau hoi ve ABAP SQL / AMDP / performance]"
effort: medium
model: sonnet
---

# ABAP SQL & AMDP — Modern ABAP Development

## 1. ABAP SQL trong ABAP Cloud

Tren ABAP Cloud, chi duoc dung **released CDS views** de doc du lieu. KHONG SELECT truc tiep
bang standard SAP (EKKO, MSEG, BKPF...). Luon dung:

```abap
SELECT * FROM i_purchaseorder         " view released thay vi EKKO
  WHERE purchasingorganization = @lv_org
  INTO TABLE @lt_data.
```

**Cac tu khoa ABAP SQL quan trong:**

| Tu khoa | Mo ta | Vi du |
|---------|-------|-------|
| `INTO TABLE @lt_data` | Select nhieu dong, internal table | `INTO TABLE @lt_orders` |
| `INTO @ls_data` | Select 1 dong | `SELECT SINGLE ... INTO @ls_header` |
| `FOR ALL ENTRIES` | Join voi internal table (tranh bi dong du lieu) | `FOR ALL ENTRIES IN @lt_keys WHERE ...` |
| `INNER JOIN` / `LEFT OUTER JOIN` | Join view | `JOIN i_businesspartner ON ...` |
| `GROUP BY` / `HAVING` | Aggregation | `GROUP BY purchasinggroup HAVING count(*) > 10` |
| `ORDER BY` | Sap xep | `ORDER BY purchasingdocument DESC` |
| `UP TO 1 ROWS` | Gioi han so dong | `UP TO 1 ROWS ORDER BY creationdate DESC` |
| `UNION` | Hop ket qua | `UNION ... SELECT ...` |

## 2. Window Functions (ABAP SQL 7.55+)

ABAP SQL ho tro window functions tu ABAP 7.55 / S/4HANA 2021:

```abap
SELECT
  matnr,
  werks,
  labst,
  ROW_NUMBER() OVER ( PARTITION BY matnr ORDER BY labst DESC ) AS rank
FROM i_stock
INTO TABLE @lt_data.
```

| Function | Mo ta | Vi du |
|----------|-------|-------|
| `ROW_NUMBER( )` | Danh so thu tu | `ROW_NUMBER() OVER (PARTITION BY matnr ORDER BY labst DESC)` |
| `RANK( )` | Rank (co the bang nhau) | `RANK() OVER (ORDER BY netwr DESC)` |
| `DENSE_RANK( )` | Rank lien tuc | `DENSE_RANK() OVER (ORDER BY netwr DESC)` |
| `SUM( ) OVER ( ... )` | Running total | `SUM(amt) OVER (PARTITION BY bukrs ORDER BY gjahr)` |
| `LAG( )` / `LEAD( )` | Truy cap dong truoc/sau | `LAG(labst) OVER (PARTITION BY matnr ORDER BY budat)` |
| `COUNT( ) OVER ( ... )` | Dem tren partition | `COUNT(*) OVER (PARTITION BY bukrs)` |
| `AVG( ) OVER ( ... )` | Trung binh tren partition | `AVG(netpr) OVER (PARTITION BY matnr)` |

**Gioi han tren ABAP Cloud**: Window functions chi chay duoc trong **AMDP** hoac **CDS views**
(dung SQLScript/Windowing function).

## 3. CTE (Common Table Expressions)

```abap
WITH
  +active_orders AS (
    SELECT purchaseorder, supplier, netamount
    FROM i_purchaseorder
    WHERE overallstatus = 'IN_PROCESS'
  ),
  +high_value AS (
    SELECT * FROM +active_orders
    WHERE netamount > 10000
  )
SELECT * FROM +high_value
  INTO TABLE @lt_result.
```

CTE giai quyet van de nested SELECT doc hon.

## 4. AMDP (ABAP Managed Database Procedures)

AMDP = ABAP code chay truc tiep tren HANA (SQLScript), cho performance cao nhat:

```abap
CLASS zcl_amdp_demo DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.          " <-- bat buoc
    METHODS get_high_value_orders
      IMPORTING VALUE(iv_min_amount) TYPE i
      EXPORTING VALUE(et_result) TYPE STANDARD TABLE OF i_purchaseorder.
ENDCLASS.

CLASS zcl_amdp_demo IMPLEMENTATION.
  METHOD get_high_value_orders BY DATABASE PROCEDURE FOR HDB
    LANGUAGE SQLSCRIPT
    OPTIONS READ-ONLY.
    et_result = SELECT * FROM i_purchaseorder
      WHERE netamount > iv_min_amount
      ORDER BY netamount DESC;
  ENDMETHOD.
ENDCLASS.
```

**Luu y quan trong**:
- `if_amdp_marker_hdb` interface bat buoc cho HANA AMDP
- `BY DATABASE PROCEDURE FOR HDB LANGUAGE SQLSCRIPT`
- Chi doc du lieu (READ-ONLY) hoac doc-ghi (tu 7.40 SP10)
- AMDP chi chay duoc trong **on-stack** hoac **BTP ABAP Environment**

## 5. Khi nao dung ABAP SQL vs AMDP vs CDS?

| Tinh huong | Cong cu | Ly do |
|------------|---------|-------|
| Business logic don gian, 1-2 table | ABAP SQL | Don gian, de test |
| Can doc tu nhieu view join | CDS view + ABAP SQL | View da toi uu san |
| Can window function, CTE phuc tap | CDS view (SQLScript) hoac AMDP | HANA-native, nhanh |
| Can doc-ghi DB (write) | AMDP | ABAP SQL INSERT/UPDATE/MODIFY |
| Performance quan trong (>1M rows) | AMDP / CDS view | Tan dung HANA column store |
| Can lay data cho RAP BO | CDS view (definition) | RAP bat buoc doc tu CDS view |

## 6. Performance Patterns

| Pattern | Mo ta |
|---------|-------|
| **Index-based read** | `SELECT SINGLE ... WHERE primary_key` => nhanh nhat |
| **FOR ALL ENTRIES** | Net va trong 1-10K keys, tranh dung empty |
| **SELECT ... INTO CORRESPONDING FIELDS** | Tranh SELECT * khong can thiet |
| **Trung gian view** | Tao CDS view cho logic phuc tap thay vi nested SELECT |
| **Batch processing** | SELECT ... INTO TABLE ... kokhoi dong batch thay vi loop |
| **AMDP bulk read** | AMDP cho mass data >100K rows |

## 7. ABAP SQL bi cam tren ABAP Cloud

| Cu phap bi cam | Ly do | Thay bang |
|----------------|-------|-----------|
| `SELECT * FROM bkpf` | Bang standard, chua released | `SELECT FROM i_journalentry` |
| `NATIVE SQL` | Bypass ABAP layer | AMDP (SQLScript, van trong ABAP) |
| `SELECT ... CLIENT SPECIFIED` | Security bypass | `cl_abap_context_info=>get_client( )` |
| `EXEC SQL` | Legacy | AMDP hoac CDS view |

## Nguon tham khao

- SAP Help: ABAP SQL, AMDP (7.55+)
- SAP Community: ABAP SQL + Window Functions
- `xco_cp` SQL utilities trên BTP Steampunk
