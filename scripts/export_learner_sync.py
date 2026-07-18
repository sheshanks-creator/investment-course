#!/usr/bin/env python3
"""
Export learner state for the Telegram digest sender.

Reads data/state.json (personal, gitignored) + learner-profile.md (committed)
and writes sync/learner.json (committed) — the compact view the GitHub Action
uses to adapt digests. Run automatically by the pre-commit hook.
"""
import json
import os
import re
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(ROOT, 'data', 'state.json')
PROFILE_FILE = os.path.join(ROOT, 'learner-profile.md')
OUT_DIR = os.path.join(ROOT, 'sync')
OUT_FILE = os.path.join(OUT_DIR, 'learner.json')


def load_state():
    try:
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def parse_weak_concepts():
    """Parse the '## Weak concepts' markdown table from learner-profile.md."""
    weak = []
    try:
        with open(PROFILE_FILE, encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        return weak

    in_section = False
    for line in text.split('\n'):
        if line.startswith('## '):
            in_section = line.strip().lower() == '## weak concepts'
            continue
        if in_section and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 2 and cells[0] not in ('concept', '') and not set(cells[0]) <= {'-', ' '}:
                try:
                    severity = int(cells[1])
                except ValueError:
                    continue
                weak.append({'concept': cells[0], 'severity': severity})
    return weak


def main():
    state = load_state()
    os.makedirs(OUT_DIR, exist_ok=True)

    highlights = []
    for topic_id, hls in (state.get('highlights') or {}).items():
        for hl in hls:
            highlights.append({
                'topicId': int(topic_id),
                'text': hl.get('text', ''),
                'note': hl.get('note', ''),
            })

    out = {
        'exportedAt': datetime.date.today().isoformat(),
        'completed': state.get('completed', []),
        'availableThrough': state.get('availableThrough', 3),
        'weakConcepts': parse_weak_concepts(),
        'highlights': highlights,
    }

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"sync/learner.json written: {len(out['weakConcepts'])} weak concepts, "
          f"{len(highlights)} highlights, availableThrough={out['availableThrough']}")


if __name__ == '__main__':
    main()
