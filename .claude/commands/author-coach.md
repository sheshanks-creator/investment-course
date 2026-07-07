---
description: Author a coach walkthrough + numerical quiz for a topic group
argument-hint: <first-topic-id>-<last-topic-id, e.g. 4-6>
---

Author a Coach case (worked walkthrough) and its paired Numerical Quiz for topics $ARGUMENTS. These are created on demand — when the student hits a mechanics wall — so tailor them to what the student is struggling with.

## Steps

1. **Read first:**
   - `docs/content-standards.md` — binding, especially the Coach and Numerical Quiz sections
   - The lesson.md files for the covered topics
   - `learner-profile.md` if it exists, plus the student's most recent quiz/case `responses.md` evaluations — the coach must target the *actual* observed gaps, the way Coach 1 targeted "reaches for adjectives instead of numbers"
   - `content/coaches/coach-01.json` as the structural reference

2. **Pick two different real Indian companies** — one for the coach walkthrough, a different one for the numerical quiz (transfer, not memorisation).

3. **Write the coach** to `content/coaches/coach-NN.json` (next free id): intro with financials table, 6–10 steps that each show a full calculation plus the keyIdea / applyElsewhere / watchOut boxes, and an application checklist. Every numerically-expressible concept from the covered topics must appear in a step. Create `coach-cases/coach-NN-topics-X-Y/` with `.gitkeep`.

4. **Write the numerical quiz** to `content/num-quizzes/num-NN.json` (next free id): 8 questions laddering through the coach's steps in order. Every `answer` must be a number you have independently recomputed — do the arithmetic twice. Create folder entry per standards.

5. **Update `content/manifest.json`** with both entries.

6. **Verify:** `source venv/bin/activate && python3 tests/run_tests.py` — schema suite must pass.

7. **Commit** (pre-commit re-runs tests).

8. **Report back:** which observed weaknesses each step targets, and the full answer key with one-line derivations so the user can sanity-check the arithmetic.
