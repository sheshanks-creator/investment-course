# Research Bridge — linking wealth-agents research into the course

Weaves the user's real stock research (from the **wealth-agents** project + Obsidian vault) into the course: a **"My Research"** view in the app, and **personalised research exercises** in the Telegram digests.

## The privacy boundary (read this first)

- **Full research content is read live and locally only.** The app fetches it from the source files at request time; it is never copied into the repo and never committed.
- **Only a minimal watchlist is committed** — `sync/watchlist.json` = company names + which course concepts each relates to. No thesis prose, conviction, or position sizing. This exists so the **cloud** GitHub Action (which can't see your local files) can personalise digest exercises. It relies on the course repo staying **private**.
- `config/research-sources.json` (machine paths) and `research-index.json` (live index of your positions) are **gitignored**.

## How it works

```
wealth-agents/thesis/*.md ─┐
vault wiki/analyses/*.md   ─┼─►  scan_research.py  ─►  research-index.json  ─►  app "My Research" view (live content)
vault raw/sources/*.md    ─┘         (hash-based)         (gitignored)      └►  export_watchlist.py ─► sync/watchlist.json ─► digest
```

1. **Configure** — copy `config/research-sources.json.example` → `config/research-sources.json` and set the root paths for your machine.
2. **Scan** — `python3 scripts/scan_research.py` builds `research-index.json`: every `.md` under the roots (except templates), classified as `thesis` / `research` / `bull-bear` / `evaluation` / `source`, with ticker, company (market-suffix stripped), content hash, excerpt, and — for theses — a section→topic map.
3. **Serve** — the course server exposes `GET /api/research-index`, `GET /api/research/<id>` (path-safelisted to the configured roots; traversal rejected), and `POST /api/research/mark-read`.
4. **View** — "📁 My Research" appears in the sidebar with an unread badge; open a company to read its docs, with a banner linking each thesis section to the course topic it exercises.
5. **Digest** — `export_watchlist.py` distils the index into `sync/watchlist.json`; the sender personalises the morning research task to a real watchlist company when the day's concept matches (e.g. "Re-read your Pokarna pre-mortem…").

Steps 2 and 5 run automatically in the pre-commit hook, so a normal commit refreshes both.

## The read/unread ledger

`research-index.json` doubles as the ledger. Each entry has `read` + `readAt`. The scanner **preserves** these across runs but **flips `read:false` when a file's content hash changes** — so edited/new research shows up as unread. Opening a doc in the app marks it read.

### Index entry schema

```json
{
  "id": "16-hex-of-path",
  "path": "/abs/path/to/file.md",     // server-side only; never sent to the browser
  "ticker": "POKARNA.NS",
  "company": "POKARNA",                // market suffix stripped, for grouping
  "market": "IN",                       // IN if .NS/.BO else US
  "type": "research",                  // thesis | research | bull-bear | evaluation | source
  "title": "POKARNA · research",
  "filename": "pokarna.ns-research-2026-05-29.md",
  "mtime": 1748500000,
  "sha1": "…",                          // content hash; change ⇒ read reset
  "excerpt": "first meaningful line…",
  "concepts": ["circle-of-competence", "base-rates"],
  "read": false,
  "readAt": null,
  "sectionMap": [{"section": "3. Variant Perception…", "topicId": 7}]   // theses only
}
```

## Having wealth-agents update the index (optional)

The hash scan already re-detects any changed file, so wealth-agents needs to do nothing for freshness. If you *want* the other project to push updates directly, it can edit `research-index.json`:
- **Mark a doc unread** after regenerating it: set that entry's `"read": false`.
- **Add a new doc**: append an entry (minimally `id`, `path`, `ticker`, `company`, `type`, `sha1`, `read:false`); the next `scan_research.py` reconciles the rest.

Keep the id = first 16 hex chars of `sha1(path)` so the two projects agree on identity.

## Graceful degradation

If `config/research-sources.json` is absent or its paths don't resolve, `configured_roots()` returns empty: the scanner writes an empty index, "My Research" doesn't render, and digests fall back to the generic pre-authored exercises. The course stays fully self-contained; tests never touch your real files.
