---
name: parse-inbox-notes
description: |
  Разбор pending-заметок из governance-репо (`inbox/fleeting-notes.md` и `inbox/captures.md`).
  Классифицирует заметки, формирует `extraction-reports/YYYY-MM-DD-inbox-check.md`
  со статусом `pending-review`, помечает исходные заметки `[analyzed]` и коммитит результат.
  Используется как ручная замена или дополнение к launchd-запуску `extractor.sh inbox-check`.
version: 0.1.0
status: experimental
layer: L2
agents: single
interaction: multi-step
gates_required: []
gates_enforced: []
gates_rationale: "Ad-hoc project-level skill для ручного разбора inbox. Базируется на существующем DP.AISYS.013 (Inbox-Check) и ролях R2/R15; IntegrationGate пропущен по явной команде пилота."
triggers:
  slash:
    - /parse-inbox-notes
  phrases:
    - разбери заметки
    - разбор заметок
    - parse inbox notes
    - обработай inbox
---

# /parse-inbox-notes

> **Scope:** ручной или по-требованию разбор inbox-заметок в governance-репо.
> **Not in scope:** автоматический cron/launchd (это `extractor.sh inbox-check`); финальное accept/reject/defer кандидатов (это `/apply-captures`).
> **Role:** R2 Экстрактор в ручном режиме.

## When to use

- Пилот написал заметки боту, они появились в `inbox/fleeting-notes.md`, и хочет их разобрать без ожидания launchd.
- `extractor.sh inbox-check` не сработал (например, scheduler cron not fired).
- Нужно быстро превратить несколько свежих заметок в `extraction-reports` для последующего `/apply-captures`.

## Preconditions

1. **WP Gate precondition.** Разбор привязан к согласованному РП (по умолчанию WP-1 Саморазвитие / инфраструктурные навыки).
2. **Git pull.** Перед разбором governance-репо должно быть синхронизировано с GitHub (extension `day-open.before.git-pull.md` или ручной `git pull --rebase`).
3. **Inbox-файлы.** Должен существовать хотя бы один из: `inbox/fleeting-notes.md`, `inbox/captures.md`.

## Algorithm

### Step 1 — Синхронизация и сканирование

Input: governance-репо `${IWE_GOVERNANCE_REPO:-DS-strategy}`.
Action:
- Убедиться, что локальная копия governance-репо актуальна (`git pull --rebase origin main`).
- Запустить `bash "${IWE_TEMPLATE:-FMT-exocortex-template}/.claude/skills/parse-inbox-notes/scripts/parse-inbox-notes.sh" scan` для детерминированного поиска pending-заметок.
- Если pending-заметок нет — сообщить пилоту и завершить.

Output: список pending-заметок с заголовком, источником (`fleeting-notes.md` / `captures.md`) и сырым текстом.

### Step 2 — Классификация

Input: список pending-заметок.
Action: для каждой заметки определить тип:

| Тип | Признак |
|-----|---------|
| `entity` | Компонент, архитектура, понятие |
| `distinction` | Пара «A ≠ B» |
| `method` | Способ действия, алгоритм, процесс |
| `wp` | Тип артефакта / рабочий продукт |
| `fm` | Типовая ошибка, failure mode |
| `rule` | Ограничение, правило 1–3 строки |
| `task` | Конкретное действие, TODO |
| `reference` | Ссылка, источник, цитата |
| `noise` | Шум, приветствие, неструктурированный поток мыслей |

Output: классифицированные заметки.

### Step 3 — Маршрутизация

Input: классифицированные заметки.
Action:
- Прочитать `roles/extractor/config/routing.md` для определения целевого Pack и директории.
- Для каждой доменной заметки (`entity`, `distinction`, `method`, `wp`, `fm`, `rule`) определить `target_repo` и `target_path`.
- Для задач (`task`) предложить создать WP или записать в `captures.md`.
- Для `reference` — предложить сохранить в `captures.md` или соответствующий SoTA/справочник.
- `noise` — отметить как rejected с причиной «шум».

Output: заметки с маршрутом.

### Step 4 — Проверка на дубли и feedback-log

Input: заметки с маршрутом.
Action:
- Прочитать `inbox/feedback-log.md` (если есть).
- Проверить каждого кандидата на пересечение с существующими сущностями целевого Pack (grep по ключевым словам).
- Если найден дубликат — вердикт `reject`, указать существующий ID.
- Если найдено противоречие — вердикт `defer` до разрешения.

Output: заметки с предварительным вердиктом.

### Step 5 — Генерация Extraction Report

Input: заметки с вердиктами.
Action:
- Создать файл `inbox/extraction-reports/YYYY-MM-DD-inbox-check.md`.
- Frontmatter: `type: extraction-report`, `source: inbox-check`, `date: YYYY-MM-DD`, `status: pending-review`, `processed: N`, `remaining: 0`.
- Для каждого кандидата (кроме `noise`/`reject`) добавить блок с:
  - источником,
  - сырым текстом,
  - классификацией,
  - `target_repo`, `target_path`, `action`,
  - совместимостью,
  - готовым текстом (для accept),
  - вердиктом `accept`/`reject`/`defer` и обоснованием.

Output: файл `extraction-reports/YYYY-MM-DD-inbox-check.md`.

### Step 6 — Пометка исходных заметок

Input: созданный отчёт.
Action:
- В `inbox/fleeting-notes.md` и `inbox/captures.md` для каждой обработанной заметки добавить к заголовку `### ... [analyzed YYYY-MM-DD]`.
- **Не ставить `[processed]`** — это делается только после `/apply-captures`.

Output: помеченные inbox-файлы.

### Step 7 — Коммит и push

Input: изменённые `inbox/extraction-reports/*.md`, `inbox/fleeting-notes.md`, `inbox/captures.md`.
Action:
- `git add` только изменённые inbox-файлы.
- `git commit -m "inbox-check: N captures → extraction report YYYY-MM-DD"`.
- `git push origin main`.

Output: изменения запушены в governance-репо.

## Bundled resources

- `scripts/parse-inbox-notes.sh` — детерминированный helper для поиска pending-заметок и git-pull.

## Anti-patterns

- Не записывать кандидатов напрямую в Pack — только в `extraction-reports`.
- Не ставить `[processed]` вместо `[analyzed]`.
- Не пропускать живое решение R15 — этот скилл только готовит отчёт.
- Не обрабатывать более 5 заметок за раз; если больше — взять 5 самых старых.

## Verification

1. Записать тестовую заметку в `inbox/fleeting-notes.md`.
2. Вызвать `/parse-inbox-notes`.
3. Убедиться, что создан `inbox/extraction-reports/YYYY-MM-DD-inbox-check.md`.
4. Убедиться, что заметка помечена `[analyzed YYYY-MM-DD]`.
5. Запустить `bash .claude/skills/skill-creator/scripts/verify-skill.sh parse-inbox-notes` — ожидается PASS.
