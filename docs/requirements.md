# Value Investing Cockpit — Full Requirements Specification

## 1. Purpose & Context

A personal AI-powered value investing system for a busy professional who:
- Has limited time due to job and family duties
- Has a tendency to procrastinate on investing
- Wants to learn value investing systematically over 12 months
- Wants AI to collapse the time cost of learning and research dramatically

---

## 2. Delivery Mechanism

- **Primary interface:** Interactive web app (artifact/widget) running inside claude.ai in the browser
- **No separate login, no download required** to get started
- **Standalone HTML file** as the migration target — downloadable, openable in any browser, works on phone and laptop
- **GitHub Pages** as the eventual hosting target for true device independence
- The app uses `sendPrompt()` to fire structured prompts into the claude.ai chat — Claude responds there
- No direct API calls from the widget (blocked by sandbox CORS policy)
- Fallback: copy prompt to clipboard when running outside claude.ai

---

## 3. Data Persistence

- All state saves to **browser localStorage** between sessions
- **Export JSON** button — downloads full state snapshot as a `.json` file
- **Import JSON** button — reloads state from a previously exported file
- JSON file is the portable backup and cross-device sync mechanism
- User commits to one primary browser for localStorage continuity
- Data captured in JSON includes:
  - Concepts learned (array of topic indices)
  - Notes per topic
  - Quiz scores and history
  - Watchlist companies
  - Investment memos
  - Session count
  - Current lesson pointer

---

## 4. Context Reloading (Session Briefing System)

The single most important architectural feature. Because Claude has no memory between chats:

- The app auto-generates a **Session Briefing** — a compressed, structured intelligence file
- The briefing is NOT a transcript — it is a tight summary of everything that matters
- At the start of every new chat, user pastes the briefing and says: *"Load my investing session"*
- Claude reads it in seconds and resumes as if no session was lost

### Session Briefing contains:
- Current phase and curriculum status
- Full list of concepts learned
- Next topic up
- Quiz average score and weak areas flagged
- Unresolved questions / open threads from prior sessions
- Watchlist companies
- Memos written
- Session count

### Master Briefing (monthly):
- High-altitude view of progress
- Demonstrated strengths and gaps
- Investing thesis as it has evolved
- Companies researched and current conclusions

---

## 5. Curriculum

### Source
Based on the uploaded curriculum document, preserved as-is with 120 topics across 12 phases.

### Structure

| Phase | Topic | Weeks | Topics |
|-------|-------|-------|--------|
| 1 | Core Foundations | 1–4 | 1–10 |
| 2 | Financial Statements | 5–6 | 11–20 |
| 3 | Business Quality & Moats | 7–9 | 21–30 |
| 4 | Management & Capital Allocation | 10–11 | 31–40 |
| 5 | Returns & Metrics | 12–13 | 41–50 |
| 6 | Valuation | 14–16 | 51–60 |
| 7 | Industries & Business Models | 17–19 | 61–70 |
| 8 | Behaviour & Psychology | 20–21 | 71–80 |
| 9 | Portfolio Construction | 22–23 | 81–90 |
| 10 | Finding Opportunities | 24–25 | 91–100 |
| 11 | Thesis Building & Review | 26–27 | 101–110 |
| 12 | Master Thinking | 28+ | 111–120 |

### Lesson prompt format (per topic):
- Clear introduction — assume learner is coming in fresh
- 3–5 substantive paragraphs going deep
- 1 real-world company example (well-known)
- 1 common investor mistake on this topic
- 1 reflection question at the end
- Direct, intellectually honest, beyond surface level

---

## 6. Learning Flow

The system supports a specific learning pattern:

1. **Micro-lesson** — Claude delivers the lesson in chat
2. **Follow-up questions** — user asks freely in chat; Claude has full context
3. **After every 4–5 concepts** — a case study to solidify understanding
4. **Evaluation** — tight quiz to assess retention
5. **Notes** — user saves personal notes per topic in the app
6. **Mark as learned** — user confirms readiness before moving on

This flow must never be lost between sessions. The Session Briefing preserves:
- Which concepts are learned
- What questions were asked and whether they were resolved
- What case studies were completed
- Quiz scores and weak areas

---

## 7. App Tabs & Features

### Dashboard
- Metrics: concepts learned, current phase, average quiz score, sessions done
- Curriculum progress bar per phase (12 phases)
- "Next up" widget showing next topic
- Recent quiz scores

### Today's Lesson
- Topic selector (all 120 topics, learned ones marked ✓)
- Prompt preview — shows exactly what will be sent to Claude
- **Send to chat** button — fires lesson prompt via `sendPrompt()`
- Notes field — saves per topic to localStorage
- Mark as learned button
- Quick link to quiz

### Quiz
- Topic selector
- **Send to chat** button — fires quiz prompt (4-question multiple choice)
- User answers in chat, then comes back to log score manually
- Score logger — 4/4, 3/4, 2/4, 1/4, 0/4
- Score history with colour coding (green ≥70%, red <70%)
- Weak areas automatically flagged for revisiting

### Research
- Company input + analysis type selector:
  - Moat analysis
  - Management quality
  - Bear case
  - Valuation sense-check
  - Full overview
- Prompt preview
- **Send to chat** button
- Add to watchlist
- Draft memo shortcut

### Memos
- New memo editor
- **Get AI draft** button — fires memo prompt to chat, user pastes response back
- Save / delete memos
- Memo list with preview

### Session Briefing
- Auto-generates full structured briefing
- Regenerate button
- Copy to clipboard button
- Instructions for pasting into new chat

---

## 8. Weekly Workflow (Target)

| Time | Activity | AI Role |
|------|-----------|---------|
| Sunday, 15 min | One concept/lesson | Claude teaches via sendPrompt |
| Wednesday, 15 min | Screen 2–3 companies | Claude analyses via sendPrompt |
| Whenever interested | Company deep dive | Claude researches via sendPrompt |
| Quarterly, 30 min | Portfolio review | Claude stress-tests theses |

---

## 9. Technical Architecture

```
claude.ai browser session
│
├── Widget (HTML artifact)
│   ├── UI: tabs, forms, buttons, progress tracking
│   ├── State: localStorage (vic3 key)
│   ├── Prompts: generated and fired via sendPrompt()
│   └── Export/Import: JSON file via browser download/upload
│
├── Claude (chat)
│   ├── Receives lesson / quiz / research / memo prompts
│   ├── Responds in chat — user reads there
│   └── No API key required inside claude.ai
│
└── Session Briefing
    ├── Generated by app from localStorage state
    ├── Copied by user at end of session
    └── Pasted at start of next session to reload context
```

### Standalone HTML file (migration target):
- Single `.html` file, no dependencies
- Same UI and localStorage logic
- `sendPrompt()` when inside claude.ai, clipboard fallback otherwise
- Host on **GitHub Pages** for permanent URL accessible from any device
- URL format: `username.github.io/investing-cockpit`

---

## 10. Design Principles

- **Zero friction to start** — open app, hit send, lesson appears
- **Pre-built prompts** — no blank page, no thinking required to begin
- **Progressive** — each session builds on the last, nothing is lost
- **Honest evaluation** — quizzes are conceptual, not trivial; weak areas flagged
- **User owns the data** — JSON export means no lock-in, no server dependency
- **Version labelled** — app header shows version so user always knows which build to use
- **Works on phone and laptop** — responsive layout, localStorage-based

---

## 11. What Is Explicitly Out of Scope (For Now)

- Real-time stock data or price feeds
- Automated portfolio tracking
- Multi-user or shared access
- Backend server or database
- Native mobile app
- Automated push notifications (calendar block is the manual substitute)

---

## 12. Migration Roadmap

| Stage | What | When |
|-------|------|-------|
| **Now** | Use widget inside claude.ai | Immediately |
| **Month 1** | Validate the system works for your learning style | After first 4–5 topics |
| **Month 2** | Download standalone HTML, open in Chrome | When proven |
| **Month 3** | Push to GitHub Pages for permanent URL | When ready for device independence |
| **Year 2+** | Full hosted app with real DB if needed | Only if outgrown vibe coding |

