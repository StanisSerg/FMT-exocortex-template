# Оперативная память

> **Инструкции:** `{{WORKSPACE_DIR}}/CLAUDE.md` | **Настройте под свою экосистему**

## БЛОКИРУЮЩИЕ (проверяй ВСЕГДА)

1. **WP Gate:** Задание → проверь РП в таблице ниже → нет = СТОП (CLAUDE.md § 2)
2. **Close:** push ≠ закрытие → capture-to-pack + подтверждение + backup (CLAUDE.md § 2)
3. **ArchGate ≥8:** Предлагать ТОЛЬКО решения с оценкой ≥8 по ArchGate (ЭМОГСС). Слабые решения (≤7) — НЕ предлагать.

## ВАЖНЫЕ (проверяй на рубежах)

3. **Capture:** На рубеже → «Capture: X → Y» (CLAUDE.md § 2)
4. **Отчёты:** ВСЕ репо в {{WORKSPACE_DIR}}/
5. **Процессы:** Нельзя реализовывать без PROCESSES.md (CLAUDE.md § 3)

---

## РП текущей недели (W19: 5–11 мая)

> Порядок: in_progress → pending → done.
> WeekPlan: `DS-strategy/current/WeekPlan-W19-2026-05-05.md`

| # | РП | Бюджет | Статус | Дедлайн |
|---|-----|--------|--------|---------|
| 93 | Создание Decision Layer — тестирование + интеграция | 4h | in_progress | — |
| 83 | Methods PACK — создание шаблонов методов | 3h | pending | — |
| 75 | SoTA Ingestion — сессия 2 (10 статей) | 3h | in_progress | — |
| 94 | Изучение FPF — разбор принципов | 2h | pending | — |
| 1 | Саморазвитие — 1 principle → capture | 1h | pending | — |
| 96 | Создание модуля «НДК» — доработка | 1h | in_progress | — |

---

## Навигация (Слой 3)

| Тема | Файл |
|------|------|
| Различения (жёсткие пары) | `memory/hard-distinctions.md` |
| FPF (навигация, принципы) | `memory/fpf-reference.md` |
| Правила по типам репо | `memory/repo-type-rules.md` |
| Чеклисты | `memory/checklists.md` |
| **SOTA-практики** | `memory/sota-reference.md` |
| Обслуживание CLAUDE.md | `memory/claude-md-maintenance.md` |
| Урок WP Gate | `memory/wp-gate-lesson.md` |
| **Системно-специфичное** | **→ repo/CLAUDE.md** |
| Стратег | `DS-strategist/README.md` |
