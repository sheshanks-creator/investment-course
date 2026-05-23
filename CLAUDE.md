# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Commands

```bash
# Install dependencies (run once after cloning)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Initialise personal state (run once after cloning)
cp data/state.example.json data/state.json

# Start the course server
source venv/bin/activate
python3 server.py          # serves on http://localhost:8080

# Run the full regression test suite
python3 tests/run_tests.py

# Run tests without starting a server (frontend + content suites only)
python3 tests/run_tests.py --no-api

# Install the pre-commit hook (run once after cloning)
bash scripts/install-hooks.sh
```

There is no build step — `index.html` is served directly.

---

## Architecture

The application is a **single-page course player** made of two files:

### `index.html` — the entire front-end

One self-contained file (~2400 lines): all HTML, CSS, and JavaScript.

**Key data objects (all embedded as JS constants):**
- `LESSONS` — lesson Markdown keyed by topic ID (1–120). New topics are generated via `/api/generate` and written into this object at runtime.
- `QUIZ_DATA` — pre-authored quiz objects keyed by quiz ID. Each has `topicIds`, `title`, `questions[]`.
- `CASE_DATA` — pre-authored case study objects keyed by case ID. Each has `topicIds`, `scenario` (Markdown), `questions[]`, and a `rubric` object.
- `ALL_TITLES` — map of all 120 topic IDs → title strings.

**Runtime state (`ST`):** A single `ST` object mirrors `data/state.json`. It is fetched on load via `fetchState()` and synced back via `pushState()` on every meaningful change (mark done, highlight, note save).

**View model:** One active view at a time — lesson, quiz, or case study — controlled by `showLesson()`, `showQuiz(id)`, `showCaseStudy(id)`. The sidebar is rebuilt by `renderSidebar()` which inserts quiz and case study items after every 3rd topic using `(i+1) % 3 === 0`.

**Markdown rendering:** `mdToHtml(md)` — a hand-rolled line-by-line parser. Supports headings, bold, italic, lists, tables (`|`-delimited), blockquotes, and `---` rules. Tables are rendered as `.cs-table`. Extend this function when adding new Markdown features.

**Highlighting:** Text selection triggers `onTextSelect()` → colour picker bar → `applyHL()` stores the highlight in `ST.highlights[topicId]`. On lesson reload, `reapplyHighlights()` re-wraps matching text using `markTextInContainer()`.

**Q&A workflow (pending questions):** Questions are stored in `localStorage` under key `vic_pq` (not in `ST`). The user copies them, pastes into Claude Code, and answers are appended to the topic's `qa.md` file. `loadAnswers()` fetches that file and renders it.

**Auto-save:** Quiz and case study textarea inputs are debounced with `_qzDebounce` / `_csDebounce` (800 ms). Responses are kept in memory until `submitQuiz()` / `submitCaseStudy()` sends them to the server.

**Color themes:** Quiz module uses `--blue` / `--blue-bg`. Case study module uses `--amber` / `--amber-bg` / `--amber-bdr`. Both defined as CSS variables in `:root`.

---

### `server.py` — the Python HTTP server

Standard library only (except `anthropic`). No framework.

**Routing:**
| Method | Path | Handler |
|--------|------|---------|
| GET | `/`, `/index.html` | serves `index.html` |
| GET | `/api/state` | `load_state()` → JSON |
| POST | `/api/state` | `save_state(body)` |
| POST | `/api/chat` | `handle_chat()` — Anthropic API, streams Q&A |
| POST | `/api/generate` | `handle_generate()` — Anthropic API, generates lessons + quiz |
| POST | `/api/save-quiz-responses` | `handle_save_quiz_responses()` — writes `quizzes/<folder>/responses.md` |
| POST | `/api/save-case-responses` | `handle_save_case_responses()` — writes `case-studies/<folder>/responses.md` |
| POST | `/api/evaluate-quiz` | `handle_evaluate_quiz()` — Anthropic API, legacy path |
| GET | `*` | static file from project root |

**State file:** `data/state.json`. Path is overridable via `COURSE_STATE` env var (used by tests). Port is overridable via `COURSE_PORT` (default 8080, tests use 18080). `load_state()` always merges from defaults so old state files gain new keys automatically.

**File artefacts written by the server:**
- `topics/<id>-<slug>/lesson.md` — generated lesson content
- `topics/<id>-<slug>/qa.md` — Q&A log appended on each chat answer
- `quizzes/<folder>/responses.md` — user's quiz answers + evaluation placeholders
- `case-studies/<folder>/responses.md` — user's case study answers + rubric + placeholders

---

## Evaluation workflow (Claude Code's role)

When the user types **`evaluate quiz N`** or **`evaluate case study N`**:
1. Read `quizzes/quiz-0N-topics-X-Y/responses.md` or `case-studies/cs-0N-topics-X-Y/responses.md`
2. Evaluate each answer and replace the `*Pending — type "evaluate ..." in Claude Code.*` placeholder under each `**Evaluation:**` heading with detailed feedback
3. Replace the `*Pending evaluation.*` line under `## Overall Assessment` with a summary
4. Save the file — the user clicks **Load Evaluation** in the browser to fetch and display it

The evaluation rubric for case studies is in `docs/quiz-evaluation-rubric.md`.

---

## Content structure

```
topics/<NN>-<slug>/
  lesson.md    — the lesson content (authored or AI-generated)
  qa.md        — append-only Q&A log for that topic

quizzes/quiz-<NN>-topics-<X>-<Y>/
  responses.md — written on submission; evaluated by Claude Code

case-studies/cs-<NN>-topics-<X>-<Y>/
  responses.md — written on submission; evaluated by Claude Code

docs/          — authoring references (rubrics, prompts, topic list)
data/
  state.json         — personal progress (gitignored)
  state.example.json — blank template for new installs
```

Topics 1–10 are authored. Topics 11–120 are AI-generated on demand when the student completes a batch of three.

---

## Tests

118 tests across three suites in `tests/`:

- `test_api.py` — HTTP endpoint tests (requires live server on port 18080)
- `test_frontend.py` — static analysis of `index.html` (no server)
- `test_content.py` — file/folder structure checks (no server)

Human-readable descriptions of every test case are in `tests/test-cases.md`. The auto-generated pass/fail report is in `tests/test-report.md` (committed automatically by the pre-commit hook).

The pre-commit hook (`scripts/pre-commit.sh`, installed to `.git/hooks/pre-commit`) runs the full suite and stages the updated report before every commit. To skip in an emergency: `git commit --no-verify`.
