# Test Cases — Value Investing Course

118 test cases across three suites. Run with `python3 tests/run_tests.py`.

---

## Suite 1 — API Endpoint Tests

These tests start a live server on port 18080 with an isolated temporary state file, make real HTTP requests, and verify responses. They cover every server route that the front-end depends on.

---

### Static File Serving

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 1 | Root returns 200 | GET request to `/` (the course homepage) | HTTP 200 OK |
| 2 | index.html returns HTML | GET `/index.html` and inspect the Content-Type header | HTTP 200 with `text/html` in Content-Type |
| 3 | state.example.json served | GET `/data/state.example.json` as a static file | HTTP 200 OK |
| 4 | Unknown path returns 404 | GET a path that does not exist on the server | HTTP 404 |
| 5 | Unknown path has CORS header | GET a non-existent path and inspect response headers | `Access-Control-Allow-Origin` header is present even on 404 responses |

---

### CORS & OPTIONS Preflight

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 6 | OPTIONS preflight returns 200 | Send an OPTIONS request to `/api/state` (as a browser would before a cross-origin POST) | HTTP 200 OK |
| 7 | OPTIONS has Allow-Methods header | Send OPTIONS to `/api/state` and check response headers | `Access-Control-Allow-Methods` header is present |
| 8 | GET state has CORS wildcard | GET `/api/state` and inspect the origin header | `Access-Control-Allow-Origin` is exactly `*` |

---

### GET /api/state

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 9 | Returns 200 | GET `/api/state` | HTTP 200 OK |
| 10 | Content-Type is JSON | Inspect the Content-Type header on the response | Header contains `application/json` |
| 11 | Body is valid JSON | Parse the response body | Body is a valid JSON object (not an array or primitive) |
| 12 | Key: completed | Parse the state object | Contains a `completed` key |
| 13 | Key: availableThrough | Parse the state object | Contains an `availableThrough` key |
| 14 | Key: currentTopic | Parse the state object | Contains a `currentTopic` key |
| 15 | Key: highlights | Parse the state object | Contains a `highlights` key |
| 16 | Key: topicNotes | Parse the state object | Contains a `topicNotes` key |
| 17 | Key: qa | Parse the state object | Contains a `qa` key |
| 18 | Key: quizzes | Parse the state object | Contains a `quizzes` key |
| 19 | Key: quizResponses | Parse the state object | Contains a `quizResponses` key |
| 20 | Key: caseResponses | Parse the state object | Contains a `caseResponses` key |

---

### POST /api/state

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 21 | Returns 200 | POST a valid state object to `/api/state` | HTTP 200 OK |
| 22 | Returns ok: true | POST a valid state object and parse the response body | Response body is exactly `{"ok": true}` |
| 23 | Has CORS header | POST to `/api/state` and inspect response headers | `Access-Control-Allow-Origin` header is present |
| 24 | Saved value is retrievable | POST a state with `completed: [1,2,3]` and `availableThrough: 5`, then GET the state | Retrieved state contains the exact values that were saved |
| 25 | Highlights are persisted | POST a state with a highlights object containing a test highlight, then GET the state | Retrieved highlights object matches what was saved |

---

### POST /api/save-quiz-responses

A test quiz with ID 99 is submitted with two questions and two answers. All assertions run against the resulting `responses.md` file and the updated server state.

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 26 | Endpoint returns 200 | POST a quiz submission payload to `/api/save-quiz-responses` | HTTP 200 OK |
| 27 | Endpoint returns ok | Parse the response body | Response body contains `"ok": true` |
| 28 | responses.md created | Check the filesystem after submission | A `responses.md` file exists inside the quiz folder |
| 29 | File contains title | Read the created `responses.md` | The quiz title "Test Quiz" is present in the file |
| 30 | File contains question | Read the created `responses.md` | The question text is present in the file |
| 31 | File contains user answer | Read the created `responses.md` | The user's answer text is present in the file |
| 32 | File contains evaluation placeholder | Read the created `responses.md` | The word "Pending" appears, marking where Claude Code will insert the evaluation |
| 33 | File contains submitted status | Read the created `responses.md` | The word "submitted" appears in the status line |
| 34 | State quizResponses updated | GET `/api/state` after submission | The state's `quizResponses` object contains an entry for quiz ID 99 |
| 35 | Response has CORS header | Inspect the submission response headers | `Access-Control-Allow-Origin` header is present |

---

### POST /api/save-case-responses

A test case study with ID 99 is submitted with two questions (one answered, one blank) and a rubric. All assertions run against the resulting `responses.md` and state.

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 36 | Endpoint returns 200 | POST a case study submission payload to `/api/save-case-responses` | HTTP 200 OK |
| 37 | Endpoint returns ok | Parse the response body | Response body contains `"ok": true` |
| 38 | responses.md created | Check the filesystem after submission | A `responses.md` file exists inside the case study folder |
| 39 | File contains title | Read the created `responses.md` | The case study title "Test Case Study" is present |
| 40 | File contains question | Read the created `responses.md` | The question text is present in the file |
| 41 | File contains user answer | Read the created `responses.md` | The user's answer text is present for the answered question |
| 42 | Empty response handled | Read the created `responses.md` for the unanswered question | The phrase "no response" appears, indicating the blank was handled gracefully |
| 43 | File contains rubric | Read the created `responses.md` | The rubric dimension "Framework Accuracy" is present |
| 44 | File contains evaluation placeholder | Read the created `responses.md` | The word "Pending" appears, marking where Claude Code will insert the evaluation |
| 45 | State caseResponses updated | GET `/api/state` after submission | The state's `caseResponses` object contains an entry for case study ID 99 |
| 46 | Response has CORS header | Inspect the submission response headers | `Access-Control-Allow-Origin` header is present |

---

### Unknown Endpoints

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 47 | Unknown POST returns 404 | POST to `/api/nonexistent` | HTTP 404 |
| 48 | Unknown POST returns JSON error | POST to `/api/nonexistent` and parse the response body | Response body is valid JSON and contains an `error` key |

---

## Suite 2 — Frontend Structure Tests

These tests read `index.html` directly from disk without starting a server. They verify that all JavaScript objects, functions, CSS variables, and HTML elements that the app depends on are present and correctly named.

---

### index.html Existence

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 49 | File exists | Check that `index.html` is present in the project root | File exists on disk |
| 50 | File is non-trivial | Check the file size | File is larger than 10 KB (guards against accidental truncation or an empty placeholder) |

---

### JavaScript Data Objects

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 51 | QUIZ_DATA present | Search for the `QUIZ_DATA` identifier in `index.html` | The string `QUIZ_DATA` appears — confirms pre-authored quiz content is embedded |
| 52 | CASE_DATA present | Search for the `CASE_DATA` identifier in `index.html` | The string `CASE_DATA` appears — confirms pre-authored case study content is embedded |
| 53 | LESSONS present | Search for the `LESSONS` identifier in `index.html` | The string `LESSONS` appears — confirms lesson content object is embedded |

---

### JavaScript Functions

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 54 | mdToHtml | Search for the function declaration | `function mdToHtml(` is present — the Markdown renderer is defined |
| 55 | renderSidebar | Search for the function declaration | `function renderSidebar(` is present — the left-nav builder is defined |
| 56 | loadTopic | Search for the function declaration | `function loadTopic(` is present — the lesson loader is defined |
| 57 | showQuiz | Search for the function declaration | `function showQuiz(` is present — the quiz view renderer is defined |
| 58 | submitQuiz | Search for the function declaration | `function submitQuiz(` is present — the quiz submission handler is defined |
| 59 | loadEvaluation | Search for the function declaration | `function loadEvaluation(` is present — the quiz evaluation loader is defined |
| 60 | autoSaveQuizResponse | Search for the function declaration | `function autoSaveQuizResponse(` is present — the quiz auto-save debouncer is defined |
| 61 | showCaseStudy | Search for the function declaration | `function showCaseStudy(` is present — the case study view renderer is defined |
| 62 | submitCaseStudy | Search for the function declaration | `function submitCaseStudy(` is present — the case study submission handler is defined |
| 63 | loadCaseEvaluation | Search for the function declaration | `function loadCaseEvaluation(` is present — the case study evaluation loader is defined |
| 64 | autoSaveCaseResponse | Search for the function declaration | `function autoSaveCaseResponse(` is present — the case study auto-save debouncer is defined |
| 65 | showFromCase | Search for the function declaration | `function showFromCase(` is present — the back-to-lesson navigation from case study is defined |
| 66 | fetchState | Search for the identifier | `fetchState` appears — the state loader is referenced |
| 67 | pushState | Search for the identifier | `pushState` appears — the state saver is referenced |
| 68 | markDone | Search for the function declaration | `function markDone(` is present — the topic completion handler is defined |
| 69 | init | Search for the function declaration | `function init(` is present — the application bootstrap is defined |

---

### CSS Variables

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 70 | --amber | Search for the CSS variable declaration | `--amber:` appears in the `:root` block — amber colour for case study theme is defined |
| 71 | --amber-bg | Search for the CSS variable declaration | `--amber-bg:` appears — amber background tint is defined |
| 72 | --amber-bdr | Search for the CSS variable declaration | `--amber-bdr:` appears — amber border colour is defined |
| 73 | --blue | Search for the CSS variable declaration | `--blue:` appears — blue colour for quiz theme is defined |
| 74 | --accent | Search for the CSS variable declaration | `--accent:` appears — primary gold accent colour is defined |
| 75 | --ok | Search for the CSS variable declaration | `--ok:` appears — green success colour is defined |

---

### API Endpoint Strings

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 76 | /api/state referenced | Search for the string in JS code | `/api/state` appears — the state sync endpoint is wired up |
| 77 | /api/save-quiz-responses referenced | Search for the string in JS code | `/api/save-quiz-responses` appears — the quiz submission endpoint is wired up |
| 78 | /api/save-case-responses referenced | Search for the string in JS code | `/api/save-case-responses` appears — the case study submission endpoint is wired up |
| 79 | /api/generate referenced | Search for the string in JS code | `/api/generate` appears — the lesson generation endpoint is wired up |

---

### HTML Structure

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 80 | Has DOCTYPE | Search for the HTML5 doctype declaration | `<!DOCTYPE html>` is present at the top of the file |
| 81 | Has Inter font link | Search for the Google Fonts reference | Both `fonts.googleapis.com` and `Inter` appear — the typeface is loaded |
| 82 | Has sidebar element | Search for the sidebar div | `id="sidebar"` is present — the left navigation panel exists |
| 83 | Has main element | Search for the main div | `id="main"` is present — the main content area exists |
| 84 | Has quiz view | Search for the quiz view container | `quiz-view` appears — the quiz reading/answering panel exists |
| 85 | Has case view | Search for the case study view container | `case-view` appears — the case study panel exists |
| 86 | Quiz submit button | Search for the button ID | `btn-submit-quiz` appears — the quiz submission button is present |
| 87 | Case submit button | Search for the button ID | `btn-submit-case` appears — the case study submission button is present |

---

## Suite 3 — Content & File Structure Tests

These tests verify the project's file and folder layout — that all authored content files exist, that the state template is correct, and that the project is set up for clean installation on a new machine.

---

### data/state.example.json

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 88 | File exists | Check that `data/state.example.json` is present | File exists on disk |
| 89 | File is valid JSON | Parse the file | File is valid JSON and the root value is an object |
| 90 | Has completed key | Parse and inspect the state template | Contains a `completed` key |
| 91 | Has availableThrough key | Parse and inspect the state template | Contains an `availableThrough` key |
| 92 | Has quizResponses key | Parse and inspect the state template | Contains a `quizResponses` key |
| 93 | Has caseResponses key | Parse and inspect the state template | Contains a `caseResponses` key |
| 94 | completed is empty list | Parse and inspect the state template | The `completed` key is an empty array `[]` — no topics pre-completed in the template |

---

### Topic Folders

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 95 | topics/ directory exists | Check that the topics directory is present | `topics/` exists on disk |
| 96 | All ten topic folders exist | Check for folders `01-*` through `10-*` inside `topics/` | All ten folders are present; none are missing |
| 97 | All topics have lesson.md | Check for a `lesson.md` file inside each of the ten topic folders | All ten `lesson.md` files exist |
| 98 | All topics have qa.md | Check for a `qa.md` file inside each of the ten topic folders | All ten `qa.md` files exist |
| 99 | lesson.md files are non-empty | Check the file size of each `lesson.md` | No `lesson.md` file has zero bytes — all have content |

---

### docs/ Folder

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 100 | docs/ directory exists | Check that the docs directory is present | `docs/` exists on disk |
| 101 | requirements.md exists | Check for the app requirements document | `docs/requirements.md` exists |
| 102 | master-topic-list.md exists | Check for the full 120-topic curriculum list | `docs/master-topic-list.md` exists |
| 103 | quiz-evaluation-rubric.md exists | Check for the quiz evaluation rubric | `docs/quiz-evaluation-rubric.md` exists |
| 104 | case-study-prompt.md exists | Check for the case study authoring prompt | `docs/case-study-prompt.md` exists |
| 105 | quiz-generation-prompt.md exists | Check for the quiz generation prompt | `docs/quiz-generation-prompt.md` exists |

---

### Quiz & Case Study Folders

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 106 | quizzes/ directory exists | Check that the quizzes directory is present | `quizzes/` exists on disk |
| 107 | quiz-01-topics-1-3 folder exists | Check for the Phase 1 quiz folder | `quizzes/quiz-01-topics-1-3/` exists on disk |
| 108 | case-studies/ directory exists | Check that the case studies directory is present | `case-studies/` exists on disk |
| 109 | cs-01-topics-1-3 folder exists | Check for the Phase 1 case study folder | `case-studies/cs-01-topics-1-3/` exists on disk |

---

### Project Root Files

| # | Name | Description | Expected Result |
|---|------|-------------|-----------------|
| 110 | requirements.txt exists | Check that the Python dependency file is present | `requirements.txt` exists on disk |
| 111 | requirements.txt contains anthropic | Read `requirements.txt` | The word `anthropic` appears — the Anthropic SDK is listed as a dependency |
| 112 | README.md exists | Check that the setup guide is present | `README.md` exists on disk |
| 113 | README.md has setup instructions | Read `README.md` and search for key terms | Both `python3` and `venv` appear — installation instructions are present |
| 114 | .gitignore exists | Check that the Git exclusion file is present | `.gitignore` exists on disk |
| 115 | .gitignore excludes venv/ | Read `.gitignore` | `venv/` appears — the virtual environment folder is excluded from version control |
| 116 | .gitignore excludes state.json | Read `.gitignore` | `state.json` appears — personal progress data is excluded from version control |
| 117 | server.py exists | Check that the server file is present | `server.py` exists on disk |
| 118 | index.html exists | Check that the front-end file is present | `index.html` exists on disk |

---

## Running the tests

```bash
# Full suite (starts test server on port 18080)
cd /Users/sheshank/Documents/Claude/Investment-Course
source venv/bin/activate
python3 tests/run_tests.py

# Skip API tests if you don't want to start a server
python3 tests/run_tests.py --no-api
```

The pre-commit hook runs the full suite automatically before every `git commit`. The machine-generated pass/fail report is written to `tests/test-report.md` and committed alongside your changes.
