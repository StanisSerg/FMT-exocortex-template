#!/bin/bash
# kimi-wakatime-stop.sh — остановка heartbeat и расчёт длительности сессии
set -euo pipefail

RUNTIME_DIR="${HOME}/IWE/.iwe-runtime"
PIDFILE="$RUNTIME_DIR/wakatime-kimi.pid"
LOGFILE="$RUNTIME_DIR/wakatime-kimi.log"

if [ ! -f "$PIDFILE" ]; then
  echo "No running heartbeat found"
  exit 1
fi

PID=$(cat "$PIDFILE")
if ps -p "$PID" > /dev/null 2>&1; then
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
fi

END_EPOCH=$(date +%s)
START_EPOCH=$(tail -1 "$LOGFILE" | awk '{print $2}')
DURATION=$((END_EPOCH - START_EPOCH))
DURATION_MIN=$((DURATION / 60))

echo "STOP $END_EPOCH $DURATION_MIN" >> "$LOGFILE"
rm -f "$PIDFILE"

echo "WakaTime heartbeat stopped. Kimi CLI session: ${DURATION_MIN} min"
