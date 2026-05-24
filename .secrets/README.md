# MCP Secrets

> Директория для чувствительных данных. Права: 700 (только владелец).
> НЕ коммитится в git (см. `.gitignore`).

## Текущие секреты

| Файл | Назначение | Статус |
|------|-----------|--------|
| `mcp-token.txt` | Bearer token для MCP (aisystant.com) | ⏳ Ожидает заполнения |

## Как получить MCP Bearer token

### Способ 1: Через браузер (рекомендуется)

1. Откройте https://aisystant.com/auth в браузере
2. Войдите в свой аккаунт
3. Откройте DevTools → Network (F12)
4. Найдите любой запрос к `aisystant.com` после входа
5. В Headers найдите `Authorization: Bearer eyJ...`
6. Скопируйте токен (всё после `Bearer `)

### Способ 2: Через localStorage

1. После входа на https://aisystant.com откройте DevTools → Console
2. Выполните:
   ```javascript
   copy(localStorage.getItem('ory_access_token'))
   ```
3. Токен скопирован в буфер обмена

### Способ 3: Через Claude Code (если MCP уже работает там)

```bash
# Claude Code хранит токен в Keychain/macOS или Secret Service/Linux
# Проверьте:
cat ~/.claude/settings.json | grep -i token
cat ~/.claude/.mcp.json | grep -i bearer
```

## Как сохранить

```bash
# После получения токена:
echo "YOUR_TOKEN_HERE" > /home/asus/IWE/.secrets/mcp-token.txt
chmod 600 /home/asus/IWE/.secrets/mcp-token.txt
```

## Проверка

```bash
bash /home/asus/IWE/scripts/mcp-healthcheck.sh
```
