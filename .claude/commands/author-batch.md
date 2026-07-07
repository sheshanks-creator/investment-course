---
description: Author the next 3-topic batch — lessons + quiz + case study
argument-hint: <first-topic-id, e.g. 11>
---

Author course content for the 3-topic batch starting at topic $ARGUMENTS.

## Steps

1. **Read first:**
   - `docs/content-standards.md` — the house style (binding)
   - `content/topics.json` — titles for topics N, N+1, N+2
   - `content/manifest.json` — current content inventory and next free ids
   - The lesson.md of the 2–3 most recent topics, so the new lessons bridge naturally
   - `learner-profile.md` if it exists — weight known weak areas in quiz/case questions

2. **Write the three lessons** to `topics/NN-<slug>/lesson.md` (create folders; slug = lowercase title, non-alphanumerics → hyphens). Also create an empty-template `qa.md` per topic (see existing topics for the format). Follow the lesson structure in content-standards.

3. **Write the quiz** to `content/quizzes/quiz-NN.json` (next free quiz id). 7 questions per the standards; folder `quiz-NN-topics-X-Y`; create `quizzes/quiz-NN-topics-X-Y/` with `.gitkeep`.

4. **Write the case study** to `content/cases/cs-NN.json` (next free case id). Real Indian company relevant to the batch topics, full scenario with metric definitions and financial table; folder `cs-NN-topics-X-Y`; create `case-studies/cs-NN-topics-X-Y/` with `.gitkeep`.

5. **Update `content/manifest.json`:** append the three topic ids to `lessonTopics`, add the quiz and case entries.

6. **Verify:** run `source venv/bin/activate && python3 tests/run_tests.py`. All tests, especially the schema suite, must pass.

7. **Update state availability** if the user asked to unlock the batch: set `availableThrough` in `data/state.json` to the last topic id of the batch.

8. **Commit** with a message describing the batch (pre-commit re-runs tests).

9. **Report back:** one-paragraph summary per lesson, the quiz's synthesis questions, and the case study company + why it fits the topics. Flag anything where you deviated from the standards and why.

Do NOT copy question patterns verbatim from existing quizzes — vary the scenarios while keeping the difficulty ladder.
