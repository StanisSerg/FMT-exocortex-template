# Навигация: DS-aisystant-docs

> Репо: `DS-aisystant-docs` (submodule) — VitePress документация курсов системного мышления
> Upstream: https://github.com/aisystant/docs
> Source-of-truth контента: https://github.com/aisystant/PACK-personal

---

## Быстрый доступ по курсам

### Личностное (personal)

| Курс | Путь | Темы |
|------|------|------|
| Саморазвитие | `docs/ru/personal/1-1-self-development/` | Физический мир, тренинг, внимание, системный подход, роли, траектория |
| Методы саморазвития | `docs/ru/personal/1-2-self-development-methods/` | Второй мозг, инвестиции времени, чтение, письмо, речь, досуг, среда, стратегирование, планирование |
| Введение в системное мышление | `docs/ru/personal/1-3-systems-thinking-introduction/` | Системы, роли, типы систем, уровни, моделирование, создание |
| Системный фитнес | `docs/ru/personal/systems-based-fitness/` | Регуляция, усилия, техники, диафрагмы, координация |

### Профессиональное (professional)

| Курс | Путь | Темы |
|------|------|------|
| Системное мышление | `docs/ru/professional/systems-thinking/` | Мышление, интересы, креативность, реализация систем |
| Системное моделирование | `docs/ru/professional/systems-modeling/` | Описание систем, онтология 3 поколения, уровни, графы создателей |
| Моделирование-1 | `docs/ru/professional/modeling-1/` | Базовое моделирование, внимание, коммуникация, лидерство |
| Моделирование-2 | `docs/ru/professional/modeling-2/` | Языки, знаки, типы моделей, онтология, презентация |
| Системная инженерия | `docs/ru/professional/systems-engineering/` | Процессы, DevOps, архитектура, масштабирование |
| Системный менеджмент | `docs/ru/professional/systems-management/` | Лидерство, бизнес, операционный менеджмент, стратегия |
| Методология | `docs/ru/professional/methodology/` | Метод как объект, стратегия, инженерные процессы |
| Тушение пожаров | `docs/ru/professional/firefighting/` | Фокус, ресурсы, язык, метод vs работа |
| Контрфактуальность | `docs/ru/professional/counterfactuality/` | Причинность, объяснения, исследования |
| Инженерия личности | `docs/ru/professional/personality-engineering/` | Образование, обучение, культурная практика |

### Исследовательское (research)

| Курс | Путь | Темы |
|------|------|------|
| Стек интеллекта | `docs/ru/research/intellect-stack/` | Эстетика, алгоритмика, этика, логика, математика, онтология, физика, риторика, семантика, методология |

---

## Связь с текущими РП

| РП | Релевантные курсы |
|----|-------------------|
| WP-1 (Саморазвитие) | `personal/1-1-self-development`, `personal/1-2-self-development-methods` |
| WP-97 (Модуль воспроизводства) | `professional/personality-engineering`, `professional/methodology` |
| WP-94 (FPF) | `professional/methodology`, `professional/systems-thinking` |
| WP-78 (Метрики) | `professional/methodology`, `research/intellect-stack` |

---

## Использование

**Поиск по содержимому:**
```bash
grep -r "термин" DS-aisystant-docs/docs/ru/
```

**Чтение курса:**
```bash
cat DS-aisystant-docs/docs/ru/professional/systems-thinking/index.md
```

**Сборка VitePress:**
```bash
cd DS-aisystant-docs/docs && npm install && npm run docs:dev
```

---

*Создано: 2026-05-24. Обновляется при добавлении новых курсов.*
