#!/usr/bin/env python3
"""
Scan the configured research roots (wealth-agents + Obsidian vault) and
(re)build research-index.json. Preserves read/unread state; flips an entry
to unread when its file content changes.

Usage: python3 scripts/scan_research.py
"""
import sys

from research_lib import scan, load_index, save_index, configured_roots


def main():
    roots = configured_roots()
    if not roots:
        print('No research roots configured (config/research-sources.json absent '
              'or paths missing). Nothing to scan.')
        # Still write an empty index so the app degrades cleanly.
        save_index({'entries': []})
        return 0

    index = scan(previous=load_index())
    save_index(index)

    entries = index['entries']
    unread = sum(1 for e in entries if not e['read'])
    by_type = {}
    for e in entries:
        by_type[e['type']] = by_type.get(e['type'], 0) + 1
    tickers = sorted({e['ticker'] for e in entries})
    print(f'research-index.json: {len(entries)} docs, {unread} unread')
    print(f'  tickers: {", ".join(tickers)}')
    print(f'  by type: {by_type}')
    return 0


if __name__ == '__main__':
    # allow importing research_lib from same dir
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
