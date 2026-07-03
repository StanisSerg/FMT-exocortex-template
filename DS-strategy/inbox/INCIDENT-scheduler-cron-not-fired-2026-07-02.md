---
type: incident
incident_id: INC-2026-07-02-scheduler-cron-not-fired
severity: critical
opened: 2026-07-02
detected_by: day-open-scaffold.sh (auto Mode A)
mode: A (cron не запущен)
status: open
owner: pilot
related_wp: WP-7, WP-178, WP-356
auto_generated: true
---

# Инцидент: scheduler/feedback-watchdog не запущен (2026-07-02)

## Симптом (auto-detected)

- launchctl: юнит `iwe.scheduler` или `iwe.feedback-watchdog` отсутствует
- Последний лог `~/logs/synchronizer/feedback-watchdog-*.log` старше 24ч (или отсутствует)
- Mode A классификация (см. peer-сессия 2026-05-30-07 §Gap 3)

## Action items

1. Проверить `~/Library/LaunchAgents/` на наличие plist
2. `bash /home/asus/IWE/FMT-exocortex-template/DS-strategy/scripts/install-launchd.sh` для регистрации
3. Запустить руками: `bash ${IWE_SCHEDULER_PATH:-/home/asus/IWE/FMT-exocortex-template/scripts/scheduler.sh} --dry-run`

## Auto-generation note

Этот файл создан автоматически day-open-scaffold.sh при каждом обнаружении Mode A.
Если решено отложить fix — поставить `status: deferred` и убрать `auto_generated` поле, чтобы скаффолд не перезаписывал контекст.
