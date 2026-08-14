# SAP User-Created Skills

Thư mục này chứa các skill documents được **tự động tạo** bởi `sap-daily-learner` agent
khi giải quyết các vấn đề SAP phức tạp (lấy cảm hứng từ Hermes Agent của Nous Research).

Mỗi skill document là 1 file `.md` với format:

```markdown
---
name: <module>-<topic>
description: <mô tả>
created: <YYYY-MM-DD>
source: <câu hỏi gốc>
tags: [tag1, tag2]
---

# Tiêu đề

## Problem
Vấn đề

## Solution
Các bước giải quyết

## SSCUI / Fiori App
- ...

## API
- ...

## Notes
...
```

Các skill này có thể được dispatch lại khi user có câu hỏi tương tự.
