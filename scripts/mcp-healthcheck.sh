#!/bin/bash
# MCP Healthcheck — ручная проверка для Kimi CLI environment
# Usage: bash scripts/mcp-healthcheck.sh [--with-token]
# Токен берётся из .secrets/mcp-token.txt (создайте по инструкции .secrets/README.md)

set -euo pipefail

IWE_ROOT="${IWE_ROOT:-/home/asus/IWE}"
TOKEN_FILE="$IWE_ROOT/.secrets/mcp-token.txt"
MCP_URL="https://mcp.aisystant.com/mcp"

echo "========================================"
echo "  MCP Healthcheck"
echo "========================================"
echo "  Endpoint: $MCP_URL"
echo "  Token file: $TOKEN_FILE"
echo ""

# Проверка наличия токена
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ TOKEN NOT FOUND"
    echo ""
    echo "Создайте токен по инструкции:"
    echo "  cat $IWE_ROOT/.secrets/README.md"
    echo ""
    echo "Быстрый старт:"
    echo "  echo 'YOUR_BEARER_TOKEN' > $TOKEN_FILE"
    echo "  chmod 600 $TOKEN_FILE"
    exit 1
fi

TOKEN=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
if [ -z "$TOKEN" ]; then
    echo "❌ TOKEN FILE EMPTY"
    echo "   $TOKEN_FILE существует, но пустой."
    exit 1
fi

echo "✅ Token found (${#TOKEN} chars)"
echo ""

# Healthcheck: initialize request
echo "[1/4] knowledge_search (initialize + search)..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}s" \
    -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "iwe-audit", "version": "1.0.0"}
        }
    }' 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
TIME=$(echo "$RESPONSE" | grep "TIME:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/,$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "    ✅ OK ($TIME)"
else
    echo "    ❌ FAIL — HTTP $HTTP_CODE ($TIME)"
    echo "    Body: $BODY"
fi

# Проверка других endpoints (если initialize прошёл)
echo ""
echo "[2/4] github_status..."
echo "    ⏸️  Нет отдельного endpoint — зависит от knowledge_search"

echo ""
echo "[3/4] personal_search..."
echo "    ⏸️  Подписочный tool — требует active subscription"

echo ""
echo "[4/4] dt_read_digital_twin..."
echo "    ⏸️  Подписочный tool — требует active subscription"

echo ""
echo "========================================"
echo "  Coverage: зависит от подписки"
echo "========================================"
echo ""
echo "Если initialize возвращает 200, но tools недоступны:"
echo "  → Проверьте подписку на aisystant.com"
echo ""
