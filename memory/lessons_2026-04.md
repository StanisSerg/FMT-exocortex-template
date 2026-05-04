---
valid_from: 2026-04-19
originSessionId: windows-wsl-audit-2026-04-19
---
# Уроки апреля 2026

## 2026-04-19 — Windows/WSL адаптация IWE

### PowerShell → WSL: inline-команды ломаются
- `&&`, `||`, `$(...)`, `2>/dev/null`, heredocs (`<<EOF`) — PowerShell интерпретирует эти символы ДО передачи в WSL.
- **Правило:** всегда запускать скрипты как файлы (`wsl bash ./script.sh`), а не inline (`wsl bash -c "..."`).
- Если inline unavoidable — оборачивать всё в одинарные кавыччи: `wsl bash -c '...'`.

### Ubuntu `.bashrc` guard прерывает non-interactive shells
- `.bashrc` содержит `case $- in *i*) ;; *) return;; esac` — при `source ~/.bashrc` из `.profile` в non-interactive shell возвращается.
- **Правило:** env-переменные (IWE_WORKSPACE и др.) должны source'иться напрямую из `~/.profile`, не полагаться на `.bashrc`.
- Fallback: `~/.zshenv` (zsh) → `~/.bashrc` (bash) — оба должны содержать `source ~/.iwe-paths`.

### Hardcoded пути — массовая проблема шаблона
- Найдено 40+ вхождений `/home/asus/`, `/root/IWE`, `FMT-exocortex-template` в скриптах, .plist, config.yaml, markdown.
- **Правило:** использовать `$HOME` / `$IWE_WORKSPACE` / `Path(__file__)` вместо абсолютных путей. Проверять через `grep -rn "/home/\|/root/IWE" .` перед коммитом.

### Python: `Path(__file__).resolve()` для derive путей
- `PACK-cattle-science/scripts/*.py` содержали `d:/Exocortex-V2/...` и `/root/IWE/...`.
- **Правило:** `BASE_DIR = Path(__file__).resolve().parent.parent` — надёжнее абсолютных путей и работает на любой платформе.

### CSV encoding: `utf-8-sig` для Excel BOM
- `herd_loader.py` использовал `encoding="utf-8"`, но Excel на Windows сохраняет CSV с BOM (`utf-8-sig`).
- **Правило:** для CSV, которые могли редактироваться в Excel, использовать `encoding="utf-8-sig"`.
