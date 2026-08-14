---
description: Dong bo skills/agents moi nhat tu GitHub ve local
argument-hint: ""
---

# /sync-skills — Dong bo Skills & Agents

Dong bo skills, agents, commands, reference modules moi nhat tu GitHub ve may local.  
Dung khi ban muon cap nhat ma khong can `git pull` thu cong.

## Cach dung

Trong Claude Code, go:

```text
/sync-skills
```

## Luu y

- 📡 Can co internet de ket noi GitHub
- 🔄 Chi lay **skills/ agents/ commands/ reference/** moi — khong anh huong config SAP cua ban
- 📊 Xem lich su dong bo tai `sync_skills.log` ben trong thu muc `.sap-abap-agent/` cua CHINH
  ban clone plugin nay (khong phai `%USERPROFILE%` - script tu resolve theo vi tri file cua no,
  xem `reference/scripts/sync_skills.py`)

## Trong Claude Code (khi go `/sync-skills`)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/sync_skills.py"
```

`${CLAUDE_PLUGIN_ROOT}` de Claude Code tu resolve dung thu muc cai plugin, bat ke dang mo
project nao (KHONG dung duong dan tuong doi `reference/scripts/...` vi cwd luc nay la project
cua ban, khong phai thu muc plugin).

## Tu dong dong bo (background, chay NGOAI Claude Code)

Muon tu dong cap nhat skills ma khong can go `/sync-skills` bang tay? Dung Python daemon qua
Task Scheduler/cron - luc nay chay ngoai Claude Code nen **KHONG co** `${CLAUDE_PLUGIN_ROOT}`,
phai `cd` vao dung thu muc ban da clone plugin nay truoc (hoac dung `--dir <path>`):

```bash
# Chay 1 lan (dung trong thu muc da clone plugin, hoac them --dir <path-toi-plugin>)
python reference/scripts/sync_skills.py

# Chay background (macOS/Linux: nohup, Windows: Task Scheduler)
python reference/scripts/sync_skills.py --daemon --interval 600

# Xem them tham so
python reference/scripts/sync_skills.py --help
```

Cai dat Task Scheduler tren Windows bang:

```bat
:: Chay voi quyen Administrator, trong thu muc da clone plugin
reference\scripts\install-task-scheduler.bat
```
