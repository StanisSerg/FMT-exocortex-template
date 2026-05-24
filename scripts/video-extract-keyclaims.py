#!/usr/bin/env python3
"""
video-extract-keyclaims.py — извлечение Key Claims из транскрипции.

Использование:
    python3 scripts/video-extract-keyclaims.py <transcript.txt> <template.md>
"""

import sys
import re
from pathlib import Path
from collections import Counter


def extract_segments(text: str):
    """Извлекает сегменты [start -> end] text."""
    pattern = re.compile(r"\[(\d+\.\d+) -> (\d+\.\d+)\]\s*(.*)")
    segments = []
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            segments.append({
                "start": float(m.group(1)),
                "end": float(m.group(2)),
                "text": m.group(3).strip()
            })
    return segments


def score_sentence(text: str) -> float:
    """Оцениваем 'ценность' предложения для Key Claim."""
    score = 0.0
    text_lower = text.lower()

    # Числовые данные = высокая ценность
    if re.search(r"\b\d+\.?\d*\s*(mg|g|kg|iu|mcg|ppm|%)\b", text_lower):
        score += 3.0
    if re.search(r"\b\d+\.?\d*\b", text_lower):
        score += 1.0

    # Ключевые термины transition cow nutrition
    keywords = [
        "calcium", "phosphorus", "magnesium", "potassium", "sodium", "sulfur",
        "vitamin d", "vitamin e", "vitamin a", "biotin", "choline",
        "requirement", "recommendation", "deficiency", "toxicity",
        "absorption", "bioavailability", "homeostasis", "parathyroid",
        "hypocalcemia", "milk fever", "retained placenta", "ketosis",
        "rumen", "dry matter", "intake", "negative energy",
        "bone", "resorption", "osteoclast", "kidney", "intestine"
    ]
    for kw in keywords:
        if kw in text_lower:
            score += 1.5

    # Прямые рекомендации
    if any(w in text_lower for w in ["should be", "must be", "needs to be", "recommend", "target", "optimal"]):
        score += 2.0

    # Конкретные механизмы
    if any(w in text_lower for w in ["because", "since", "therefore", "mechanism", "pathway", "hormone"]):
        score += 1.0

    # Штрафы за шум
    if any(w in text_lower for w in ["thank you", "good morning", "questions", "slide", "next"]):
        score -= 2.0

    return score


def generate_keyclaims(segments, top_n=15):
    """Генерирует top-N key claims по оценке."""
    scored = []
    for seg in segments:
        # Разбиваем на предложения
        sentences = re.split(r'(?<=[.!?])\s+', seg["text"])
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20:
                continue
            s = score_sentence(sent)
            if s >= 3.0:
                scored.append((s, seg["start"], sent))

    # Убираем дубликаты по схожести (простая эвристика — containment)
    scored.sort(key=lambda x: x[0], reverse=True)
    unique = []
    for s, ts, sent in scored:
        if len(unique) >= top_n:
            break
        # Проверяем, не является ли подстрокой уже выбранного
        if not any(sent in u[2] or u[2] in sent for u in unique):
            unique.append((s, ts, sent))

    return unique


def generate_summary(segments):
    """Генерирует краткое summary по ключевым темам."""
    all_text = " ".join(s["text"] for s in segments).lower()

    topics = Counter()
    topic_keywords = {
        "Calcium & P homeostasis": ["calcium", "phosphorus", "pth", "vitamin d", "bone", "resorption"],
        "Magnesium": ["magnesium", "mg", "hypomagnesemia"],
        "Vitamin E & Se": ["vitamin e", "selenium", "antioxidant"],
        "Trace minerals (Zn, Cu, Mn)": ["zinc", "copper", "manganese", "trace mineral"],
        "B-vitamins": ["biotin", "choline", "b vitamin", "niacin"],
        "Feed intake & DMI": ["dry matter", "intake", "dmi", "negative energy"],
        "Hypocalcemia prevention": ["hypocalcemia", "milk fever", "dcad", "anion"],
    }

    for topic, kws in topic_keywords.items():
        for kw in kws:
            topics[topic] += all_text.count(kw)

    # Топ-3 темы
    top_topics = topics.most_common(5)
    summary_lines = [f"- **{t}:** упоминается ~{c} раз" for t, c in top_topics if c > 0]

    return summary_lines


def update_template(template_path: Path, keyclaims, summary_lines):
    """Обновляет markdown-шаблон."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Summary
    summary_md = "\n".join(summary_lines)
    content = content.replace(
        "> Заполняется после просмотра / транскрибации.",
        f"> Авто-generated summary из транскрипции (faster-whisper small):\n>\n> {summary_md.replace(chr(10), chr(10)+'> ')}"
    )

    # Key Claims table
    claims_md = "\n".join(
        f"| {sent} | 0.85 | {int(ts//60)}:{int(ts%60):02d} |"
        for _s, ts, sent in keyclaims
    )
    content = content.replace(
        "| Claim | Confidence | Timestamp |\n|-------|-----------|-----------|\n| | | |",
        f"| Claim | Confidence | Timestamp |\n|-------|-----------|-----------|\n{claims_md}"
    )

    # Status
    content = content.replace(
        "status: pending-transcription",
        "status: transcribed"
    )

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(content)

    return template_path


def main():
    if len(sys.argv) < 3:
        print("Usage: video-extract-keyclaims.py <transcript.txt> <template.md>")
        sys.exit(1)

    transcript_path = Path(sys.argv[1])
    template_path = Path(sys.argv[2])

    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()

    segments = extract_segments(text)
    print(f"Сегментов: {len(segments)}")

    keyclaims = generate_keyclaims(segments, top_n=15)
    print(f"Key Claims выделено: {len(keyclaims)}")

    summary_lines = generate_summary(segments)
    print(f"Тем в summary: {len(summary_lines)}")

    update_template(template_path, keyclaims, summary_lines)
    print(f"✅ Шаблон обновлён: {template_path}")


if __name__ == "__main__":
    main()
