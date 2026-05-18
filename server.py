#!/usr/bin/env python3
"""
Value Investing Course — Local Server

Requires: pip install anthropic
Run:      python3 server.py
Open:     http://localhost:8080
"""

import json
import os
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import anthropic

PORT = 8080
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, 'data')
STATE_FILE = os.path.join(DATA_DIR, 'state.json')
os.makedirs(DATA_DIR, exist_ok=True)

# ── All 120 topic titles (for lesson generation context) ────────────────
TOPIC_TITLES = {
    1:"What is intrinsic value (and what it is not)",
    2:"Margin of safety (why it matters more than precision)",
    3:"Time horizon as an edge",
    4:"Circle of competence",
    5:"Second-order thinking",
    6:"Inversion in investing",
    7:"Probabilistic thinking vs certainty",
    8:"Opportunity cost in capital allocation",
    9:"Why most investors underperform",
    10:"Investing vs trading vs speculation",
    11:"How income statements lie",
    12:"Revenue quality vs revenue growth",
    13:"Gross margin vs operating margin",
    14:"Operating leverage (friend and enemy)",
    15:"Balance sheet strength vs cosmetic strength",
    16:"Working capital",
    17:"Cash flow vs reported earnings",
    18:"Free cash flow quality",
    19:"Maintenance capex vs growth capex",
    20:"Accounting red flags investors miss",
    21:"What makes a business 'high quality'",
    22:"Sustainable vs temporary competitive advantage",
    23:"Pricing power (real vs claimed)",
    24:"Brand as a moat",
    25:"Switching costs",
    26:"Network effects",
    27:"Cost leadership and scale advantages",
    28:"Intangible assets (licenses, IP, regulation)",
    29:"Moat erosion signals",
    30:"Why most moats fade",
    31:"Management incentives and behavior",
    32:"Capital allocation skill as the CEO's main job",
    33:"Reinvestment vs dividends vs buybacks",
    34:"When buybacks destroy value",
    35:"When dilution is actually good",
    36:"M&A: value creation vs empire building",
    37:"Reading shareholder letters effectively",
    38:"Founder-led vs professional management",
    39:"Skin in the game",
    40:"Red flags in management communication",
    41:"ROE: when it lies",
    42:"ROIC: the most important metric",
    43:"ROCE vs ROIC",
    44:"Incremental returns on capital",
    45:"Capital intensity",
    46:"Unit economics",
    47:"Scale benefits and diseconomies",
    48:"Cash conversion cycles",
    49:"Reinvestment runway",
    50:"Why growth without returns is useless",
    51:"Price vs value",
    52:"Why valuation is a range, not a point",
    53:"Discount rates (what really matters)",
    54:"DCF: what matters and what doesn't",
    55:"Reverse DCF thinking",
    56:"Relative valuation traps",
    57:"When to ignore valuation",
    58:"Multiple expansion vs business performance",
    59:"Terminal value assumptions",
    60:"Valuation in cyclical businesses",
    61:"Cyclical vs secular businesses",
    62:"Commodity businesses and mean reversion",
    63:"Financial businesses (banks, NBFCs, insurers)",
    64:"Asset-light vs asset-heavy models",
    65:"Platform businesses",
    66:"Subscription models",
    67:"Regulated industries",
    68:"Winner-take-most markets",
    69:"Fragmented industries and consolidation",
    70:"Technology as enabler vs moat",
    71:"Behavioral biases in investing",
    72:"Confirmation bias",
    73:"Loss aversion",
    74:"Overconfidence",
    75:"Recency bias",
    76:"Narrative fallacy",
    77:"FOMO and envy",
    78:"How great investors stay rational",
    79:"Boredom as an edge",
    80:"Emotional discipline during drawdowns",
    81:"Concentration vs diversification",
    82:"Position sizing frameworks",
    83:"Portfolio turnover",
    84:"Cash as an option",
    85:"Rebalancing logic",
    86:"Correlation vs diversification",
    87:"Risk of ruin",
    88:"When to add vs when to cut",
    89:"Portfolio construction mistakes",
    90:"Long-term compounding math",
    91:"How great investors find ideas",
    92:"Screens vs qualitative discovery",
    93:"Under-researched companies",
    94:"Spin-offs and special situations",
    95:"Small-cap inefficiencies",
    96:"Temporary bad news vs permanent impairment",
    97:"Mispriced risk",
    98:"Inflection points",
    99:"When to be contrarian",
    100:"Knowing when NOT to invest",
    101:"What makes a good investment thesis",
    102:"Difference between story and thesis",
    103:"Key variables that matter",
    104:"Disconfirming evidence",
    105:"Variant perception",
    106:"Base rates vs narratives",
    107:"Thesis decay over time",
    108:"Sell discipline",
    109:"Post-mortems",
    110:"Learning from mistakes",
    111:"How Buffett thinks about businesses",
    112:"How Munger thinks about problems",
    113:"Long-term vs short-term advantage",
    114:"Incentives drive outcomes",
    115:"Simplicity on the far side of complexity",
    116:"Building your personal investing philosophy",
    117:"Creating your decision checklist",
    118:"Designing your yearly investing cycle",
    119:"Writing your personal annual letter",
    120:"What lifelong compounding really means",
}

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def load_state():
    defaults = {
        'completed': [],
        'availableThrough': 2,
        'currentTopic': None,
        'highlights': {},
        'topicNotes': {},
        'qa': {},
        'quizzes': {},
        'quizResponses': {},
        'caseResponses': {},
    }
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
        # Ensure any new keys are present even in old state files
        for k, v in defaults.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return defaults

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def prior_context(up_to_id):
    titles = [f"  - Topic {i}: {TOPIC_TITLES[i]}" for i in range(1, up_to_id) if i in TOPIC_TITLES]
    return '\n'.join(titles) if titles else '  (none — this is the first topic)'


# ── HTTP Handler ─────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {fmt % args}")

    def cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path):
        try:
            with open(path, 'rb') as f:
                content = f.read()
            ext = path.rsplit('.', 1)[-1].lower()
            ctype = {'html':'text/html','js':'application/javascript',
                     'css':'text/css','json':'application/json','md':'text/plain'}.get(ext, 'text/plain')
            self.send_response(200)
            self.send_header('Content-Type', ctype + '; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404); self.end_headers()

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors_headers()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html'):
            self.serve_file(os.path.join(BASE, 'index.html'))
        elif path == '/api/state':
            self.send_json(load_state())
        else:
            fp = os.path.join(BASE, path.lstrip('/'))
            if os.path.isfile(fp):
                self.serve_file(fp)
            else:
                self.send_response(404)
                self.cors_headers()
                self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_body()
        except Exception as e:
            self.send_json({'error': f'Bad request body: {e}'}, 400)
            return

        try:
            if path == '/api/state':
                save_state(body)
                self.send_json({'ok': True})
            elif path == '/api/chat':
                self.send_json(self.handle_chat(body))
            elif path == '/api/generate':
                self.send_json(self.handle_generate(body))
            elif path == '/api/save-quiz-responses':
                self.send_json(self.handle_save_quiz_responses(body))
            elif path == '/api/save-case-responses':
                self.send_json(self.handle_save_case_responses(body))
            elif path == '/api/evaluate-quiz':
                self.send_json(self.handle_evaluate_quiz(body))
            else:
                self.send_json({'error': 'Not found'}, 404)
        except Exception as e:
            import traceback
            print(f'\n[ERROR] {path}\n{traceback.format_exc()}')
            self.send_json({'error': str(e)}, 500)

    # ── Chat ──────────────────────────────────────────────────────────────
    def handle_chat(self, body):
        topic_id    = body.get('topicId', 0)
        topic_title = body.get('topicTitle', '')
        question    = body.get('question', '').strip()
        history     = body.get('history', [])
        api_key     = body.get('apiKey', '').strip() or os.environ.get('ANTHROPIC_API_KEY', '')

        if not question:
            return {'error': 'Empty question'}
        if not api_key:
            return {'error': 'NO_API_KEY'}

        client = anthropic.Anthropic(api_key=api_key)
        messages = []
        for h in history[-8:]:
            messages += [
                {'role': 'user',      'content': h['q']},
                {'role': 'assistant', 'content': h['a']},
            ]
        messages.append({'role': 'user', 'content': question})

        resp = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            system=(
                f'You are a world-class value investing tutor. '
                f'The student is currently studying: "{topic_title}". '
                'Answer with the depth and directness of the best investing teacher alive. '
                'Use real examples where helpful. Be concise — 3–5 paragraphs max.'
            ),
            messages=messages,
        )
        answer = resp.content[0].text

        # Persist to state
        state = load_state()
        state.setdefault('qa', {}).setdefault(str(topic_id), []).append({
            'q': question, 'a': answer,
            'ts': datetime.datetime.now().isoformat(),
        })
        save_state(state)

        # Append to qa.md
        self._append_qa_file(topic_id, question, answer)

        return {'answer': answer}

    def _append_qa_file(self, topic_id, question, answer):
        topics_dir = os.path.join(BASE, 'topics')
        if not os.path.isdir(topics_dir):
            return
        for folder in sorted(os.listdir(topics_dir)):
            if folder.startswith(f'{topic_id:02d}-'):
                qa_path = os.path.join(topics_dir, folder, 'qa.md')
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                with open(qa_path, 'a', encoding='utf-8') as f:
                    f.write(f'\n\n---\n\n**Q [{ts}]:** {question}\n\n**A:** {answer}\n')
                break

    # ── Generate quiz + next lessons ─────────────────────────────────────
    def handle_generate(self, body):
        completed_batch = body.get('completedBatch', [])
        next_topics     = body.get('nextTopics', [])
        api_key         = body.get('apiKey', '').strip() or os.environ.get('ANTHROPIC_API_KEY', '')

        if not api_key:
            return {'error': 'NO_API_KEY'}

        client = anthropic.Anthropic(api_key=api_key)

        # 1. Quiz
        quiz_content = self._gen_quiz(client, completed_batch)
        quiz_filename = self._save_quiz(completed_batch, quiz_content)

        # 2. Next lessons
        lessons = []
        for t in next_topics:
            lesson_md = self._gen_lesson(client, t)
            self._save_lesson(t, lesson_md)
            lessons.append({'id': t['id'], 'title': t['title'], 'lesson': lesson_md})

        # 3. Update state
        state = load_state()
        if next_topics:
            state['availableThrough'] = max(t['id'] for t in next_topics)
        batch_key = '-'.join(str(t['id']) for t in completed_batch)
        state.setdefault('quizzes', {})[batch_key] = {
            'content': quiz_content,
            'file': quiz_filename,
            'topics': completed_batch,
            'generatedAt': datetime.datetime.now().isoformat(),
            'userAnswers': {},
            'evaluation': None,
        }
        save_state(state)

        return {
            'quiz': quiz_content,
            'quizFile': quiz_filename,
            'lessons': lessons,
            'newAvailableThrough': state['availableThrough'],
        }

    def _gen_quiz(self, client, topics):
        topic_lines = '\n'.join(f"- Topic {t['id']}: {t['title']}" for t in topics)
        prompt = (
            f"Generate a 10-question quiz covering these value investing topics:\n{topic_lines}\n\n"
            "Requirements:\n"
            "- Open-ended only — no multiple choice\n"
            "- Mix: conceptual (what/why), application (given X, what would an intelligent investor do?), "
            "and judgment questions (evaluate this situation)\n"
            "- At least 2 questions require applying BOTH topics together\n"
            "- Questions should expose gaps in understanding, not just test recall\n"
            "- Number each question (1. 2. etc.)\n"
            "- After all 10 questions, add a line with just: ---\n"
            "- Then MODEL ANSWERS numbered to match, each 3–5 sentences\n"
        )
        resp = client.messages.create(
            model='claude-sonnet-4-6', max_tokens=2500,
            system="You are a rigorous investing examiner writing curriculum-quality assessment content.",
            messages=[{'role':'user','content':prompt}],
        )
        return resp.content[0].text

    def _gen_lesson(self, client, topic):
        context = prior_context(topic['id'])
        prompt = (
            f'Write a lesson on this value investing topic: "{topic["title"]}"\n\n'
            f"This is Topic {topic['id']} in a 120-topic curriculum.\n"
            f"Topics the student has already covered:\n{context}\n\n"
            "Follow this exact structure:\n\n"
            "## A Quick Orientation\n"
            "[2-3 sentences: bridge from prior knowledge to this topic]\n\n"
            "## [Main concept heading]\n"
            "[Core explanation — deep, not surface-level. 2-3 paragraphs.]\n\n"
            "## [Second angle or 'What It Is NOT' heading]\n"
            "[Critical nuance or the flip side. 2-3 paragraphs.]\n\n"
            "## A Real Company to Make This Concrete: [Company Name]\n"
            "[One specific real-world example. 1-2 paragraphs.]\n\n"
            "## The Most Common Mistake\n"
            "[The single most costly error investors make here. 1-2 paragraphs.]\n\n"
            "## Reflection Question\n"
            "REFLECTION:[One penetrating question forcing application, not recall]\n\n"
            "Style: Direct, intellectually honest, 700–900 words. "
            "Use **bold** for key terms. Use *italics* for emphasis. "
            "No hedging, no filler, no trailing next-topic line."
        )
        resp = client.messages.create(
            model='claude-sonnet-4-6', max_tokens=1800,
            system="You are a world-class value investing tutor writing curriculum for a serious student with 10 minutes per day.",
            messages=[{'role':'user','content':prompt}],
        )
        return resp.content[0].text

    def _save_lesson(self, topic, content):
        slug = slugify(topic['title'])
        folder = os.path.join(BASE, 'topics', f"{topic['id']:02d}-{slug}")
        os.makedirs(folder, exist_ok=True)

        lesson_path = os.path.join(folder, 'lesson.md')
        with open(lesson_path, 'w', encoding='utf-8') as f:
            f.write(f"# Topic {topic['id']}: {topic['title']}\n\n")
            f.write("**Generated lesson | ~10 min read**\n\n---\n\n")
            f.write(content)

        qa_path = os.path.join(folder, 'qa.md')
        if not os.path.exists(qa_path):
            with open(qa_path, 'w', encoding='utf-8') as f:
                f.write(f"# Q&A Log — Topic {topic['id']}: {topic['title']}\n\n")
                f.write("> Questions and answers from your study sessions.\n\n---\n\n")
                f.write("*No questions yet.*\n")

    def _save_quiz(self, topics, content):
        ids = '-'.join(str(t['id']) for t in topics)
        filename = f"quiz-topics-{ids}.md"
        filepath = os.path.join(BASE, 'quizzes', filename)
        header = (
            f"# Quiz: Topics {ids}\n\n"
            f"**Covering:** {', '.join(t['title'] for t in topics)}\n"
            f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n---\n\n"
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + content)
        return filename

    # ── Save case study responses ─────────────────────────────────────────
    def handle_save_case_responses(self, body):
        case_id      = body.get('caseId')
        folder       = body.get('folder', f'cs-{case_id:02d}')
        title        = body.get('title', f'Case Study {case_id}')
        subtitle     = body.get('subtitle', '')
        topic_ids    = body.get('topicIds', [])
        topic_titles = body.get('topicTitles', [])
        questions    = body.get('questions', [])
        responses    = body.get('responses', {})
        rubric       = body.get('rubric', {})

        cs_dir = os.path.join(BASE, 'case-studies', folder)
        os.makedirs(cs_dir, exist_ok=True)
        file_path = os.path.join(cs_dir, 'responses.md')

        topics_line = ' | '.join(
            f'Topic {tid}: {ttitle}' for tid, ttitle in zip(topic_ids, topic_titles)
        )
        now = datetime.datetime.now().strftime('%Y-%m-%d')

        # Build rubric reference block
        rubric_lines = []
        if rubric.get('dimensions'):
            rubric_lines += ['', '### Evaluation Rubric (per question, max 13 pts)', '']
            for d in rubric['dimensions']:
                rubric_lines.append(f'- **{d["name"]} ({d["max"]} pts):** {d["desc"]}')
            rubric_lines += ['']
            if rubric.get('grades'):
                rubric_lines.append('**Grade scale:**')
                for g in rubric['grades']:
                    rubric_lines.append(f'- {g["min"]}%+: {g["label"]} — {g["note"]}')

        lines = [
            f'# {title}',
            f'*{subtitle}*',
            '',
            f'**Topics covered:** {topics_line}',
            f'**Submitted:** {now}',
            f'**Status:** submitted',
            '',
            '---',
            '',
            f'> To receive evaluation: type **evaluate case study {case_id}** in Claude Code chat.',
            *rubric_lines,
            '',
        ]

        for i, q in enumerate(questions):
            resp = (responses.get(str(i)) or '').strip()
            lines += [
                f'## Q{i+1}: {q}',
                '',
                '**Your response:**',
                resp if resp else '*(no response)*',
                '',
                '**Evaluation:**',
                f'*Pending — type "evaluate case study {case_id}" in Claude Code.*',
                '',
                '---',
                '',
            ]

        lines += [
            '## Overall Assessment',
            '',
            '*Pending evaluation.*',
        ]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        # Mirror status into state.json
        state = load_state()
        state.setdefault('caseResponses', {})[str(case_id)] = {
            'status': 'submitted',
            'submittedAt': datetime.datetime.now().isoformat(),
        }
        save_state(state)

        return {'ok': True, 'file': file_path}

    # ── Save pre-authored quiz responses ─────────────────────────────────
    def handle_save_quiz_responses(self, body):
        quiz_id     = body.get('quizId')
        folder      = body.get('folder', f'quiz-{quiz_id:02d}')
        title       = body.get('title', f'Quiz {quiz_id}')
        topic_ids   = body.get('topicIds', [])
        topic_titles= body.get('topicTitles', [])
        questions   = body.get('questions', [])
        responses   = body.get('responses', {})

        quiz_dir = os.path.join(BASE, 'quizzes', folder)
        os.makedirs(quiz_dir, exist_ok=True)
        file_path = os.path.join(quiz_dir, 'responses.md')

        topics_line = ' | '.join(
            f'Topic {tid}: {ttitle}'
            for tid, ttitle in zip(topic_ids, topic_titles)
        )
        now = datetime.datetime.now().strftime('%Y-%m-%d')

        lines = [
            f'# {title}',
            '',
            f'**Topics covered:** {topics_line}',
            f'**Submitted:** {now}',
            f'**Status:** submitted',
            '',
            '---',
            '',
            f'> To receive evaluation: type **evaluate quiz {quiz_id}** in Claude Code chat.',
            '',
        ]

        for i, q in enumerate(questions):
            resp = (responses.get(str(i)) or '').strip()
            lines += [
                f'## Q{i+1}: {q}',
                '',
                '**Your response:**',
                resp if resp else '*(no response)*',
                '',
                '**Evaluation:**',
                f'*Pending — type "evaluate quiz {quiz_id}" in Claude Code to receive feedback.*',
                '',
                '---',
                '',
            ]

        lines += [
            '## Overall Assessment',
            '',
            '*Pending evaluation.*',
        ]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        # Mirror status into state.json
        state = load_state()
        state.setdefault('quizResponses', {})[str(quiz_id)] = {
            'status': 'submitted',
            'submittedAt': datetime.datetime.now().isoformat(),
        }
        save_state(state)

        return {'ok': True, 'file': file_path}

    # ── Quiz evaluation ───────────────────────────────────────────────────
    def handle_evaluate_quiz(self, body):
        batch_key   = body.get('batchKey', '')
        questions   = body.get('questions', [])
        answers     = body.get('answers', [])
        model_ans   = body.get('modelAnswers', [])
        api_key     = body.get('apiKey', '').strip() or os.environ.get('ANTHROPIC_API_KEY', '')

        if not api_key:
            return {'error': 'NO_API_KEY'}

        qa_pairs = '\n\n'.join(
            f"Q{i+1}: {questions[i]}\nStudent answer: {answers[i]}\nModel answer: {model_ans[i] if i < len(model_ans) else 'N/A'}"
            for i in range(len(questions))
        )
        prompt = (
            f"Here are a student's quiz answers on value investing:\n\n{qa_pairs}\n\n"
            "Evaluate each answer as if you were the best value investor in the world. "
            "For each question provide:\n"
            "1. What they missed\n"
            "2. How they could have articulated it better\n"
            "3. What a mind-blowing answer would have looked like\n\n"
            "Then an Overall Assessment:\n"
            "- Strongest understanding\n"
            "- Biggest gap to close\n"
            "- What to focus on before the next quiz"
        )
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model='claude-sonnet-4-6', max_tokens=3000,
            system="You are the world's most demanding and insightful value investing examiner. Be honest, specific, and constructive.",
            messages=[{'role':'user','content':prompt}],
        )
        evaluation = resp.content[0].text

        # Persist evaluation
        state = load_state()
        if batch_key in state.get('quizzes', {}):
            state['quizzes'][batch_key]['userAnswers'] = {str(i): answers[i] for i in range(len(answers))}
            state['quizzes'][batch_key]['evaluation'] = evaluation
            state['quizzes'][batch_key]['evaluatedAt'] = datetime.datetime.now().isoformat()
            save_state(state)

            # Append to quiz file
            quiz_file = state['quizzes'][batch_key].get('file')
            if quiz_file:
                fpath = os.path.join(BASE, 'quizzes', quiz_file)
                with open(fpath, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n---\n\n## Your Answers & Evaluation\n\n")
                    for i, (q, a) in enumerate(zip(questions, answers)):
                        f.write(f"**Q{i+1}:** {q}\n**Your answer:** {a}\n\n")
                    f.write(f"## Evaluation\n\n{evaluation}\n")

        return {'evaluation': evaluation}


# ── Entry point ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f"\n📈  Value Investing Course Server")
    print(f"    URL:  http://localhost:{PORT}")
    print(f"    Stop: Ctrl+C\n")
    server = HTTPServer(('localhost', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
