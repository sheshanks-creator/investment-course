#!/usr/bin/env python3
"""
One-time migration: extract embedded content constants from index.html
into the content/ JSON tree, and regenerate topics/*/lesson.md from the
embedded LESSONS (the canonical version the user has been reading).

Run from the project root:  python3 scripts/migrate_content.py
Safe to re-run; output files are simply rewritten.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def slice_block(src, name):
    """Return the text of `const NAME = { ... };` including the final };"""
    start = src.index(f'const {name} = {{')
    end = src.index('\n};', start) + 3
    return src[start:end]


def js_object_to_python(block):
    """Convert a JS object literal (as authored in this repo) to a Python
    object, via string-placeholder tokenisation then JSON parsing.

    Handles: single/double-quoted strings with \\' escapes, template
    literals (no interpolation), unquoted keys, trailing commas."""
    # Drop the "const NAME = " prefix and trailing semicolon
    obj_text = block[block.index('{'):].rstrip()
    if obj_text.endswith(';'):
        obj_text = obj_text[:-1]

    strings = []
    out = []
    i = 0
    n = len(obj_text)
    while i < n:
        ch = obj_text[i]
        if ch == '`':
            j = obj_text.index('`', i + 1)
            strings.append(obj_text[i + 1:j])  # raw content, real newlines
            out.append(f'"@@S{len(strings)-1}@@"')
            i = j + 1
        elif ch == "'":
            j = i + 1
            buf = []
            while j < n:
                c = obj_text[j]
                if c == '\\':
                    nxt = obj_text[j + 1]
                    buf.append({'n': '\n', 't': '\t', "'": "'", '"': '"', '\\': '\\'}.get(nxt, nxt))
                    j += 2
                elif c == "'":
                    break
                else:
                    buf.append(c)
                    j += 1
            strings.append(''.join(buf))
            out.append(f'"@@S{len(strings)-1}@@"')
            i = j + 1
        elif ch == '"':
            j = i + 1
            buf = []
            while j < n:
                c = obj_text[j]
                if c == '\\':
                    nxt = obj_text[j + 1]
                    buf.append({'n': '\n', 't': '\t', "'": "'", '"': '"', '\\': '\\'}.get(nxt, nxt))
                    j += 2
                elif c == '"':
                    break
                else:
                    buf.append(c)
                    j += 1
            strings.append(''.join(buf))
            out.append(f'"@@S{len(strings)-1}@@"')
            i = j + 1
        elif ch == '/' and i + 1 < n and obj_text[i + 1] == '/':
            # line comment — skip to end of line
            j = obj_text.index('\n', i)
            i = j
        else:
            out.append(ch)
            i += 1

    structural = ''.join(out)
    # Quote unquoted keys (word chars followed by colon)
    structural = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', structural)
    # Also numeric keys:  1: { ... }
    structural = re.sub(r'([{,]\s*)(\d+)\s*:', r'\1"\2":', structural)
    # Remove trailing commas before } or ]
    structural = re.sub(r',(\s*[}\]])', r'\1', structural)

    data = json.loads(structural)

    def restore(x):
        if isinstance(x, str):
            m = re.fullmatch(r'@@S(\d+)@@', x)
            return strings[int(m.group(1))] if m else x
        if isinstance(x, list):
            return [restore(v) for v in x]
        if isinstance(x, dict):
            return {k: restore(v) for k, v in x.items()}
        return x

    return restore(data)


def main():
    src = open(INDEX, encoding='utf-8').read()

    all_titles = js_object_to_python(slice_block(src, 'ALL_TITLES'))
    lessons    = js_object_to_python(slice_block(src, 'LESSONS'))
    quiz_data  = js_object_to_python(slice_block(src, 'QUIZ_DATA'))
    case_data  = js_object_to_python(slice_block(src, 'CASE_DATA'))
    coach_data = js_object_to_python(slice_block(src, 'COACH_DATA'))
    num_data   = js_object_to_python(slice_block(src, 'NUM_QUIZ_DATA'))

    content = os.path.join(ROOT, 'content')
    for sub in ['quizzes', 'cases', 'coaches', 'num-quizzes']:
        os.makedirs(os.path.join(content, sub), exist_ok=True)

    # topics.json — all 120 titles with deterministic folder names
    topics = [
        {'id': int(tid), 'title': title, 'folder': f'{int(tid):02d}-{slugify(title)}'}
        for tid, title in sorted(all_titles.items(), key=lambda kv: int(kv[0]))
    ]
    with open(os.path.join(content, 'topics.json'), 'w', encoding='utf-8') as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)

    # Content items → one file each
    manifest = {'lessonTopics': sorted(int(k) for k in lessons), 'quizzes': [],
                'cases': [], 'coaches': [], 'numQuizzes': []}

    def write_items(items, subdir, prefix, key):
        for iid, obj in sorted(items.items(), key=lambda kv: int(kv[0])):
            fname = f'{subdir}/{prefix}-{int(iid):02d}.json'
            with open(os.path.join(content, fname), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
            manifest[key].append({'id': int(iid), 'file': fname})

    write_items(quiz_data,  'quizzes',     'quiz',  'quizzes')
    write_items(case_data,  'cases',       'cs',    'cases')
    write_items(coach_data, 'coaches',     'coach', 'coaches')
    write_items(num_data,   'num-quizzes', 'num',   'numQuizzes')

    with open(os.path.join(content, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # Regenerate lesson.md files from embedded LESSONS (canonical: it is what
    # the user has been reading and highlighting in the app)
    tmap = {t['id']: t for t in topics}
    for tid, body in lessons.items():
        tid = int(tid)
        folder = os.path.join(ROOT, 'topics', tmap[tid]['folder'])
        os.makedirs(folder, exist_ok=True)
        header = (f"# Topic {tid}: {tmap[tid]['title']}\n\n"
                  f"**~10 min read**\n\n---\n\n")
        with open(os.path.join(folder, 'lesson.md'), 'w', encoding='utf-8') as f:
            f.write(header + body.strip() + '\n')

    print(f"topics.json: {len(topics)} topics")
    print(f"lessons rewritten: {sorted(int(k) for k in lessons)}")
    print(f"quizzes: {len(quiz_data)}, cases: {len(case_data)}, "
          f"coaches: {len(coach_data)}, num-quizzes: {len(num_data)}")
    print("manifest.json written")


if __name__ == '__main__':
    sys.exit(main())
