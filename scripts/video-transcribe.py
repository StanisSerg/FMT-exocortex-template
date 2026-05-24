#!/usr/bin/env python3
"""
video-transcribe.py — транскрибация аудио/видео через faster-whisper.

Использование:
    python3 scripts/video-transcribe.py <media-file> [--model small] [--output <path>]
"""

import os
import sys
import argparse
from pathlib import Path
from faster_whisper import WhisperModel


def transcribe(media_path: str, model_size: str = "small", output_path: str = None):
    media = Path(media_path)
    if not media.exists():
        print(f"❌ Файл не найден: {media_path}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        output_path = media.with_suffix(".txt")
    else:
        output_path = Path(output_path)

    print(f"🎙️  Транскрибация: {media.name}")
    print(f"   Модель: {model_size}")
    print(f"   Устройство: CPU (int8)")
    print(f"   Вывод: {output_path}")
    print()

    # Загрузка модели
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    # Транскрибация
    segments, info = model.transcribe(str(media), beam_size=5, language="en", condition_on_previous_text=True)

    print(f"   Язык: {info.language} (confidence: {info.language_probability:.2f})")
    print(f"   Длительность: {info.duration:.1f} сек (~{info.duration/60:.1f} мин)")
    print()

    # Сохранение
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Транскрипция: {media.name}\n\n")
        f.write(f"- **Модель:** {model_size}\n")
        f.write(f"- **Язык:** {info.language}\n")
        f.write(f"- **Длительность:** {info.duration/60:.1f} мин\n")
        f.write(f"- **Дата транскрибации:** {__import__('datetime').datetime.now().isoformat()}\n\n")
        f.write("---\n\n")

        for segment in segments:
            timestamp = f"[{segment.start:.2f} -> {segment.end:.2f}]"
            f.write(f"{timestamp} {segment.text}\n")

    print(f"✅ Готово. Сохранено: {output_path}")
    print(f"   Сегментов: {sum(1 for _ in segments)}")


def main():
    parser = argparse.ArgumentParser(description="Транскрибация аудио/видео через faster-whisper")
    parser.add_argument("media", help="Путь к медиафайлу")
    parser.add_argument("--model", default="small", help="Размер модели (tiny, base, small, medium, large)")
    parser.add_argument("--output", default=None, help="Путь для сохранения транскрипции")
    args = parser.parse_args()

    transcribe(args.media, args.model, args.output)


if __name__ == "__main__":
    main()
