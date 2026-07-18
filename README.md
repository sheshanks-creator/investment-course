# Value Investing Course

A personal, self-hosted value investing course built as a single-page application. Lessons, quizzes, and case studies are authored upfront; progress, highlights, notes, and quiz/case responses are persisted locally via a lightweight Python server.

---

## Prerequisites

- Python 3.8+
- A modern browser (Chrome or Firefox recommended)
- Claude Code (for quiz and case study evaluation)

---

## Setup on a new machine

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/investment-course.git
cd investment-course
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate.bat     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialise your state file

```bash
cp data/state.example.json data/state.json
```

This creates a fresh progress file. Do not commit `data/state.json` — it contains your personal study data and is gitignored.

### 5. Start the server

```bash
python3 server.py
```

The server runs on **http://localhost:8080**. Keep this terminal open while studying.

### 6. Open the course

Open your browser and go to: **http://localhost:8080**

---

## Daily usage

1. `source venv/bin/activate` (if not already active)
2. `python3 server.py`
3. Open http://localhost:8080

To stop the server: `Ctrl+C` in the terminal.

---

## Quiz workflow

1. Complete three topics, then click the quiz item in the left sidebar.
2. Answer each question and navigate with Next / Back — responses auto-save.
3. Click **Submit Quiz** when done. A `responses.md` file is written to `quizzes/quiz-XX-topics-Y-Z/`.
4. In Claude Code chat, type: `evaluate quiz <N>` (e.g. `evaluate quiz 1`).
5. Claude reads the file, fills in per-question evaluations, and saves it.
6. Back in the browser, click **Load Evaluation** to view the feedback inline.

---

## Case study workflow

Same as quizzes, but for case studies:

1. After every 3 topics a case study appears in the sidebar (amber colour).
2. Read the scenario, answer the four analysis questions, submit.
3. In Claude Code chat, type: `evaluate case study <N>`.
4. Click **Load Evaluation** to view feedback.

---

## Telegram micro-digests

Twice-daily adaptive micro-learning on your phone: morning (8:00 IST) — a weakness-targeted concept card, an MCQ quiz poll, a numeric drill with a tap-to-reveal answer, and one of your own highlights resurfaced; evening (18:30 IST) — a shorter MCQ + drill. Sent by a GitHub Actions workflow, so it works even when your computer is off.

### One-time setup (~5 minutes)

1. **Create the bot.** In Telegram, message **@BotFather** → send `/newbot` → pick a name (e.g. "Value Investing Coach") and a username ending in `bot`. BotFather replies with a **token** like `1234567890:AAF...` — copy it.

2. **Get your chat id.** Send any message (e.g. "hi") to your new bot. Then open this URL in a browser, with your token substituted:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   In the JSON response, find `"chat":{"id":123456789,...}` — that number is your **chat id**.

3. **Add both as GitHub secrets.** In your repo: **Settings → Secrets and variables → Actions → New repository secret**:
   - `TELEGRAM_BOT_TOKEN` = the token from step 1
   - `TELEGRAM_CHAT_ID` = the number from step 2

4. **Push and test.** Push the repo, then go to **Actions → Telegram micro-digest → Run workflow**, pick `morning`, and run it. The digest should arrive on your phone within a minute.

After that, digests arrive automatically at 8:00 and 18:30 IST every day.

### How it adapts

Digest content is weighted toward your weak areas as recorded in `learner-profile.md` (updated by Claude Code every time it evaluates a quiz or case study). Your highlights and progress flow to the digest via `sync/learner.json`, which the pre-commit hook refreshes automatically — so the digests get smarter every time you commit and push.

### Testing locally

```bash
python3 scripts/send_digest.py --slot morning --dry-run    # prints instead of sending
```

---

## Project structure

```
index.html          ← single-page application (all HTML, CSS, JS)
server.py           ← Python HTTP server with REST endpoints
requirements.txt    ← pip dependencies
data/
  state.json        ← personal progress (gitignored)
  state.example.json← blank template for new installs
topics/
  01-*/             ← lesson.md + qa.md per topic
  ...
quizzes/
  quiz-01-*/        ← responses.md written on submission
case-studies/
  cs-01-*/          ← responses.md written on submission
docs/               ← authoring references and architecture notes
  requirements.md
  master-topic-list.md
  quiz-evaluation-rubric.md
  quiz-generation-prompt.md
  case-study-prompt.md
  example-case-study.md
```

---

## Server endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/state` | Load full state |
| POST | `/api/state` | Save full state |
| POST | `/api/save-quiz-responses` | Write quiz responses.md |
| POST | `/api/save-case-responses` | Write case study responses.md |

---

## Re-creating from scratch

If you need to rebuild on a new machine with no git history, everything needed to run the application is in the repository. The only file not tracked is `data/state.json` (personal progress). Copy from `data/state.example.json` and you start fresh.

If you want to restore your progress, copy your backed-up `state.json` into `data/` and your `responses.md` files back into their quiz/case-study folders.
