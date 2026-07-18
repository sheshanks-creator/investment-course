---
description: Author Telegram micro-content (cards + MCQs) for a topic
argument-hint: <topic-id>
---

Author the micro-content bank file for topic $ARGUMENTS (used by the twice-daily Telegram digests).

## Steps

1. **Read first:** `docs/content-standards.md` (the "Micro content" section is binding — note the Telegram limits: MCQ question ≤295 chars, options ≤100, explanation ≤200), the topic's `lesson.md`, and `learner-profile.md` for concepts worth extra reinforcement.

2. **Write `content/micro/micro-NN.json`**: ~3 cards + ~3 MCQs, each tagged with a concept id from the standards vocabulary. Cards use *fresh* examples, not the lesson's. MCQ wrong-answers must be plausible errors.

3. **Add the manifest entry** to the `micro` list in `content/manifest.json`.

4. **Verify:** `source venv/bin/activate && python3 tests/run_tests.py` (the micro schema tests enforce the Telegram limits), then spot-check with `python3 scripts/send_digest.py --slot morning --dry-run`.

5. **Commit.**
