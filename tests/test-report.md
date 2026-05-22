# Test Report — Value Investing Course

**Run date:** 2026-05-22 23:39
**Duration:** 0.2s
**Result:** ✅ ALL PASS
**Summary:** 118 passed · 0 failed · 0 skipped · 118 total

---

## ✅ Content — docs/ folder (6/6)

| Test | Status | Detail |
|------|--------|--------|
| case study prompt exists | ✅ PASS |  |
| docs dir exists | ✅ PASS |  |
| master topic list exists | ✅ PASS |  |
| quiz evaluation rubric exists | ✅ PASS |  |
| quiz generation prompt exists | ✅ PASS |  |
| requirements md exists | ✅ PASS |  |

## ✅ Content — project root files (9/9)

| Test | Status | Detail |
|------|--------|--------|
| gitignore excludes state json | ✅ PASS |  |
| gitignore excludes venv | ✅ PASS |  |
| gitignore exists | ✅ PASS |  |
| index html exists | ✅ PASS |  |
| readme exists | ✅ PASS |  |
| readme has setup instructions | ✅ PASS |  |
| requirements txt contains anthropic | ✅ PASS |  |
| requirements txt exists | ✅ PASS |  |
| server py exists | ✅ PASS |  |

## ✅ Content — quiz & case folders (4/4)

| Test | Status | Detail |
|------|--------|--------|
| case studies dir exists | ✅ PASS |  |
| cs 01 folder exists | ✅ PASS |  |
| quiz 01 folder exists | ✅ PASS |  |
| quizzes dir exists | ✅ PASS |  |

## ✅ Content — state.example.json (7/7)

| Test | Status | Detail |
|------|--------|--------|
| completed is empty list | ✅ PASS |  |
| file exists | ✅ PASS |  |
| file is valid json | ✅ PASS |  |
| has available through key | ✅ PASS |  |
| has case responses key | ✅ PASS |  |
| has completed key | ✅ PASS |  |
| has quiz responses key | ✅ PASS |  |

## ✅ Content — topic folders (5/5)

| Test | Status | Detail |
|------|--------|--------|
| all ten topic folders exist | ✅ PASS |  |
| all topics have lesson md | ✅ PASS |  |
| all topics have qa md | ✅ PASS |  |
| lesson md files are non empty | ✅ PASS |  |
| topics dir exists | ✅ PASS |  |

## ✅ Frontend — API endpoint strings (4/4)

| Test | Status | Detail |
|------|--------|--------|
| api generate referenced | ✅ PASS |  |
| api save case responses referenced | ✅ PASS |  |
| api save quiz responses referenced | ✅ PASS |  |
| api state get referenced | ✅ PASS |  |

## ✅ Frontend — CSS variables (6/6)

| Test | Status | Detail |
|------|--------|--------|
| accent variable | ✅ PASS |  |
| amber bdr variable | ✅ PASS |  |
| amber bg variable | ✅ PASS |  |
| amber variable | ✅ PASS |  |
| blue variable | ✅ PASS |  |
| ok variable | ✅ PASS |  |

## ✅ Frontend — HTML structure (8/8)

| Test | Status | Detail |
|------|--------|--------|
| case submit button | ✅ PASS |  |
| has case view | ✅ PASS |  |
| has doctype | ✅ PASS |  |
| has inter font link | ✅ PASS |  |
| has main element | ✅ PASS |  |
| has quiz view | ✅ PASS |  |
| has sidebar element | ✅ PASS |  |
| quiz submit button | ✅ PASS |  |

## ✅ Frontend — index.html existence (2/2)

| Test | Status | Detail |
|------|--------|--------|
| file exists | ✅ PASS |  |
| file is non trivial | ✅ PASS |  |

## ✅ Frontend — JS data objects (3/3)

| Test | Status | Detail |
|------|--------|--------|
| CASE DATA present | ✅ PASS |  |
| LESSONS present | ✅ PASS |  |
| QUIZ DATA present | ✅ PASS |  |

## ✅ Frontend — JS functions (16/16)

| Test | Status | Detail |
|------|--------|--------|
| autoSaveCaseResponse | ✅ PASS |  |
| autoSaveQuizResponse | ✅ PASS |  |
| fetchState | ✅ PASS |  |
| init | ✅ PASS |  |
| loadCaseEvaluation | ✅ PASS |  |
| loadEvaluation | ✅ PASS |  |
| loadTopic | ✅ PASS |  |
| markDone | ✅ PASS |  |
| mdToHtml | ✅ PASS |  |
| pushState | ✅ PASS |  |
| renderSidebar | ✅ PASS |  |
| showCaseStudy | ✅ PASS |  |
| showFromCase | ✅ PASS |  |
| showQuiz | ✅ PASS |  |
| submitCaseStudy | ✅ PASS |  |
| submitQuiz | ✅ PASS |  |

## ✅ API — CORS & OPTIONS preflight (3/3)

| Test | Status | Detail |
|------|--------|--------|
| get state has cors origin wildcard | ✅ PASS |  |
| options has allow methods | ✅ PASS |  |
| options preflight returns 200 | ✅ PASS |  |

## ✅ API — GET /api/state (12/12)

| Test | Status | Detail |
|------|--------|--------|
| body is valid json | ✅ PASS |  |
| content type is json | ✅ PASS |  |
| required key available through | ✅ PASS |  |
| required key case responses | ✅ PASS |  |
| required key completed | ✅ PASS |  |
| required key current topic | ✅ PASS |  |
| required key highlights | ✅ PASS |  |
| required key qa | ✅ PASS |  |
| required key quiz responses | ✅ PASS |  |
| required key quizzes | ✅ PASS |  |
| required key topic notes | ✅ PASS |  |
| returns 200 | ✅ PASS |  |

## ✅ API — POST /api/state (5/5)

| Test | Status | Detail |
|------|--------|--------|
| has cors header | ✅ PASS |  |
| highlights persisted | ✅ PASS |  |
| returns 200 | ✅ PASS |  |
| returns ok true | ✅ PASS |  |
| saved value retrievable | ✅ PASS |  |

## ✅ API — POST /api/save-case-responses (11/11)

| Test | Status | Detail |
|------|--------|--------|
| endpoint returns 200 | ✅ PASS |  |
| endpoint returns ok | ✅ PASS |  |
| has cors header | ✅ PASS |  |
| responses md contains evaluation placeholder | ✅ PASS |  |
| responses md contains question | ✅ PASS |  |
| responses md contains rubric | ✅ PASS |  |
| responses md contains title | ✅ PASS |  |
| responses md contains user answer | ✅ PASS |  |
| responses md created | ✅ PASS |  |
| responses md no response handled | ✅ PASS |  |
| state case responses updated | ✅ PASS |  |

## ✅ API — POST /api/save-quiz-responses (10/10)

| Test | Status | Detail |
|------|--------|--------|
| endpoint returns 200 | ✅ PASS |  |
| endpoint returns ok | ✅ PASS |  |
| has cors header | ✅ PASS |  |
| responses md contains evaluation placeholder | ✅ PASS |  |
| responses md contains question | ✅ PASS |  |
| responses md contains submitted status | ✅ PASS |  |
| responses md contains title | ✅ PASS |  |
| responses md contains user answer | ✅ PASS |  |
| responses md created | ✅ PASS |  |
| state quiz responses updated | ✅ PASS |  |

## ✅ API — Static file serving (5/5)

| Test | Status | Detail |
|------|--------|--------|
| index html returns html | ✅ PASS |  |
| root returns 200 | ✅ PASS |  |
| state example json served | ✅ PASS |  |
| unknown path has cors header | ✅ PASS |  |
| unknown path returns 404 | ✅ PASS |  |

## ✅ API — Unknown endpoints (2/2)

| Test | Status | Detail |
|------|--------|--------|
| unknown post returns 404 | ✅ PASS |  |
| unknown post returns json error | ✅ PASS |  |
