#!/usr/bin/env python3
"""Score and retrieve top-K lesson cards for a query (ACE-style retrieval).

Scoring = 0.5 * keyword_overlap + 0.3 * recency + 0.2 * usage_frequency.
Cards whose valid_until date has passed are excluded entirely (temporal
validity — a SAP release note from 2502 must not "poison" context once 2508
ships). Retrieved cards have usage_count incremented and last_used stamped,
so frequently-useful lessons keep rising to the top over time.

Usage:
  python lesson_card_retrieve.py <memory-root> <module> "<query text>" [--top-k 5]

Output (stdout, JSON): {"results": [{...card, "score": 0.73}, ...]}
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

RECENCY_WINDOW_DAYS = 180
USAGE_CAP = 10
MIN_SCORE = 0.05
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "la", "va", "khi", "cho", "neu", "thi", "nen", "can", "duoc", "khong",
    "the", "a", "an", "of", "to", "in", "on", "is", "are", "how", "what",
}


def tokenize(text):
    return {t for t in TOKEN_RE.findall((text or "").lower()) if t not in STOPWORDS and len(t) > 1}


def lessons_path(memory_root, module):
    return Path(memory_root) / "lessons" / f"{module.upper()}.jsonl"


def load_cards(path):
    if not path.exists():
        return []
    cards = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cards.append(json.loads(line))
    return cards


def save_cards(path, cards):
    with open(path, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")


def is_expired(card, today):
    valid_until = card.get("valid_until")
    if not valid_until:
        return False
    return date.fromisoformat(valid_until) < today


def score_card(card, query_tokens, today):
    fact_tokens = tokenize(card.get("fact", ""))
    keyword_overlap = (len(query_tokens & fact_tokens) / len(query_tokens)) if query_tokens else 0.0

    created = card.get("created")
    age_days = (today - date.fromisoformat(created)).days if created else RECENCY_WINDOW_DAYS
    recency = max(0.0, 1.0 - age_days / RECENCY_WINDOW_DAYS)

    usage_score = min(1.0, card.get("usage_count", 0) / USAGE_CAP)

    return 0.5 * keyword_overlap + 0.3 * recency + 0.2 * usage_score


def retrieve(memory_root, module, query, top_k=5):
    path = lessons_path(memory_root, module)
    cards = load_cards(path)
    today = date.today()

    live_cards = [c for c in cards if not is_expired(c, today)]
    query_tokens = tokenize(query)

    scored = [(score_card(c, query_tokens, today), c) for c in live_cards]
    # Require at least some keyword relevance — otherwise recency+usage alone
    # could surface a "popular" card for a query that has nothing to do with it.
    scored = [
        (s, c) for s, c in scored
        if s >= MIN_SCORE and (query_tokens & tokenize(c.get("fact", "")))
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = scored[:top_k]

    retrieved_ids = {c["id"] for _, c in top}
    if retrieved_ids:
        for c in cards:
            if c["id"] in retrieved_ids:
                c["usage_count"] = c.get("usage_count", 0) + 1
                c["last_used"] = today.isoformat()
        save_cards(path, cards)

    return [dict(c, score=round(s, 4)) for s, c in top]


def main():
    if len(sys.argv) < 4:
        print('Usage: lesson_card_retrieve.py <memory-root> <module> "<query>" [--top-k N]', file=sys.stderr)
        return 2

    memory_root, module, query = sys.argv[1], sys.argv[2], sys.argv[3]
    top_k = 5
    if "--top-k" in sys.argv:
        idx = sys.argv.index("--top-k")
        if idx + 1 < len(sys.argv):
            top_k = int(sys.argv[idx + 1])

    results = retrieve(memory_root, module, query, top_k=top_k)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
