# WakaTime Kimi CLI — запуск heartbeat

Запустить фоновый heartbeat для трекинга времени в Kimi CLI:

```bash
bash "$IWE_ROOT/scripts/kimi-wakatime-start.sh"
```

Результат: PID процесса записан в `.iwe-runtime/wakatime-kimi.pid`.
Heartbeat отправляется каждые 2 минуты в WakaTime с entity="IWE/Kimi CLI".
