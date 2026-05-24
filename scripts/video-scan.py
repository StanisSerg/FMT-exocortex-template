#!/usr/bin/env python3
"""
video-scan.py — сканирование видео/аудио при Day Open.

Читает day-rhythm-config.yaml, находит необработанные медиафайлы
и создаёт markdown-шаблоны для транскрибации / извлечения знаний.

Использование:
    python3 scripts/video-scan.py [--dry-run]

Вывод: markdown-список необработанных файлов для вставки в DayPlan.
"""

import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path

IWE_ROOT = Path("/home/asus/IWE")
CONFIG_PATH = IWE_ROOT / "memory" / "day-rhythm-config.yaml"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_media_files(config):
    """Находит медиафайлы по конфигу."""
    video_cfg = config.get("video", {})
    directories = video_cfg.get("directories", [])
    extensions = video_cfg.get("extensions", ["mp4", "mov", "webm"])
    ext_set = set(f"." + ext.lstrip(".") for ext in extensions)

    files = []
    for directory in directories:
        dir_path = Path(os.path.expanduser(directory))
        if not dir_path.exists():
            continue
        for root, _dirs, filenames in os.walk(dir_path):
            for filename in filenames:
                filepath = Path(root) / filename
                if filepath.suffix.lower() in ext_set:
                    files.append(filepath)
    return files


def get_transcript_path(media_path: Path, config) -> Path:
    """Возвращает путь к ожидаемому markdown-файлу транскрипта."""
    video_cfg = config.get("video", {})
    transcripts_dir = video_cfg.get("transcripts_dir", "transcripts")

    # transcripts_dir может быть абсолютным или относительным к первой директории
    if transcripts_dir.startswith("/"):
        base = Path(transcripts_dir)
    else:
        directories = video_cfg.get("directories", [])
        if directories:
            base = Path(os.path.expanduser(directories[0])) / transcripts_dir
        else:
            base = media_path.parent / transcripts_dir

    # Имя .md = базовое имя медиафайла + .md
    md_name = media_path.stem + ".md"
    return base / md_name


def extract_wp_from_filename(filename: str) -> str | None:
    """Извлекает номер WP из имени файла по паттерну WP-{N}."""
    match = re.search(r"WP[-_\s]?(\d+)", filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def extract_date_from_filename(filename: str) -> str | None:
    """Извлекает дату из имени файла (YYYY или YYYY-MM-DD)."""
    match = re.search(r"(20\d{2})", filename)
    if match:
        return match.group(1)
    return None


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"


def create_transcript_template(media_path: Path, transcript_path: Path, config) -> str:
    """Создаёт markdown-шаблон для медиафайла."""
    video_cfg = config.get("video", {})
    transcript_path.parent.mkdir(parents=True, exist_ok=True)

    wp = extract_wp_from_filename(media_path.name)
    year = extract_date_from_filename(media_path.name)
    file_size = format_file_size(media_path.stat().st_size)
    mtime = datetime.fromtimestamp(media_path.stat().st_mtime).strftime("%Y-%m-%d")

    wp_line = f"wp: {wp}" if wp else "wp: "
    date_line = f"date: {year}-01-01" if year else f"date: {mtime}"

    content = f"""---
type: video-transcript
{wp_line}
{date_line}
source: "{media_path.name}"
file_path: "{media_path}"
file_size: "{file_size}"
status: pending-transcription
---

# {media_path.stem}

## Метаданные
- **WP:** WP-{wp if wp else "?"}
- **Источник:** {media_path.stem}
- **Дата записи:** {year if year else "—"}
- **Длительность:** 
- **Файл:** `{media_path.name}` ({file_size})

## Краткое содержание (summary)
> Заполняется после просмотра / транскрибации.

## Key Claims
| Claim | Confidence | Timestamp |
|-------|-----------|-----------|
| | | |

## Loss Notes
- Что потеряно при сокращении / пересказе?

## Source Links
- 

## Action Items
- [ ] Транскрибировать (whisper / ручная расшифровка)
- [ ] Извлечь Key Claims
- [ ] Создать SoTA или обновить существующую
- [ ] Связать с WP-{wp if wp else "?"}
"""

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(transcript_path)


def main():
    dry_run = "--dry-run" in sys.argv

    if not CONFIG_PATH.exists():
        print(f"❌ Конфиг не найден: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    video_cfg = config.get("video", {})

    if not video_cfg.get("enabled", False):
        print("<!-- video.enabled = false — пропускаем -->")
        sys.exit(0)

    media_files = find_media_files(config)
    pending = []

    for media_path in media_files:
        transcript_path = get_transcript_path(media_path, config)
        if not transcript_path.exists():
            pending.append((media_path, transcript_path))

    if not pending:
        print("**Видео:** 0 необработанных записей.")
        sys.exit(0)

    print(f"**Видео:** {len(pending)} необработанных записей.")
    print("")

    for media_path, transcript_path in pending:
        wp = extract_wp_from_filename(media_path.name)
        wp_tag = f"WP-{wp}" if wp else "без WP"

        if not dry_run:
            create_transcript_template(media_path, transcript_path, config)
            status = f"🆕 Создан шаблон: `{transcript_path}`"
        else:
            status = f"⏸️ dry-run: будет создан `{transcript_path}`"

        print(f"- `{media_path.name}` ({wp_tag}) — {status}")

    print("")
    print("> **Action:** Просмотреть / транскрибировать → извлечь Key Claims → SoTA.")


if __name__ == "__main__":
    main()
