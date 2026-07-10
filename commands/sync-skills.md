---
description: Dong bo skills/agents moi nhat tu GitHub ve local
argument-hint: ""
---

# /sync-skills — Dong bo Skills & Agents

Dong bo skills, agents, commands, reference modules moi nhat tu GitHub ve may local.  
Dung khi ban muon cap nhat ma khong can `git pull` thu cong.

## Cach dung

Trong Claude Code, go:

```
/sync-skills
```

## Luu y

- 📡 Can co internet de ket noi GitHub
- 🔄 Chi lay **skills/ agents/ commands/ reference/** moi — khong anh huong config SAP cua ban
- 📊 Xem lich su dong bo tai `.sap-abap-agent/sync_skills.log`

## Tu dong dong bo (background)

Muon tu dong cap nhat skills ma khong can go `/sync-skills` bang tay?
Dung Python daemon:

```bash
# Chay 1 lan
python reference/scripts/sync_skills.py

# Chay background (macOS/Linux: nohup, Windows: Task Scheduler)
python reference/scripts/sync_skills.py --daemon --interval 600

# Xem them tham so
python reference/scripts/sync_skills.py --help
```

Cai dat Task Scheduler tren Windows bang:
```
# Chay voi quyen Administrator
reference/scripts/install-task-scheduler.bat
```
