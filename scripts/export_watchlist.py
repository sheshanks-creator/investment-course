#!/usr/bin/env python3
"""
Export a MINIMAL watchlist from research-index.json for the Telegram digest.

sync/watchlist.json contains only tickers + the course concepts each company's
research relates to — NEVER thesis prose, conviction, or sizing. It is committed
so the cloud GitHub Action can personalise research exercises. Everything richer
stays local (served by the app from the live files).

Run automatically by the pre-commit hook.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(ROOT, 'research-index.json')
OUT_DIR = os.path.join(ROOT, 'sync')
OUT_FILE = os.path.join(OUT_DIR, 'watchlist.json')


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    try:
        with open(INDEX_FILE, encoding='utf-8') as f:
            index = json.load(f)
    except (FileNotFoundError, ValueError):
        index = {'entries': []}

    companies = {}
    for e in index.get('entries', []):
        if e.get('removed'):
            continue
        co = e.get('company') or e.get('ticker')
        c = companies.setdefault(co, {
            'company': co,
            'market': e.get('market', 'US'),
            'concepts': set(),
            'topics': set(),
            'hasThesis': False,
            'docCount': 0,
        })
        c['docCount'] += 1
        if e.get('market') == 'IN':
            c['market'] = 'IN'  # any Indian listing marks the company Indian
        c['concepts'].update(e.get('concepts', []))
        if e.get('type') == 'thesis':
            c['hasThesis'] = True
        for s in e.get('sectionMap', []):
            c['topics'].add(s['topicId'])

    watchlist = []
    for c in sorted(companies.values(), key=lambda x: x['company']):
        watchlist.append({
            'company': c['company'],
            'market': c['market'],
            'concepts': sorted(c['concepts']),
            'topics': sorted(c['topics']),
            'hasThesis': c['hasThesis'],
            'docCount': c['docCount'],
        })

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({'watchlist': watchlist}, f, ensure_ascii=False, indent=2)

    print(f'sync/watchlist.json: {len(watchlist)} companies '
          f'({", ".join(c["company"] for c in watchlist)})')


if __name__ == '__main__':
    main()
