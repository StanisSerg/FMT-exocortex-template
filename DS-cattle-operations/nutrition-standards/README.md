# Нормы питания КРС (Nutrition Standards)

> **Версия:** 0.1.0  
> **Источники:** CNCPS 2025, NASEM 2021  
> **Статус:** 🚧 В разработке (partial — извлечены ключевые группы, остальные в процессе)

---

## Назначение

Машиночитаемая нормативная база для оценки коммерческих продуктов и рационов.  
Источник истины — PDF-оригиналы в `sources/`. Все производные файлы (`extracted/`, `reference/`) генерируются из них.

## Структура репозитория

```
nutrition-standards/
├── sources/              # Исходные PDF (read-only)
│   ├── CNCPS-2025.pdf
│   ├── NASEM-2021.pdf
│   └── README.md
├── extracted/            # Структурированные данные из PDF
│   ├── CNCPS-2025/
│   │   └── requirements.yaml
│   ├── NASEM-2021/
│   │   └── table-21-1.yaml   # partial
│   └── README.md
├── reference/            # Сводные справочники
│   ├── quick-reference.md
│   └── README.md
├── validation/           # Тесты корректности данных
├── groups/               # Рационы по группам животных
│   ├── dry-period/
│   ├── transition-period/
│   ├── fresh-period/
│   ├── lactation-early/
│   ├── lactation-mid/
│   ├── lactation-late/
│   ├── heifers/
│   ├── calves/
│   └── bulls/
├── README.md             # Этот файл
└── TEMPLATE-NORM.md      # Шаблон для новых норм
```

---

## Быстрый доступ

| Что нужно | Куда идти |
|-----------|-----------|
| Сравнить продукт с нормой | `reference/quick-reference.md` |
| Данные CNCPS 2025 | `extracted/CNCPS-2025/requirements.yaml` |
| Данные NASEM 2021 | `extracted/NASEM-2021/` |
| Проверить источник | `sources/README.md` |
| Добавить новую группу | `TEMPLATE-NORM.md` |

---

## Источники

### CNCPS 2025
**Cornell Net Carbohydrate and Protein System**  
T. R. Overton, M. E. Van Amburgh, L. E. Chase  
Cornell University, 2025  
https://cncps.cornell.edu/

### NASEM 2021
**Nutrient Requirements of Dairy Cattle: Eighth Revised Edition**  
National Academies of Sciences, Engineering, and Medicine  
The National Academies Press, Washington, DC, 2021  
DOI: https://doi.org/10.17226/25806

---

## Статус извлечения

| Источник | Группы | Статус |
|----------|--------|--------|
| CNCPS 2025 | 4 группы (dry 1, dry 2, fresh, high-producing) | ✅ Готово |
| NASEM 2021 | Таблица 21-1, группа dry | 🚧 Partial |
| NASEM 2021 | Таблицы 21-2, 21-3 | 🚧 В процессе |

---

## Принципы работы

1. **PDF — read-only.** Не редактируем. Обновления — заменой файла + перегенерация.
2. **YAML — машиночитаемый формат.** Все числа, единицы, диапазоны — структурированы.
3. **Markdown — человекочитаемые сводки.** Генерируются из YAML.
4. **Partial допустимо.** Не ждём 100% покрытия перед коммитом. Коммитим частями с пометкой `status: partial`.

---

## История изменений

- **2026-04-22** — Создание репозитория, извлечение CNCPS 2025, partial NASEM 21-1, quick-reference.md
