#!/bin/bash
# kimi-wakatime-start.sh — запуск фонового heartbeat для Kimi CLI
set -euo pipefail

RUNTIME_DIR="${HOME}/IWE/.iwe-runtime"
PIDFILE="$RUNTIME_DIR/wakatime-kimi.pid"
LOGFILE="$RUNTIME_DIR/wakatime-kimi.log"
mkdir -p "$RUNTIME_DIR"

if [ -f "$PIDFILE" ]; then
  OLD_PID=$(cat "$PIDFILE")
  if ps -p "$OLD_PID" > /dev/null 2>&1; then
    echo "WakaTime heartbeat already running (PID $OLD_PID)"
    exit 0
  fi
fi

START_EPOCH=$(date +%s)
echo "START $START_EPOCH" >> "$LOGFILE"

(
  while true; do
    ~/.wakatime/wakatime-cli \
      --entity "IWE/Kimi CLI" \
      --plugin "kimi-cli" \
      --language Markdown \
      --write > /dev/null 2>&1 || true
    sleep 120
  done
) &

echo $! > "$PIDFILE"
echo "WakaTime heartbeat started (PID $!)"
