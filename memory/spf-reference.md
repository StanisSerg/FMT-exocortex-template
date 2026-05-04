# SPF Reference — Справка по Second Principles Framework

> Быстрый справочник по SPF для работы с Pack'ами в Exocortex-V2.

---

## Что такое SPF

**SPF (Second Principles Framework)** — фреймворк формы и процесса для создания Pack'ов.

- **Назначение:** Стандартизация структуры доменных знаний
- **Upstream:** FPF (First Principles Framework)
- **Downstream:** Pack'и (PACK-cattle-science, и др.)
- **Локальный путь:** `../SPF/`

---

## Иерархия

```
FPF (Level 1) — мета-онтология
    ↓
SPF (Level 2) — форма + процесс
    ↓
Pack (Level 2) — доменное знание
    ↓
Downstream (Level 3) — курсы, приложения
```

---

## Структура SPF

```
SPF/
├── README.md              # Обзор
├── CLAUDE.md              # Инструкции для Claude
├── ontology.md            # Онтология SPF
├── docs/                  # Концептуальная документация
│   ├── conceptual-model.md
│   └── fpf-spf-pack.md
├── process/               # Процесс создания Pack'а
│   ├── 00-process-overview.md
│   ├── 01-domain-selection.md
│   ├── 02-bounded-context.md
│   ├── 03-distinctions-work.md
│   ├── 04-domain-entities-identification.md
│   ├── 05-information-ingestion.md
│   ├── 06-analysis-and-formalization.md
│   ├── 07-method-and-product-extraction.md
│   ├── 08-failure-modes-extraction.md
│   ├── 09-sota-annotation.md
│   ├── 10-map-maintenance.md
│   ├── 11-review-and-evolution-cycle.md
│   ├── material-ingestion-protocol.md
│   └── process-lint.md    # ← Проверка корректности
├── spec/                  # Спецификации
│   ├── ai-view.md
│   ├── downstream-contract.md
│   ├── human-guides.md
│   ├── SPF.SPEC.001-entity-coding.md
│   └── SPF.SPEC.003-pack-scalability.md
└── pack-template/         # Шаблон Pack'а
    ├── 00-pack-manifest.md
    ├── 01-domain-contract/
    ├── 02-domain-entities/
    ├── 03-methods/
    ├── 04-work-products/
    ├── 05-failure-modes/
    ├── 06-sota/
    └── 07-map/
```

---

## Структура Pack'а (pack-template/)

### Обязательные элементы

| Элемент | Файл/Папка | Описание |
|---------|-----------|----------|
| **Manifest** | `00-pack-manifest.md` | Паспорт Pack'а |
| **Domain Contract** | `01-domain-contract/` | Границы, различения, онтология |
| **Domain Entities** | `02-domain-entities/` | Сущности, роли, индексы |
| **Methods** | `03-methods/` | Методы работы |
| **Work Products** | `04-work-products/` | Рабочие продукты |
| **Failure Modes** | `05-failure-modes/` | Режимы отказа |
| **SoTA** | `06-sota/` | Источники, исследования |
| **Map** | `07-map/` | Навигация, индексы |

### Статус PACK-cattle-science

| Элемент | Статус | Примечание |
|---------|--------|------------|
| 00-pack-manifest.md | ✅ | Есть |
| 01-domain-contract/ | ✅ | Полный |
| 02-domain-entities/ | ⚠️ | Добавлены индексы |
| 03-methods/ | ✅ | 3 метода |
| 04-work-products/ | ✅ | 3 WP |
| 05-failure-modes/ | ✅ | Создан |
| 06-sota/ | ✅ | 29 источников |
| 07-map/ | ✅ | Есть |

**Соответствие SPF:** 85% → 95% (после обновлений)

---

## Процесс создания Pack'а

### Этапы (process/)

| # | Этап | Описание | Триггер |
|---|------|----------|---------|
| 01 | Domain Selection | Выбор области | Новая область |
| 02 | Bounded Context | Определение границ | Начало работы |
| 03 | Distinctions Work | Ключевые различения | Формирование ядра |
| 04 | Entities ID | Идентификация сущностей | После различений |
| 05 | Info Ingestion | Сбор информации | Постоянно |
| 06 | Analysis | Анализ и формализация | По мере накопления |
| 07 | Method Extraction | Извлечение методов | Стабилизация практик |
| 08 | Failure Modes | Режимы отказа | После методов |
| 09 | SoTA Annotation | Аннотация источников | Постоянно |
| 10 | Map Maintenance | Поддержка карт | Регулярно |
| 11 | Review & Evolution | Пересмотр и эволюция | Циклически |

### Текущий статус PACK-cattle-science

```
01 ✅ Domain Selection — Cattle Science
02 ✅ Bounded Context — Определены границы
03 ✅ Distinctions Work — Основные различения
04 ⚠️ Entities ID — Частично (нужно больше)
05 🔄 Info Ingestion — Активно (WP-75)
06 🔄 Analysis — По мере поступления
07 ✅ Method Extraction — 3 метода
08 ✅ Failure Modes — Создан раздел
09 🔄 SoTA Annotation — 29 источников
10 🔄 Map Maintenance — Регулярно
11 ⏳ Review & Evolution — Запланировано
```

---

## Кодирование сущностей (SPF.SPEC.001)

### Формат ID

```
[DOMAIN].[TYPE].[NUMBER]-[short-name]

Примеры:
- CS.ENTITY.001-21d-pregnancy-rate
- CS.METHOD.003-reproductive-economics
- CS.WP.003-reproduction-economic-report
- CS.FM.001-overestimation-21d-pr
- CS.SOTA.001-lauber-2025-economic-simulation
- CS.MAP.001-sota-index
```

### Типы сущностей

| Код | Тип | Описание | Пример |
|-----|-----|----------|--------|
| ENTITY | Сущность | Объект внимания | 21-d PR |
| METHOD | Метод | Способ действия | Экономическая оценка |
| WP | Work Product | Рабочий продукт | Отчёт |
| FM | Failure Mode | Режим отказа | Ошибка расчёта |
| SOTA | State of the Art | Источник знаний | Lauber 2025 |
| MAP | Map | Навигация | Индекс SoTA |
| ROLES | Roles | Роли | Ветеринар |
| TOOLS | Tools | Инструменты | ПО, оборудование |

### Диапазоны номеров

| Тип | Диапазон | Примечание |
|-----|----------|------------|
| ENTITY | 001-999 | Последовательно |
| METHOD | 001-599 | По категориям |
| WP | 001-999 | Последовательно |
| FM | 001-999 | Последовательно |
| SOTA | 001-999 | По подпапкам |

---

## Hard Bans (запреты)

### Запрет дидактики в Pack

**ЗАПРЕЩЕНО:**
- "step", "lesson", "in N days"
- "implement", "first/then"
- "exercise", "module", "week 1"

**ПРИЧИНА:** Дидактика — downstream (DS-cattle-course). Pack = **что существует**, не **как учить**.

### Запрет путаницы типов

| ❌ Путаница | ✅ Правильно |
|------------|-------------|
| Method = Tool | Method = как; Tool = чем |
| WP = Description | WP = артефакт; Description = текст |
| Role = Actor | Role = функция; Actor = исполнитель |

---

## Process Lint (process/process-lint.md)

### Что проверяет

| Проверка | Описание | Критичность |
|----------|----------|-------------|
| Structure | Соответствие pack-template | Критично |
| ID Format | Корректность идентификаторов | Критично |
| Uniqueness | Уникальность ID | Критично |
| Content | Отсутствие дидактики | Критично |
| Links | Валидность ссылок | Важно |
| Distinctions | Соблюдение Hard Distinctions | Важно |

### Как запустить

```bash
# Ручная проверка
- Прочитать process-lint.md
- Проверить каждый пункт
- Исправить нарушения

# Автоматическая (будущее)
- SPF linter (в разработке)
```

---

## Практические сценарии

### Сценарий 1: Добавить новую SoTA

```
1. Прочитать SPF/process/material-ingestion-protocol.md
2. Применить правила классификации
3. Создать CS.SOTA.XXX по шаблону
4. Обновить CS.MAP.001
5. Проверить lint
6. Commit
```

### Сценарий 2: Создать новый метод

```
1. Убедиться, что практика стабильна
2. Определить ID (CS.METHOD.XXX)
3. Создать файл по шаблону
4. Обновить 02C-methods-index.md
5. Связать с WP и FM
6. Проверить lint
7. Commit
```

### Сценарий 3: Исправить нарушение

```
1. Запустить process-lint.md
2. Найти нарушение
3. Исправить
4. Проверить снова
5. Commit с пометкой "lint fix"
```

---

## Обновление SPF

```bash
cd ../SPF
git pull
```

**Что проверить после обновления:**
- [ ] Новые версии process/
- [ ] Изменения в pack-template/
- [ ] Обновления spec/
- [ ] Breaking changes в CHANGELOG

**Адаптация:**
- Применить изменения к PACK-cattle-science
- Обновить отчёт о соответствии
- Протестировать процессы

---

## Ссылки

| Ресурс | Путь | Описание |
|--------|------|----------|
| SPF README | `../SPF/README.md` | Обзор |
| SPF CLAUDE | `../SPF/CLAUDE.md` | Инструкции |
| Pack Template | `../SPF/pack-template/` | Шаблон |
| Process | `../SPF/process/` | Процессы |
| Spec | `../SPF/spec/` | Спецификации |
| Репозиторий | https://github.com/TserenTserenov/SPF | GitHub |

---

*Создан: 2026-03-12*  
*Версия SPF: текущая*  
*Статус: Активное использование*
