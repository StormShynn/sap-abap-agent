#!/usr/bin/env python3
"""Append a lesson card to the SEMANTIC memory tier (ACE-style itemized fact).

Part of sap-daily-learner's self-improvement loop: after resolving a complex
question (or a systematic-debugging fix), extract 1-3 short fact snippets and
append them here instead of writing a whole new skill file — cheaper to write,
cheaper to retrieve (see lesson_card_retrieve.py), and deterministic merge
(append-or-skip-duplicate) means a bad extraction never destroys prior
knowledge the way a wholesale-rewrite would.

Storage: <memory-root>/lessons/<MODULE>.jsonl (one JSONL file per module;
each line is one lesson card). MODULE is upper-cased on write/read so callers
don't need to worry about case.

Input: a single JSON object on stdin:
  {"module": "FI", "topic": "acdoca", "fact": "...", "source_session": "...",
   "valid_until": "2027-01-01" (optional), "confidence": 0.9 (optional)}

Usage:
  echo '{"module":"FI","topic":"acdoca","fact":"..."}' | python lesson_card_add.py <memory-root>

Output (stdout, JSON): {"action": "added", "id": "..."} or
                       {"action": "skipped_duplicate", "similar_to": "..."}
"""
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

DUPLICATE_JACCARD_THRESHOLD = 0.8
TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return set(TOKEN_RE.findall(text.lower()))


def jaccard(a, b):
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def lessons_path(memory_root, module):
    d = Path(memory_root) / "lessons"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{module.upper()}.jsonl"


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


def find_duplicate(cards, topic, fact):
    fact_tokens = tokenize(fact)
    for card in cards:
        if card.get("topic") != topic:
            continue
        if jaccard(fact_tokens, tokenize(card.get("fact", ""))) >= DUPLICATE_JACCARD_THRESHOLD:
            return card
    return None


def add_card(memory_root, module, topic, fact, source_session=None, valid_until=None, confidence=0.85):
    path = lessons_path(memory_root, module)
    cards = load_cards(path)

    dup = find_duplicate(cards, topic, fact)
    if dup is not None:
        return {"action": "skipped_duplicate", "similar_to": dup["id"]}

    card = {
        "id": f"lc-{int(time.time())}-{format(hash(fact) & 0xFFFF, '04x')}",
        "module": module.upper(),
        "topic": topic,
        "fact": fact,
        "source_session": source_session,
        "created": date.today().isoformat(),
        "valid_until": valid_until,
        "confidence": confidence,
        "usage_count": 0,
        "last_used": None,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(card, ensure_ascii=False) + "\n")
    return {"action": "added", "id": card["id"]}


def main():
    if len(sys.argv) < 2:
        print("Usage: echo '<json>' | lesson_card_add.py <memory-root>", file=sys.stderr)
        return 2

    memory_root = sys.argv[1]
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"Invalid JSON on stdin: {e}", file=sys.stderr)
        return 2

    module = payload.get("module")
    topic = payload.get("topic")
    fact = payload.get("fact")
    if not module or not topic or not fact:
        print("Payload must include module, topic, fact", file=sys.stderr)
        return 2

    valid_until = payload.get("valid_until")
    if valid_until:
        try:
            datetime.strptime(valid_until, "%Y-%m-%d")
        except ValueError:
            print(f"valid_until must be YYYY-MM-DD, got: {valid_until!r}", file=sys.stderr)
            return 2

    result = add_card(
        memory_root, module, topic, fact,
        source_session=payload.get("source_session"),
        valid_until=valid_until,
        confidence=payload.get("confidence", 0.85),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
