# CLAUDE.md — Инструкции для DS-cattle-operations

> **Тип репозитория:** DS (Instrument / Operations)  
> **Назначение:** Операционная работа с фермой, оценки, принятие решений  
> **Связь:** Использует PACK-cattle-science как source-of-truth

---

## Архитектура: Case → DL → Pack Rule

```
┌─────────────────────────────────────────────────────────────┐
│                    DS-cattle-operations                     │
├─────────────────────────────────────────────────────────────┤
│  cases/          decisions/         feed-additives/         │
│  (сырые факты)   (что решили)       (оценки добавок)        │
│       ↓                ↓                    ↓               │
│   CASE-001 ──→    DL-001 ──→    EVAL-001 ──→              │
│       ↓                ↓                    ↓               │
│   Валидация      Формализация      Применимость             │
│       ↓                ↓                    ↓               │
└───────┴────────────────┴────────────────────┴───────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│              PACK-cattle-science                            │
│              pack/rules/                                    │
│              (обобщённые знания)                            │
└─────────────────────────────────────────────────────────────┘
```

### Light Automation (структурированный ввод сразу)

**Принцип:** Сразу фиксируем правильно → потом масштабируем

```yaml
structured_capture:
  template: "templates/CASE-INPUT-TEMPLATE.yaml"
  политика: "structured only"
  notes_raw: "только контекст, НЕ для расчётов"
  
  обязательные_блоки:
    - A: identification
    - B: raw_measurements
    - C: derived_parameters (авто-расчёт)
    - D: clinical_flags
    - F: prediction (фиксируется ДО терапии)
    - G: decision
    - H: outcome (через 7-14 дней)
```

**Важно:**
- Все кейсы проходят через шаблон
- Prediction фиксируется сразу
- Формулы считаются одинаково (derived)

---

## Структура

### 1. cases/ — Сырые кейсы с фермы

**Формат:** `CASE-NNN-{краткое-описание}.md`

**Содержит:**
- Вход (параметры до)
- Действие (что делали)
- Результат (параметры после)

**Критерий готовности:**
- [ ] Заполнен structured input ([templates/CASE-INPUT-TEMPLATE.yaml](templates/CASE-INPUT-TEMPLATE.yaml))
- [ ] Prediction зафиксирован ДО терапии
- [ ] Outcome заполнен через 7-14 дней
- [ ] Classification (TP/FP/FN) определён

**Шаблон:** [cases/TEMPLATE-CASE.md](cases/TEMPLATE-CASE.md)  
**Structured Input:** [templates/CASE-INPUT-TEMPLATE.yaml](templates/CASE-INPUT-TEMPLATE.yaml) ← **использовать всегда**

---

### 2. decisions/ — Decision Layer

**Формат:** `DL-NNN-{краткое-описание}.md`

**Содержит:**
- Ссылка на CASE
- IF (условия)
- THEN (решение)
- BECAUSE (почему)
- LIMITS (где работает)

**Ключевой вопрос:** *«Что именно здесь было решением?»*

**Шаблон:** [decisions/TEMPLATE-DL.md](decisions/TEMPLATE-DL.md)

---

### 3. feed-additives/ — Оценки кормовых добавок

**Формат:** 
- `evaluations/EVAL-NNN-{добавка}-{условия}.md`
- `products/{название-производителя}/`

**Содержит:**
- Описание добавки
- Условия применения
- Оценка по правилам PACK
- Вывод: применять / не применять / требует проверки

**Шаблон:** [feed-additives/TEMPLATE-EVALUATION.md](feed-additives/TEMPLATE-EVALUATION.md)

---

## Workflow

### Добавление нового кейса

```bash
# 1. Создать из шаблона
cp cases/TEMPLATE-CASE.md cases/CASE-002-{описание}.md

# 2. Заполнить
# 3. Коммит
git add cases/CASE-002-{описание}.md
git commit -m "case: Описание ситуации"
```

### Извлечение решения (DL)

```bash
# 1. Создать DL
cp decisions/TEMPLATE-DL.md decisions/DL-002-{описание}.md

# 2. Заполнить на основе CASE
# 3. Коммит
git add decisions/DL-002-{описание}.md
git commit -m "decision: Что было решением в CASE-002"
```

### Оценка добавки

```bash
# 1. Создать оценку
cp feed-additives/TEMPLATE-EVALUATION.md \
   feed-additives/evaluations/EVAL-001-{добавка}-{условия}.md

# 2. Провести оценку по правилам PACK
# 3. Коммит
git add feed-additives/evaluations/EVAL-001-...
git commit -m "eval: Добавка X для условий Y"
```

---

## Связь с PACK-cattle-science

**PACK = source-of-truth:**
- Все правила живут в `PACK-cattle-science/pack/rules/`
- DS только *использует* правила
- При валидации в DS — предлагается перенос в PACK

**Ссылки в документах:**
```markdown
# В DL или Evaluation:
Согласно [RULE-002](https://github.com/StanisSerg/PACK-cattle-science/blob/main/pack/rules/RULE-002-sck-bhb-threshold.md)...
```

---

## Принципы работы

### 1. Capture-to-Pack
На каждом рубеже: есть ли знание для записи?
- Анонсировать: *«Capture: [что] → [куда]»*

### 2. Case → DL → Rule
Не останавливаться на кейсе. Вытащить решение. Сформализовать.

### 3. Evidence-based
Каждое решение должно иметь:
- Или ссылку на SoTA (PACK)
- Или собственную валидацию (несколько кейсов)

### 4. Автоматизация
Правила с высоким confidence → кандидаты для:
- Триггеров мониторинга
- AI-рекомендаций
- Алертов

---

## Триггеры для Claude

| Команда | Действие |
|---------|----------|
| `/case new` | Создать новый кейс |
| `/decision from CASE-NNN` | Создать DL из кейса |
| `/evaluate {добавка}` | Оценить кормовую добавку |
| `/pack rule` | Предложить правило в PACK |

---

## Блокирующие правила (из CLAUDE.md Base)

1. **WP Gate:** Любое задание → проверить в MEMORY.md
2. **Close:** push ≠ закрытие → capture + verify
3. **ArchGate:** Архитектурное решение → оценка

---

*Обновлено: 2026-04-11*
