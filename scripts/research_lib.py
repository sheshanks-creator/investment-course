#!/usr/bin/env python3
"""
Shared research-bridge helpers: config loading, source classification,
and the index read/write. Imported by scan_research.py, export_watchlist.py,
and server.py. No third-party deps.
"""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(ROOT, 'config', 'research-sources.json')
INDEX_FILE = os.path.join(ROOT, 'research-index.json')

# Thesis section heading -> course topic id it exercises
SECTION_TOPIC_MAP = [
    ('variant perception', 7),
    ('key assumptions', 7),
    ('scenarios', 7),
    ('pre-mortem', 6),
    ('kill criteria', 6),
    ('time horizon', 3),
    ('position & portfolio', 8),
    ('opportunity cost', 8),
    ('valuation framing', 2),
    ('the bet', 1),
    ('core thesis', 1),
    ('behavioural self-check', 9),
    ('what must be true', 5),
    ('catalysts', 5),
    ('circle', 4),
]

# Concept ids (shared with docs/content-standards.md) inferred from a doc's
# type + content, so the digest can map a ticker to the concepts it teaches.
TYPE_CONCEPTS = {
    'thesis': ['variant-perception', 'expected-value', 'pre-mortem', 'margin-of-safety'],
    'bull-bear': ['second-order-thinking', 'inversion', 'expected-value'],
    'research': ['circle-of-competence', 'base-rates'],
    'evaluation': ['pre-mortem', 'variant-perception', 'explicit-framework-application'],
    'source': ['circle-of-competence'],
}


def load_config():
    """Return the config dict, or {'roots': []} if absent (graceful degradation)."""
    try:
        with open(CONFIG_FILE, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {'roots': []}


def configured_roots():
    """Absolute, existing root directories from config."""
    roots = []
    for r in load_config().get('roots', []):
        p = os.path.realpath(os.path.expanduser(r.get('path', '')))
        if p and os.path.isdir(p):
            roots.append(p)
    return roots


def _classify(filename):
    """(type, is_template) from a markdown filename."""
    low = filename.lower()
    if low in ('investment_thesis_template.md', 'readme.md', 'claude.md'):
        return None, True
    if low.startswith('investment_thesis_'):
        return 'thesis', False
    if 'thesis-evaluation' in low or 'evaluation' in low:
        return 'evaluation', False
    if 'bull-bear' in low:
        return 'bull-bear', False
    if 'research' in low:
        return 'research', False
    if 'thesis' in low:
        return 'thesis', False
    return 'source', False


def _ticker(filename, ftype):
    name = filename[:-3] if filename.lower().endswith('.md') else filename
    if ftype == 'thesis' and name.lower().startswith('investment_thesis_'):
        return name[len('investment_thesis_'):].upper()
    # analyses pattern: <ticker>-<tag>-<date>.md
    m = re.match(r'^(.*?)-(research|bull-bear|thesis-evaluation|evaluation|analysis)\b',
                 name, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return name.split('-')[0].upper()


def _market(ticker):
    return 'IN' if ticker.upper().endswith(('.NS', '.BO')) else 'US'


def _company(ticker):
    """Normalised company key for grouping (strips the market suffix), so a
    POKARNA thesis and POKARNA.NS research group together."""
    return re.sub(r'\.(NS|BO)$', '', ticker.upper())


def _excerpt(text, limit=240):
    for raw in text.split('\n'):
        line = raw.strip()
        if not line or line.startswith(('#', '>', '<!--', '|', '---', '<', '-')):
            continue
        if line.startswith('[') and line.endswith(']'):  # template placeholder
            continue
        line = re.sub(r'[*_`]', '', line)
        return line[:limit]
    return ''


def _section_map(text):
    out = []
    for raw in text.split('\n'):
        if raw.startswith('## '):
            heading = raw[3:].strip().lower()
            for key, topic in SECTION_TOPIC_MAP:
                if key in heading:
                    out.append({'section': raw[3:].split('`')[0].strip(), 'topicId': topic})
                    break
    # de-dup preserving order
    seen, uniq = set(), []
    for s in out:
        k = (s['section'], s['topicId'])
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq


def scan(previous=None):
    """Walk configured roots; return an index dict. Preserves read/readAt from
    `previous` (keyed by id) but resets read=False when a file's sha changes."""
    prev_by_id = {}
    if previous:
        for e in previous.get('entries', []):
            prev_by_id[e['id']] = e

    entries = []
    seen_ids = set()
    for root in configured_roots():
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not fn.lower().endswith('.md'):
                    continue
                ftype, is_tpl = _classify(fn)
                if is_tpl or ftype is None:
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, encoding='utf-8') as f:
                        text = f.read()
                except OSError:
                    continue
                sha1 = hashlib.sha1(text.encode('utf-8')).hexdigest()
                fid = hashlib.sha1(path.encode('utf-8')).hexdigest()[:16]
                seen_ids.add(fid)
                ticker = _ticker(fn, ftype)
                prev = prev_by_id.get(fid)
                # read flag: preserve unless content changed
                if prev and prev.get('sha1') == sha1:
                    read, read_at = prev.get('read', False), prev.get('readAt')
                else:
                    read, read_at = False, None
                entry = {
                    'id': fid,
                    'path': path,
                    'ticker': ticker,
                    'company': _company(ticker),
                    'market': _market(ticker),
                    'type': ftype,
                    'title': f'{ticker} · {ftype.replace("-", "/")}',
                    'filename': fn,
                    'mtime': int(os.path.getmtime(path)),
                    'sha1': sha1,
                    'excerpt': _excerpt(text),
                    'concepts': TYPE_CONCEPTS.get(ftype, []),
                    'read': read,
                    'readAt': read_at,
                }
                if ftype == 'thesis':
                    entry['sectionMap'] = _section_map(text)
                entries.append(entry)

    entries.sort(key=lambda e: (e['ticker'], e['type'], -e['mtime']))
    import datetime
    return {'generatedAt': datetime.datetime.now().isoformat(), 'entries': entries}


def load_index():
    try:
        with open(INDEX_FILE, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {'entries': []}


def save_index(index):
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def entry_by_id(index, fid):
    for e in index.get('entries', []):
        if e['id'] == fid:
            return e
    return None


def path_is_safe(path):
    """True only if path resolves under a configured root (block traversal)."""
    rp = os.path.realpath(path)
    return any(rp == root or rp.startswith(root + os.sep) for root in configured_roots())
