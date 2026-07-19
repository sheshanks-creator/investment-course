# Content Standards — Value Investing Course

House style for all course content: lessons, quizzes, case studies, coach walkthroughs, and numerical quizzes. Every authoring session (human or Claude Code) must follow these. The structural rules are enforced by `tests/test_content_schema.py`; the editorial rules are enforced by review.

---

## Universal rules

1. **Define metrics before using them.** The student is building financial literacy — never assume a term is known. Every scenario that uses financial metrics gets a "Note on Metrics" section that defines each term (PAT, ROE, P/E, GOV, take rate, working capital…) in one or two plain-English sentences *before* the first number appears. Terms already defined in an earlier item for the *same topic group* don't need re-definition; terms from earlier phases do.

2. **Real Indian companies, real numbers.** Use listed Indian companies with actual (simplified) financials — Pidilite, Nestlé India, Britannia, Marico, Zomato are used so far. Simplify for teaching, and say so ("simplified for teaching"). Fictional companies only when no real example fits cleanly.

3. **Never reuse a company across a coach case and its paired numerical quiz.** The quiz must test transfer, not memorisation (Coach 1 = Britannia, NumQuiz 1 = Marico).

4. **Direct, intellectually honest prose.** No hedging, no filler, no "as we all know". Explain *why* something matters, not just what it is. British-Indian English (₹ crore, lakh where natural).

5. **Difficulty tracks the curriculum.** Phase 1 (topics 1–10) assumes zero finance background. Later phases may assume everything previously taught — reference earlier topics by name when building on them ("recall from Topic 2 that…").

6. **No meta-commentary.** Content never mentions Claude, prompts, or generation. It reads as authored curriculum.

---

## Lessons (`topics/NN-slug/lesson.md`)

- File header: `# Topic N: Title`, a `**~10 min read**` line, then `---`, then the body. The app strips everything through the first `---` line on load.
- Body structure (from `docs/quiz-generation-prompt.md` lineage):
  `## A Quick Orientation` (bridge from prior topics) → 2–3 concept sections → `## A Real Company to Make This Concrete: <Name>` → `## The Most Common Mistake` → `REFLECTION:` line (one penetrating application question).
- 700–900 words. **Bold** key terms on first use, *italics* for emphasis.

## Quizzes (`content/quizzes/quiz-NN.json`)

- Keys: `id`, `title`, `topicIds` (the 3-topic group), `folder` (`quiz-NN-topics-X-Y`), `questions[]`.
- 7 open-ended questions: ~2 conceptual ("define / explain why"), ~3 application ("given this situation…"), ~2 synthesis requiring **two or more topics together**. The final question always requires applying *all* topics in the group to one scenario.
- Questions expose gaps, not recall. A question a student can answer by quoting the lesson verbatim is a bad question.

## Case studies (`content/cases/cs-NN.json`)

- Keys: `id`, `title` ("Case Study N — Evocative Name"), `subtitle` (company), `topicIds`, `folder` (`cs-NN-topics-X-Y`), `rubric`, `scenario`, `questions[]` (4 questions).
- Scenario: `## Background` → `## A Note on Metrics…` (definitions) → `## Financial Snapshot` (markdown table) → 2–3 analysis sections → a closing "The Question Investors Face" section. 1,500+ words; must contain enough *numbers* that every question can be answered quantitatively.
- Rubric: the standard 5 dimensions — Framework Accuracy (3), Case Specificity (3), Analytical Depth (3), Intellectual Honesty (2), Synthesis (2) = 13/question. Grade bands: 88+ Exceptional / 75+ Strong / 50+ Developing / 0+ Foundational.
- Question 4 always demands applying each topic framework *separately and explicitly*.
- Also create the matching `case-studies/cs-NN-topics-X-Y/` folder with `.gitkeep`.

## Coach walkthroughs (`content/coaches/coach-NN.json`)

- Keys: `id`, `title`, `subtitle`, `topicIds`, `folder` (`coach-NN-topics-X-Y`), `intro`, `steps[]`, `application`.
- `intro`: what this coach fixes, the company, and a full financials table.
- Each step: `heading` ("Step N — …"), `body` (the worked calculation with real arithmetic shown line by line, blockquote the key formula), plus the three boxes:
  - `keyIdea` — what the number *means* (1–2 sentences)
  - `applyElsewhere` — the transferable pattern (1–2 sentences)
  - `watchOut` — how this step misleads when applied blindly (1–2 sentences)
- `application`: a numbered reusable checklist + a pointer to what the student should do next.
- Every concept from the covered topics that has a numerical expression must appear in some step. **Show every calculation** — never "it can be shown that".
- Also create `coach-cases/coach-NN-topics-X-Y/` with `.gitkeep` (holds `answers.md` for the Q&A loop).

## Numerical quizzes (`content/num-quizzes/num-NN.json`)

- Keys: `id`, `title`, `subtitle`, `topicIds`, `folder` (`num-NN-topics-X-Y`), `scenario`, `questions[]` (8).
- `scenario`: company intro + financials table + a tolerance note + unit conventions ("percentages as numbers, e.g. 12.5 not 0.125; amounts in ₹ crore").
- Each question: `prompt` (markdown, bold `**QN — Skill name.**` lead), `answer` (number — NEVER a string), `unit` (`'crore'`, `'%'`, `'×'`, `'years'`, or `''`), `tolerance` (fraction, default 0.05), `explanation` (full worked solution: formula → substitution → result → one "interpretation" paragraph).
- The 8 questions must ladder through the paired coach's steps in the same order.
- Verify the arithmetic. Every `answer` must be recomputed independently before committing.

## Micro content (`content/micro/micro-NN.json`) — Telegram digests

- One file per topic: `{topicId, items[]}`. Each item: `type` (`card` | `mcq` | `exercise`), `concept` (from the vocabulary below), `text`, plus type-specific fields.
- **Cards**: 3–4 sentences of plain text (no markdown — the sender escapes everything). Restate one concept with a *fresh* example not used in the lesson. Standalone — readable with zero context on a phone.
  - **Plain-language rule (important):** these are read half-awake on a commute. Lead with the plain-English idea; never open with a technical term. If a term is unavoidable, define it in the same breath — "its expense ratio (annual fee)", "earnings yield (100 ÷ P/E)". Avoid unexplained jargon (EBITDA, drawdown, unit economics, PV, corpus, vesting) unless defined inline. Write like a smart friend explaining on a walk, not like a textbook. Feedback that a card "felt like a lot of jargon" is a defect to fix, not a style choice.
- **MCQs** ship as native Telegram quiz polls, so hard API limits apply (schema-tested): question ≤295 chars, 3–4 options of ≤100 chars each, explanation ≤200 chars. Wrong options should be *plausible* errors (e.g. the non-compounded CAGR), not filler.
- **Exercises**: a 5-minute research task on a *real, specific stock* the learner can look up (default tool: screener.in; funds via valueresearchonline.com). Fields: `stock` (company name), `concept`, `text`. The task must be concrete ("find X, compare to Y, write one line concluding Z"), doable in ~5 min, and reinforce the topic's concept through real data — this directly counters the "reaches for adjectives instead of numbers" gap. Keep `text` ≤700 chars; end with "(~5 min)". One exercise per topic (schema-enforced).
- ~3 cards + ~3 MCQs + 1 exercise per topic. Every lesson topic must have a micro file (schema-enforced).

### Concept vocabulary (shared ids)

Used by micro items, `learner-profile.md`, and the digest sender's weakness weighting. Add new ids here first.

`intrinsic-value` · `price-vs-value` · `cash-vs-profit` · `fcf-bridge` · `normalised-earnings` · `valuation-range` · `margin-of-safety` · `cheapness-vs-mos` · `time-horizon` · `institutional-constraints` · `compounding-math` · `circle-of-competence` · `competence-boundaries` · `second-order-thinking` · `incentives` · `inversion` · `pre-mortem` · `probabilistic-thinking` · `expected-value` · `base-rates` · `variant-perception` · `opportunity-cost` · `hurdle-rate` · `investor-behaviour` · `underperformance-causes` · `investing-vs-speculation` · `dcf-mechanics` · `discount-rate` · `terminal-value` · `roe` · `sustainable-growth` · `cagr` · `return-decomposition` · `explicit-framework-application`

---

## Pipeline for any authoring session

1. Read this file, `content/manifest.json`, and the relevant lesson(s).
2. Write the content file(s) + any required folders.
3. Add manifest entries (and topic ids to `lessonTopics` for new lessons).
4. `python3 tests/run_tests.py` — schema suite must pass.
5. Commit (pre-commit re-runs the tests).
