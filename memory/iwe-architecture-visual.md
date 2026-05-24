# 🧠 IWE Экзокортекс — Визуальная архитектура

**Версия:** FMT 0.34.1  
**Дата:** 2026-05-24  
**Формат:** Markdown + Mermaid (рендерится в Obsidian, GitHub, GitLab)

---

## Легенда слоёв

| Слой | Цвет | Назначение |
|------|------|------------|
| L0 Raw / External | 🔴 | Внешние источники: PDF, Web, календарь, GitHub |
| L1 Platform | 🟠 | Неизменяемый шаблон `FMT-exocortex-template`: скиллы, хуки, скрипты, правила |
| L2 Runtime | 🟡 | Генерируемый слой `.iwe-runtime/`: подставленные пути, runtime-роли, манифесты |
| L3 User Customizations | 🟢 | Пользовательские расширения: `extensions/`, `params.yaml`, память, паки |
| L4 Personal | 🔵 | Персональные настройки: USER-SPACE в `CLAUDE.md`, ритм дня, личное руководство |

---

## 1. Общая архитектура (L0–L4)

Эта диаграмма показывает, как пять слоёв экзокортекса стыкуются друг с другом.  
**Главный смысл:** потоки данных идут снизу вверх (L0 → L1 → L2 → L3), а управляющие сигналы — сверху вниз (L4 → L3 → L1). L1 никогда не правится руками — только через `update.sh`. Все персональные правки живут в L3–L4.

```mermaid
graph TB
    subgraph L0["🔴 L0 Raw / External"]
        PDF["📄 PDF источники<br/>NASEM, исследования"]
        WEB["🌐 Web / Новости"]
        CAL["📅 Календарь"]
        GIT["🔧 GitHub / Issues"]
    end

    subgraph L1["🟠 L1 Platform (FMT-template)"]
        SKILLS["🎭 Skills<br/>23 скилла"]
        HOOKS["⚓ Hooks<br/>12 штук"]
        SCRIPTS["📜 Scripts<br/>40+ скриптов"]
        RULES["📋 Rules<br/>4 файла"]
        ROLES["🎬 Roles<br/>5 ролей"]
    end

    subgraph L2["🟡 L2 Runtime (.iwe-runtime)"]
        RT_HOOKS["Runtime Hooks"]
        RT_ROLES["Runtime Roles<br/>substituted paths"]
        RT_MANIFEST["update-manifest.json"]
    end

    subgraph L3["🟢 L3 User Customizations"]
        EXT["📎 Extensions/<br/>4 файла"]
        PARAMS["⚙️ params.yaml"]
        MEMORY_FILES["📝 Memory артефакты<br/>WP-сессии, lessons"]
        PACKS["📦 Pack/<br/>cattle-science"]
    end

    subgraph L4["🔵 L4 Personal"]
        CLAUDE_USER["CLAUDE.md<br/>USER-SPACE"]
        DAY_RHYTHM["day-rhythm-config.yaml"]
        PERSONAL["personal-guide/"]
    end

    PDF -->|"SoTA Ingestion"| PACKS
    WEB -->|"Scout / News"| MEMORY_FILES
    CAL -->|"Day Open"| SKILLS
    GIT -->|"Issues"| SKILLS

    SKILLS -->|"вызывают"| SCRIPTS
    HOOKS -->|"PreToolUse gate"| RT_HOOKS
    ROLES -->|"install.sh"| RT_ROLES
    SCRIPTS -->|"update.sh"| RT_MANIFEST

    RT_HOOKS -->|"блокируют/разрешают"| EXT
    RT_ROLES -->|"cron / launchd"| DAY_RHYTHM

    EXT -->|"override"| SKILLS
    PARAMS -->|"конфигурируют"| SCRIPTS
    MEMORY_FILES -->|"read/write"| PACKS
    PACKS -->|"правила"| RULES

    CLAUDE_USER -->|"персональные инструкции"| SKILLS
    DAY_RHYTHM -->|"ритм дня"| SKILLS
    PERSONAL -->|"цели / НЭП"| MEMORY_FILES
```

**Ключевые связи:**
- `CAL → SKILLS` — календарь триггерит ритуал Day Open через скилл.
- `RT_HOOKS → EXT` — хуки runtime принимают решение «разрешить / заблокировать» на основе пользовательских расширений.
- `PACKS → RULES` — знания из Pack (например, `cattle-science`) становятся правилами для всей системы.

---

## 2. Ритуальный цикл дня

Эта диаграмма описывает замкнутый цикл суточной работы.  
**Главный смысл:** Day Open и Day Close — это не просто заметки, а **протоколы** с обязательными шагами. Пропуск шага = риск потери контекста. Quick Close используется после каждой рабочей сессии, Day Close — в конце дня.

```mermaid
graph LR
    A["🌅 Утро<br/>Day Open"] -->|"Carry-over"| B["⚡ День<br/>Work / Sessions"]
    B -->|"Quick Close"| C["🌙 Вечер<br/>Day Close"]
    C -->|"backup + git push"| D["📦 Archive<br/>exocortex/"]
    D -->|"next day"| A

    subgraph DayOpen["Day Open (skill)"]
        DO1["1. Extensions (before)"]
        DO2["2. Вчера: DayPlan + коммиты"]
        DO3["3. Issues + Inbox Triage"]
        DO4["4. План на сегодня<br/>(carry-over + WeekPlan)"]
        DO5["5. IWE за ночь<br/>(update.sh --check)"]
        DO6["6. Запись DayPlan<br/>+ session-log"]
    end

    subgraph DayClose["Day Close (skill)"]
        DC1["1. Сбор коммитов"]
        DC2["2. Governance batch<br/>WeekPlan + WeekReport + WP-REGISTRY"]
        DC3["3. Архивация DayPlan"]
        DC4["4. Memory Drift Scan"]
        DC5["5. Index Health Check"]
        DC6["6. Lesson Hygiene"]
        DC7["7. Мультипликатор<br/>(WakaTime)"]
        DC8["8. Итоги + 3 варианта завтра"]
        DC9["9. Коммит + push"]
    end

    A --> DayOpen
    C --> DayClose
```

**Что происходит на каждом этапе:**
- **Day Open** — система собирает контекст (что было вчера, какие issues, что запланировано в WeekPlan), проверяет обновления шаблона и фиксирует DayPlan.
- **Work / Sessions** — собственно работа по WP. После каждой сессии — Quick Close (коммиты, статус WP, уроки, next action).
- **Day Close** — governance-штамповка: обновление реестров, архивация, проверка здоровья индекса, time-tracking и план на завтра.
- **exocortex/** — offline-архив состояния памяти на конец дня. Не попадает в git.

---

## 3. Жизненный цикл Рабочего Продукта (WP)

Эта диаграмма показывает, как рождается, живёт и закрывается задача.  
**Главный смысл:** нельзя просто «взять и сделать». Любая работа проходит через **WP Gate** — проверку бюджета и наличия WeekPlan. Затем — **атомарная запись в 5 мест** (одна транзакция, нельзя пропустить место). Quick Close внутри сессии позволяет фиксировать прогресс без ожидания финала.

```mermaid
graph TD
    NEED["💡 Потребность<br/>Задача / Идея / НЭП"] -->|"wp-new"| GATE["🚦 WP Gate<br/>Проверка бюджета"]
    GATE -->|"PASS"| ATOM["⚛️ Атомарная запись<br/>в 5 мест"]
    GATE -->|"FAIL бюджет"| DEFER["⏸️ Defer<br/>off-plan / backlog"]

    subgraph FivePlaces["5 мест записи"]
        F1["1. MEMORY.md<br/>РП текущей недели"]
        F2["2. WP-REGISTRY.md<br/>Реестр всех WP"]
        F3["3. WeekPlan W{N}<br/>Таблица РП"]
        F4["4. Strategy.md<br/>РП → Результат месяца"]
        F5["5. inbox/WP-{N}-*.md<br/>Context file"]
    end

    ATOM --> FivePlaces
    FivePlaces --> WORK["🔨 Работа<br/>Сессии / Коммиты"]
    WORK -->|"Quick Close"| QC["📝 Quick Close<br/>per session"]
    QC --> WORK
    WORK -->|"Done"| CLOSE["✅ Close WP<br/>5 мест обновлены"]
    CLOSE --> ARCHIVE["📦 Archive<br/>wp-contexts/"]

    DEFER -->|"при появлении<br/>бюджета"| GATE
```

**WP Gate — блокеры:**
- Нет WeekPlan → СТОП.
- Бюджет недели перегружен → предупреждение.
- Open-ended WP (без чёткого результата) → запрещены.

**Quick Close фиксирует:**
- Коммиты за сессию.
- Статус WP (partial / done).
- Уроки (≤8 штук в MEMORY.md).
- Следующий шаг (next action).

---

## 4. SoTA Ingestion Pipeline

Эта диаграмма описывает путь от источника знаний до операционного метода.  
**Главный смысл:** существует два потока — **SoTA** (индивидуальные извлечения из источников) и **SYNTH** (синтез из ≥2 источников). Критическое архитектурное решение (ArchGate): **SYNTH = learning-only**. Правила пишутся только от индивидуальных SoTA (L1), не от SYNTH (L2). Это предотвращает «controlled semantic coarsening» — когда усреднение разных источников маскирует важные нюансы.

```mermaid
graph LR
    SRC["📄 Источник<br/>PDF / Статья / Книга"] -->|"Чтение + выделение"| SOTA["📋 SoTA файл<br/>CS.SOTA.XXX.md"]
    SOTA -->|"N ≥ 2 источников"| SYNTH["🧬 SYNTH<br/>Learning-only synthesis"]
    SOTA -->|"Правило"| RULE["⚖️ Rule<br/>Из L1 напрямую"]
    SYNTH -->|"Обучение"| METHOD["📖 METHOD<br/>Операционный алгоритм"]
    RULE -->|"Машинная проверка"| METHOD
    METHOD -->|"Применение"| PRACTICE["🏭 Практика<br/>Хозяйство / Работа"]

    subgraph SoTA_File["Структура SoTA"]
        SF1["Frontmatter:<br/>id, type, trust, status"]
        SF2["Key Claims<br/>с numeric confidence"]
        SF3["Loss Notes<br/>что потеряно"]
        SF4["Source Links<br/>страницы / уравнения"]
    end

    subgraph SYNTH_Rules["Правила SYNTH"]
        SR1["rules_source: false<br/>❌ Нельзя использовать<br/>как source правил"]
        SR2["KindBridge<br/>↔ Маппинг между источниками"]
        SR3["Weakest-link<br/>0.82 = min(trust)"]
        SR4["Freshness window<br/>2 года → auto-tag"]
    end

    SOTA --> SoTA_File
    SYNTH --> SYNTH_Rules
```

**Структура SoTA-файла:**
- **Frontmatter** — идентификатор, тип доверия (научный / экспертный / анекдот), статус.
- **Key Claims** — ключевые утверждения с числовым confidence (0.0–1.0).
- **Loss Notes** — честная запись о том, что потеряно при сокращении.
- **Source Links** — точные страницы, уравнения, таблицы для верификации.

**Правила SYNTH:**
- `rules_source: false` — SYNTH нельзя цитировать как основание правила.
- **Weakest-link** — итоговый confidence синтеза равен минимальному среди источников.
- **Freshness window** — источники старше 2 лет автоматически помечаются.

---

## 5. Роли (Agents) и их функции

Эта таблица описывает 8 ключевых ролей экзокортекса.  
**Главный смысл:** каждая роль — это не просто название, а контракт с чёткими полномочиями. Роли R1 и R2 — стратег и экстрактор — управляют потоками работы и знаний. R23 (Верификатор) и R24 (Аудитор) работают в режиме **context isolation**: они не видят историю сессии, а оценивают только готовый артефакт. Это защита от предвзятости.

| ID | Роль | FX | Исполнитель | Типичные задачи |
|----|------|-----|-------------|-----------------|
| R1 | **Стратег** | — | Скилл | Day Open/Close, Week Close, стратсессии, wp-new, run-protocol |
| R2 | **Экстрактор** | — | Скилл | KE в Pack, inbox check, ontology sync, apply-captures |
| R5 | **Архитектор** | FX5 | Скилл + inline | ArchGate (7 критериев ЭМОГССБ), ADR, FPF routing |
| R6 | **Кодировщик** | FX5, FX8 | Inline + скилл | Код, рефакторинг, iwe-update, audit-installation |
| R23 | **Верификатор** | — | Sub-agent | Проверка артефактов по эталону. Context isolation |
| R24 | **Аудитор** | — | Sub-agent + скилл | audit-installation: 6 компонентов, verdict ✅/⚠️/❌ |
| R8 | **Синхронизатор** | — | Скрипт + скилл | update.sh, template-sync, drift detection, backup |
| R9 | **Шаблонизатор** | FX8 | Скилл | iwe-update, extend, pack-new |

**Обозначения:**
- **FX** — функциональные требования (FX5 = архитектурные, FX8 = шаблонные).
- **Context isolation** — субагент получает только артефакт и эталон, без истории переписки.

---

## 6. Hooks — Gate-механика

Эта диаграмма показывает, как работает перехват инструментов (PreToolUse hook).  
**Главный смысл:** перед выполнением любого write-инструмента (WriteFile, Shell, Agent) система проверяет sentinel-файл. Если найден флаг dry-run — операция блокируется. Это позволяет делать audit и smoke-test без риска случайно изменить файлы.

```mermaid
graph TD
    TOOL["🔧 Tool Call<br/>WriteFile / Shell / Agent"] --> HOOK["⚓ PreToolUse Hook<br/>dry-run-gate.sh"]
    HOOK -->|"Sentinel exists?"| CHECK{"/tmp/iwe-dry-run-*.flag"}
    CHECK -->|"Да (dry-run)"| BLOCK["🚫 BLOCK<br/>Write запрещён"]
    CHECK -->|"Нет"| ALLOW["✅ ALLOW<br/>Tool выполняется"]

    subgraph HooksList["12 Hooks (.claude/hooks/)"]
        H1["agent-trace-recorder<br/>Запись трассировки"]
        H2["agent-trace-uploader<br/>Отправка трассировки"]
        H3["capture-bus<br/>Маршрутизация captures"]
        H4["close-gate-reminder<br/>Напоминание о Close"]
        H5["dry-run-gate<br/>Блокировка write в тесте"]
        H6["extensions-gate<br/>Проверка extensions"]
        H7["precompact-checkpoint<br/>Чекпоинт перед compaction"]
        H8["protocol-artifact-validate<br/>Валидация артефактов"]
        H9["protocol-completion-reminder<br/>Напоминание о завершении"]
        H10["protocol-stop-gate<br/>Остановка протокола"]
        H11["wakatime-heartbeat<br/>Heartbeat трекинга"]
        H12["wp-gate-reminder<br/>Напоминание WP Gate"]
    end
```

**Три ключевых хука:**

| Хук | Назначение |
|-----|------------|
| **dry-run-gate.sh** | Блокирует write-tools при наличии sentinel-файла. TTL: 10 мин (защита от `kill -9`). |
| **wp-gate-reminder.sh** | Проверяет наличие WP в MEMORY.md перед началом работы. Нет WP = СТОП. |
| **wakatime-heartbeat.sh** | Отправляет heartbeat в WakaTime каждые 2 минуты при работе в Kimi CLI. |

---

## 7. Ключевые скрипты — что куда записывает

Эта таблица описывает 10 основных скриптов и их роль в конвейере.  
**Главный смысл:** каждый скрипт — это автоматизация рутинной операции, которую иначе пришлось бы делать вручную и рисковать забыть шаг. Скрипты разделены по ролям: стратег (`strategist.sh`), экстрактор (`extractor.sh`), синхронизатор (`scheduler.sh`).

| Скрипт | Когда запускается | Что делает | Куда пишет |
|--------|-------------------|------------|------------|
| `day-close.sh` | Day Close (шаг 5) | Backup memory/, MCP reindex, Linear sync | `exocortex/memory-*/`, domain_event (Neon) |
| `update.sh` | Вручную / Day Open check | Синхронизация с FMT-exocortex-template | `.claude/*`, `scripts/*`, `memory/*` (selective) |
| `iwe-audit.sh` | audit-installation skill | Проверка 6 компонентов инсталляции | stdout (отчёт для Аудитора) |
| `iwe-drift.sh` | audit-installation (шаг 2) | Сравнение workspace vs FMT | stdout (diff report) |
| `mcp-healthcheck.sh` | Вручную / audit | Проверка MCP endpoint с Bearer token | stdout (latency + HTTP codes) |
| `kimi-wakatime-start.sh` | Day Open (extension) | Запуск фонового heartbeat | `.iwe-runtime/wakatime-kimi.pid` |
| `wp-sync-bundle.sh` | Day Open (шаг 3) | Сбор контекста WP + связанных | `/tmp/wp-sync-bundle-*.md` |
| `extractor.sh` | Cron / launchd (R2) | Inbox check, KE, ontology sync | `inbox/captures.md`, `Pack/` |
| `strategist.sh` | Cron / launchd (R1) | Day Open, Week Close, note-review | `current/DayPlan*`, `MEMORY.md` |
| `scheduler.sh` | Cron / launchd (R8) | Code scan, daily report, notify | `memory/*`, notifications |

**Как читать таблицу:**
- **Cron / launchd** — скрипты сидят в фоне и запускаются по расписанию, не требуя вмешательства.
- **stdout** — результат идёт прямо в консоль, откуда его подхватывает субагент (Аудитор или пользователь).
- **Selective** — `update.sh` обновляет только те файлы, которые помечены в манифесте; пользовательские правки в L3 не затираются.

---

## 8. Поток данных в memory/

Эта диаграмма показывает, как информация попадает в оперативную память и как оттуда читается.  
**Главный смысл:** `memory/` — это не просто папка с заметками, а **оперативная память экзокортекса**. Она должна оставаться компактной: MEMORY.md хранит только активные РП (in_progress + pending), done-РП удаляются на Week Close. Уроки ограничены восемью штуками; старые (>1 недели без применения) архивируются в `lessons_YYYY-MM.md`.

```mermaid
graph TB
    subgraph Inputs["Входы"]
        I1["Day Close<br/>Уроки, итоги"]
        I2["Sessions<br/>WP-context файлы"]
        I3["KE<br/>Извлечённые знания"]
        I4["Audit<br/>Gaps, рекомендации"]
        I5["User<br/>Ручные правки"]
    end

    subgraph Memory["memory/ — Оперативная память"]
        M1["MEMORY.md<br/>Активные РП + уроки"]
        M2["protocol-open.md<br/>Ритуал открытия"]
        M3["protocol-work.md<br/>Ритуал работы"]
        M4["protocol-close.md<br/>Ритуал закрытия"]
        M5["navigation*.md<br/>Карты и справочники"]
        M6["checklists.md<br/>Чеклисты"]
        M7["hard-distinctions.md<br/>Жёсткие пары"]
        M8["fpf-reference.md<br/>Принципы FPF"]
        M9["roles.md<br/>Роли и FX"]
        M10["sota-reference.md<br/>SoTA практики"]
    end

    subgraph Outputs["Выходы"]
        O1["Day Open<br/>Читает MEMORY.md"]
        O2["Week Close<br/>Ротация уроков"]
        O3["Skills<br/>Читают protocol-*.md"]
        O4["Auditor<br/>Проверяет свежесть"]
    end

    I1 --> M1
    I2 --> M1
    I3 --> M5
    I4 --> M6
    I5 --> Memory

    M1 --> O1
    M1 --> O2
    M2 --> O3
    M3 --> O3
    M4 --> O3
    M6 --> O4
```

**Правила гигиены памяти:**
- **MEMORY.md** — только активные РП. Done → архив.
- **Уроки** — ≤8 штук. Старые (>1 недели без применения) → `lessons_YYYY-MM.md`.
- **Protocol-файлы** — читаются скиллами при вызове run-protocol. Не меняются вручную — только через template-sync.
- **Navigation** — карты маршрутизации (например, `routing-vocab.md`), помогают скиллам определять куда писать новые знания.

---

## 9. Репозитории и их связи

Эта диаграмма показывает экосистему репозиториев вокруг IWE.  
**Главный смысл:** IWE — это хаб (root), который связывает стратегию (`DS-strategy`), предметные знания (`PACK-cattle-science`), обучение (`DS-cattle-course`) и внешнюю документацию (`DS-aisystant-docs`). Связи идут через git submodules и через логические потоки: бюджет из Strategy → WeekPlan → DayPlan, контент из Pack → Course, принципы из Docs → Memory.

```mermaid
graph TB
    subgraph IWE["🏠 IWE Root (Exocortex-V2)"]
        FMT["FMT-exocortex-template/<br/>(submodule, upstream)"]
        SCRIPTS["scripts/<br/>(4 кастомных + runtime)"]
        MEMORY["memory/<br/>(оперативная память)"]
        CLAUDE["CLAUDE.md<br/>(3-way merge)"]
    end

    subgraph Strategy["📊 DS-strategy"]
        WP["WP-REGISTRY.md"]
        WEEK["WeekPlan W{N}"]
        DAY["DayPlan YYYY-MM-DD"]
        STRAT["Strategy.md"]
        INBOX["inbox/<br/>WP-context файлы"]
    end

    subgraph Pack["📦 PACK-cattle-science"]
        SOTA["06-sota/<br/>CS.SOTA.XXX.md"]
        SYNTH["06-sota/synth/<br/>CS.SOTA.SYNTH.001"]
        METHOD["03-methods/<br/>CS.METHOD.XXX.md"]
        WP_PACK["04-work-products/<br/>CS.WP.XXX.md"]
    end

    subgraph Course["🎓 DS-cattle-course"]
        LECTURES["lectures/<br/>лекции 1–6"]
        MODULES["01-modules/<br/>модули воспроизводства"]
    end

    subgraph Docs["📚 DS-aisystant-docs"]
        COURSES["docs/ru/<br/>курсы СМ"]
    end

    FMT -->|"update.sh<br/>v0.34.1"| SCRIPTS
    MEMORY -->|"читает"| Strategy
    INBOX -->|"wp-new<br/>context file"| WP
    WP -->|"маппинг"| STRAT
    STRAT -->|"бюджет"| WEEK
    WEEK -->|"daily slot"| DAY

    SOTA -->|"synthesis"| SYNTH
    SYNTH -->|"learning"| METHOD
    METHOD -->|"downstream"| Course
    WP_PACK -->|"content"| Course

    Docs -->|"изучение"| Pack
    Docs -->|"принципы"| MEMORY
```

**Ключевые потоки:**
- **FMT → SCRIPTS** — `update.sh` тянет обновления шаблона в рабочую директорию. 3-way merge сохраняет USER-SPACE.
- **INBOX → WP** — при создании WP через `wp-new` контекстный файл помещается в `inbox/`, оттуда он попадает в реестр.
- **STRAT → WEEK → DAY** — каскад планирования: стратегия месяца → бюджет недели → слоты дня.
- **METHOD → Course** — методы из Pack становятся содержанием курса (лекции и модули).
- **Docs → MEMORY** — изучение внешней документации обогащает оперативную память (hard-distinctions, principles).

---

## 10. Ключевые принципы (чеклист понимания)

Этот раздел собирает 6 архитектурных правил в формате «что / зачем / следствие».  
**Главный смысл:** если вы понимаете эти 6 принципов, вы понимаете 80% того, как работает IWE. Нарушение любого из них приводит к известным anti-patterns: дрифту инсталляции, неконтролируемому росту MEMORY.md, смешению слоёв L1/L3.

### 1. L1 = Immutable
**Что:** `FMT-exocortex-template` никогда не правится руками. **Зачем:** смешение слоёв = хрупкость при обновлении. Пользовательские правки живут в L3 (`extensions/`, `params.yaml`). L1 обновляется только через `update.sh`.

### 2. WP Gate = Блокер
**Что:** Нет WP в MEMORY.md → работа не начинается. **Зачем:** предотвращает «инвентаризацию» — накопление незавершённых задач без учёта бюджета. Нет бюджета в WeekPlan → предупреждение.

### 3. SYNTH ≠ Rules
**Что:** SYNTH — только для обучения. Правила пишутся от **индивидуальных SoTA**. **Зачем:** защита от «controlled semantic coarsening». Усреднение разных источников маскирует важные нюансы. ArchGate обязателен для любого архитектурного решения.

### 4. Context Isolation
**Что:** Аудитор (R24) и Верификатор (R23) — субагенты **без истории сессии**. **Зачем:** если субагент видит, как артефакт создавался, он оценивает процесс, а не результат. Isolation гарантирует чистую проверку по эталону.

### 5. Atomic Writes
**Что:** `wp-new` = запись в 5 мест **атомарно**. **Зачем:** пропуск места = невалидный WP. Например, WP есть в WeekPlan, но нет в WP-REGISTRY → система не найдёт его при аудите.

### 6. Dry-Run Contract
**Что:** Sentinel-файл (`/tmp/iwe-dry-run-*.flag`) + `dry-run-gate.sh` = безопасное тестирование. **Зачем:** позволяет запускать протоколы (Day Close, Week Close) в режиме проверки без риска случайно записать что-то в файлы или базу данных.

---

## Как использовать этот документ

- **Obsidian:** Mermaid-диаграммы рендерятся нативно через плагин Mermaid Tools.
- **GitHub / GitLab:** Поддержка Mermaid в Markdown включена по умолчанию.
- **VS Code:** Используйте расширение Markdown Preview Mermaid Support.
- **Печать:** Экспортируйте через Pandoc или откройте HTML-версию (`memory/iwe-architecture-visual.html`) в браузере.
