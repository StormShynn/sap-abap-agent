# SAP Context Tool-Result Trim - Compact output MCP truoc khi vao context

**Dung o dau**: ky thuat noi bo, khong tu trigger qua tu khoa nua (da chuyen tu `skills/` sang day)
— duoc ap dung boi: `skills/sap-cds-kb` (Pattern A/B), `skills/sap-analyze-function-spec` (FS lon),
`skills/sap-scaffold-rap`/`skills/sap-scaffold-cds` (Pattern C), `skills/sap-atc-review` (Pattern D),
va nhac toi trong Tier 2.2 cua noi dung `sap-routing-discipline` (bom qua SessionStart hook). Khi
1 trong cac skill do can ap dung ky thuat trim, chung se tro (`Read`) truc tiep den file nay.

## Khi nao dung

- ✅ Output MCP tool > ~2K token (~8KB text) VA con phai xu ly them nhieu buoc tiep theo.
  Vi du: `get_cds_view` tra source code day du cua 1 view 200+ field; `search_cds` tra 20 candidate;
  ADT pull 20 source file cung luc.
- ✅ Tong context dang phinh (>50% window) va can giai phong token truoc khi tiep tuc.
- ❌ Output nho (<2K) - tra nguyen, khong can trim (mat thong tin > tiet kiem).
- ❌ Dang debug bug runtime - GIU NGUYEN stack trace, error message, log (masking se giet kha nang debug).

## Quy tac kim cua context-engineering (nguon: context-optimization skill)

> Observation masking chi thay the verbose output bang **compact reference** - noi dung goc van
> retrievable duoc khi can. KHONG phai xoa thong tin, la thay bang con tro.

Ap dung 3 ky thuat theo thu tu uu tien:

### 1. KV-cache stable prefix (uu tien 1 - re, khong mat thong tin)

- Trong prompt/system, KHONG inject timestamp, version, session-id vao cho prefix.
- Trong skill nay: KHONG them "Trim applied at <timestamp>" vao compact output.
- Loi ich: prefix caching hit rate cao -> latency giam, cost giam.

### 2. Observation masking (uu tien 2 - thuong mang lai giam lon nhat)

Ap dung co dieu kien, KHONG ap dung may:

| Output | Mask hay khong | Cach mask |
|---|---|---|
| `kb_info()`, `search_cds` tra <5 items | KHONG mask | tra nguyen |
| `get_cds_view` chi `sections: ["fields"]` | KHONG mask | tra nguyen (da loc san) |
| `get_cds_view` sections=all, view co <30 field | KHONG mask | tra nguyen |
| `get_cds_view` sections=all, view 30+ field | **MASK** | trim theo pattern A |
| `search_cds` tra 10+ items | **MASK** | trim theo pattern B |
| Batch 10+ source file (ADT pull) | **MASK** | trim theo pattern C |
| ADT ATC log > 100 dong | **MASK** | trim theo pattern D |
| Error/stack trace trong debug loop | **KHONG MASK** | giu nguyen (rule gotcha #4 cua context-optimization) |

### 3. Compaction (uu tien 3 - chi khi context > 70% window)

Trigger compaction neu: (a) da masking het cac output verbose, (b) context van > 70%.
CHI compact tool output + old conversation. KHONG compact system prompt (anchor).
Trigger som o 70-80%, KHONG choi den 90%+ (chat luong compaction giam manh).

## Pattern trim cu the cho SAP MCPs

**Noi luu cache (`<agent-home>`)**: KHONG ghi vao project/workspace dang mo (plugin co the cai
va dung tren bat ky project nao) - `<agent-home>` la 1 thu muc co dinh theo may, mac dinh
`%USERPROFILE%\.sap-abap-agent\` (Windows) / `~/.sap-abap-agent/` (macOS/Linux), override qua
`SAP_ABAP_AGENT_HOME`. Lay duong dan da resolve (tu tao thu muc neu chua co) bang:
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" cache/cds_kb
```

### Pattern A - `get_cds_view` output (view 30+ field, sections=all)

Giu lai:
- Ten view, package, @AbapCatalog.sqlViewName, label
- Tat ca field co annotation `@Semantics.*` (business-relevant: amount, currency, date, qty)
- Tat ca association (`_Travel`, `_Customer`...) - vi day la entry point cho SELECT
- Tat ca annotation `@Consumption.filter` / `@ObjectModel.readOnly` (filter semantic)
- Where-used quan trong: `where-used on ZR_xxx` neu co trong output

LOAI BO (co the bo, khong phai lan luon lay):
- `key element` annotation boilerplate (duplication cua field key)
- Internal metadata nhu `TechnicalObject.lastChange...`, `AdministrativeData.*`
- `@ObjectModel.association.type` chi tiet (chi can biet co association, ten)
- Source code comment khong lien quan den field semantic (vd `/* generated */`, `/* package local */`)

Format output compact:
```
[get_cds_view: I_SalesDocument - masked. View co 87 field, 12 association.
Giu: 24 field co @Semantics + 12 association + metadata. Bo: 63 field technical.
Full: <agent-home>/cache/cds_kb/I_SalesDocument_<hash>.txt]
```

Sau do neu can field cu the -> `grep @Semantics.amountCurrency <file-path>` de doc lai.

### Pattern B - `search_cds` tra nhieu items (10+)

Mac dinh tool da tra 10-50 items, moi item co name + label + score. Trim theo:
- Giu ten view, label, relevance score (top 5)
- Giu 5 candidate tiep theo chi voi ten + package (de biet co option)
- Loai bo description dai dong neu trung lap voi label

```
[search_cds: "overdue invoices" - masked. Top 5: I_ARClearing... (0.92),
I_OpenCustomerInvoice... (0.88), ... 5 candidate tiep theo co trong file.
Full: <agent-home>/cache/cds_kb/search_overdue_<hash>.json]
```

### Pattern C - Batch ADT source pull (10+ class/include)

- Chi load source KHI CAN sua/scaffold, KHONG load full ca batch.
- Dung `sap_search` de lay ten + package, sau do `sap_get_object` cho tung file khi toi luot xu ly.
- Neu user noi "show all source files" -> tom tat: ten + line count + 1 dong summary cho moi file.

### Pattern D - ATC log (100+ dong)

- Giu: header (severity, check name, object), summary (X error / Y warning), 5 dong dau tien cua moi error.
- Loai bo: stack trace trung lap, frame internal cua SAP standard, message body verbose (thay bang 1 dong "see full in <path>").
- Ghi full log vao `<agent-home>/cache/atc/<ticket>.log`.

## Quy trinh trim

### Buoc 1: Detect

Nhan dien output MCP tool:
- Do dai text > ~2000 token (Quick check: text > 8K char = ~2K token)
- Co keyword indicator: "ABAP source:", "@AbapCatalog", "field(", "association [", stack trace `at SAPM...`

### Buoc 2: Choose pattern

Theo bang o muc "Observation masking" o tren.

### Buoc 3: Mask + write cache

Ghi full output vao cache, tra compact summary trong context.

```
Cache dir: <agent-home>/cache/<mcp-name>/<object>_<hash>.{txt,json,log}
```

Hash = SHA1 cua 8 char dau noi dung (de detect duplicate). KHONG dung timestamp trong ten file
(phuc vu KV-cache stable prefix).

### Buoc 4: Reference de retrieval

Trong output compact, luon ghi path day du den cache file de agent co the doc lai:
```
Full output: <absolute-path-to-cache-file>
```

### Buoc 5: Re-fetch chi khi can

Khi can chi tiet (agent dang o buoc tiep theo, KHONG phai ngay lap tuc), doc cache file voi
line range. KHONG refetch tu MCP (mat them 1 round-trip + token).

## Vi du

### Input (verbose)
```
User: "Lay source day du cua I_SalesDocument"
Agent: get_cds_view({ name: "I_SalesDocument", sections: ["metadata","fields","associations","source"] })
[MCP tra ve 4500 token]
```

### Output (compact)
```
[get_cds_view: I_SalesDocument - masked. 87 field, 12 association.
Semantic fields (24): SalesOrder, SalesOrderType, SalesOrganization,
DistributionChannel, OrganizationDivision, SoldToParty, NetAmount,
TransactionCurrency, CustomerPriceGroup, IncotermsClassification,
... (con 14 fields, xem cache)
Associations (12): _Item, _ScheduleLine, _Partner, _Address, _PricingElement,
... (con 8, xem cache)
Top associations cho query: _Item (composition), _Partner (to-many).
Full metadata + source: C:\Users\<user>\.sap-abap-agent\cache\cds_kb\I_SalesDocument_a3f8b21c.txt]
```

## Quy tac quan trong

1. **KHONG mask error output trong debug loop** - masking error se giet kha nang debug (gotcha #4
   cua context-optimization). Neu trong 3 turn gan nhat co error, GIU NGUYEN output.
2. **Cache file phai co path absolute** - agent doc lai de tra cuu (khong tu tao tuong tu).
3. **Hash phai on dinh** - cung content -> cung hash -> cung path (giup KV-cache + audit).
4. **Compact summary phai chua enough signal de tiep tuc** - khong mask den noi khong biet
   buoc tiep theo can gi.
5. **KHONG compact system prompt** - chi compact tool output + old conversation.

## Tich hop

- Skill `sap-cds-kb` - ap dung Pattern A, B cho output `get_cds_view`, `search_cds`.
- Skill `sap-analyze-function-spec` - ap dung cho output `office_to_md.py` neu file FS > 30 trang
  (ghi full text vao `<agent-home>/cache/fs/<ticket>.md`, tra summary theo 8 section INTAKE).
- Skill `sap-scaffold-rap`/`sap-scaffold-cds` - ap dung Pattern C khi pull batch source.
- Skill `sap-atc-review` - ap dung Pattern D cho ATC log.
- Skill `sap-systematic-debugging` - ap dung nguoc lai: GIU NGUYEN stack trace, error message,
  log trong debug loop (uu tien 1, ca tren masking).

## Luu y

- ⚠️ Neu trong 3 turn gan nhat co error/debug dang active -> TAT masking, tra nguyen output.
- 💡 Cache dir tu cleanup theo retention (mac dinh giu 7 ngay, toi da 500MB - co the doi qua
  `<agent-home>/cache/.retention`, JSON `{"days": N, "max_mb": N}`) bang
  `python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/cleanup_agent_home.py"` (them `--dry-run` de
  xem truoc se xoa gi). Script nay cung don luon `sync_skills.log` cu hon N ngay.
- 🔗 Khi masking, ghi vao `LEARNING_PROGRESS.md` (skill `sap-daily-learner`) de sau nay biet
  pattern nao ap dung duoc, pattern nao mat mat thong tin.
