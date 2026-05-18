# WakaTime Kimi CLI — остановка heartbeat и запись в отчёт

## 1. Остановить heartbeat

```bash
bash "$IWE_ROOT/scripts/kimi-wakatime-stop.sh"
```

Вывод: длительность сессии в минутах (например, «Kimi CLI session: 120 min»).

## 2. Записать результат в отчёты

Прочитать `.iwe-runtime/wakatime-kimi.log`, взять последнюю строку `STOP <epoch> <min>`.

Добавить в WeekReport (факты дня) строку:
```
- **Kimi CLI tracked:** Xm
```

Добавить в session-log (секция Day Close) строку:
```
- **WakaTime Kimi session:** Xm
```

Если WeekReport не существует (fallback в WeekPlan) — записать туда же.

## 3. Рассчитать полный мультипликатор дня

```bash
# Физическое время = VS Code (WakaTime API) + Kimi CLI (heartbeat)
# VS Code время: ~/.wakatime/wakatime-cli --today
# Kimi CLI время: из .iwe-runtime/wakatime-kimi.log (последняя строка STOP)
```

Записать в итоги: «WakaTime total: VS Code Xm + Kimi CLI Ym = Zm».
