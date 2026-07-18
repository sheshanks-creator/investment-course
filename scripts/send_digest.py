#!/usr/bin/env python3
"""
Telegram micro-learning digest sender.

Composes an adaptive micro-digest from the content/micro/ bank,
sync/learner.json (weak concepts + highlights), and parameterised
numeric drill templates — then sends it via the Telegram Bot API.

Stdlib only. Deterministic per (date, slot) so the GitHub Action needs
no persisted state: the same day always produces the same digest, and
consecutive days rotate through the bank with weakness weighting.

Usage:
  python3 scripts/send_digest.py --slot morning [--dry-run] [--date 2026-07-18]

Env (required unless --dry-run):
  TELEGRAM_BOT_TOKEN   from @BotFather
  TELEGRAM_CHAT_ID     your chat id with the bot
"""
import argparse
import datetime
import json
import os
import random
import sys
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
SYNC_FILE = os.path.join(ROOT, 'sync', 'learner.json')


# ── Loading ──────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_bank():
    """All micro items for covered topics, flattened, with topicId attached."""
    manifest = load_json(os.path.join(CONTENT, 'manifest.json'))
    learner = load_learner()
    covered = set(range(1, learner['availableThrough'] + 1))
    items = []
    for entry in manifest.get('micro', []):
        if entry['topicId'] not in covered:
            continue
        data = load_json(os.path.join(CONTENT, entry['file']))
        for i, item in enumerate(data['items']):
            item = dict(item)
            item['topicId'] = data['topicId']
            item['uid'] = f"{data['topicId']}-{i}"
            items.append(item)
    return items


def load_learner():
    try:
        return load_json(SYNC_FILE)
    except FileNotFoundError:
        return {'availableThrough': 3, 'weakConcepts': [], 'highlights': []}


def topic_titles():
    return {t['id']: t['title'] for t in load_json(os.path.join(CONTENT, 'topics.json'))}


# ── Weakness-weighted deterministic selection ────────────────────────────

def concept_weights(learner):
    """weight = 1.0 base; weak concepts get 1 + severity (so sev 3 → 4x)."""
    w = {}
    for wc in learner.get('weakConcepts', []):
        w[wc['concept']] = 1.0 + wc.get('severity', 1)
    return w


def pick_weighted(rng, items, weights):
    if not items:
        return None
    ws = [weights.get(it.get('concept', ''), 1.0) for it in items]
    return rng.choices(items, weights=ws, k=1)[0]


def make_rng(date_str, slot, salt=''):
    seed = f'{date_str}|{slot}|{salt}'
    return random.Random(seed)


# ── Numeric drill templates (parameterised, infinite variants) ───────────

def drill_fcf_bridge(rng):
    pat = rng.randrange(400, 2500, 20)
    da = rng.randrange(40, 300, 10)
    capex = rng.randrange(50, 400, 10)
    dwc = rng.randrange(-150, 200, 10)
    ans = pat + da - capex - dwc
    wc_phrase = f'rose by ₹{dwc} cr' if dwc >= 0 else f'fell by ₹{-dwc} cr'
    q = (f'A company reports PAT ₹{pat} cr, D&A ₹{da} cr, capex ₹{capex} cr, '
         f'and working capital {wc_phrase}. What is its Free Cash Flow (₹ cr)?')
    sol = (f'FCF = PAT + D&A − Capex − ΔWC = {pat} + {da} − {capex} − ({dwc}) '
           f'= ₹{ans} cr')
    return q, ans, sol


def drill_roe(rng):
    equity = rng.randrange(1000, 6000, 100)
    roe_pct = rng.randrange(12, 45)
    pat = round(equity * roe_pct / 100)
    q = (f'PAT is ₹{pat} cr on shareholders’ equity of ₹{equity} cr. '
         f'What is the ROE (%)?')
    sol = f'ROE = PAT / Equity = {pat} / {equity} = {roe_pct}%'
    return q, roe_pct, sol


def drill_sustainable_growth(rng):
    roe = rng.randrange(15, 45)
    payout = rng.choice([20, 30, 40, 50, 60, 70, 80])
    retention = 100 - payout
    ans = round(roe * retention / 100, 1)
    q = (f'A firm earns {roe}% ROE and pays out {payout}% of profits as dividends. '
         f'What growth can it sustain without external capital (%)?')
    sol = (f'Sustainable growth = ROE × retention = {roe}% × {retention}% '
           f'= {ans}%')
    return q, ans, sol


def drill_present_value(rng):
    fv = rng.choice([500, 1000, 1500, 2000])
    r = rng.choice([8, 9, 10, 11, 12])
    n = rng.choice([3, 5, 7, 10])
    ans = round(fv / ((1 + r / 100) ** n))
    q = (f'₹{fv} cr arrives {n} years from now. At a {r}% discount rate, '
         f'what is its present value (₹ cr)?')
    sol = f'PV = {fv} / (1.{r:02d})^{n} = {fv} / {round((1+r/100)**n, 3)} ≈ ₹{ans} cr'
    return q, ans, sol


def drill_terminal_value(rng):
    fcf = rng.randrange(1000, 6000, 500)
    r = rng.choice([9, 10, 11, 12])
    g = rng.choice([3, 4, 5])
    ans = round(fcf / ((r - g) / 100))
    q = (f'Terminal-year FCF is ₹{fcf} cr, discount rate {r}%, perpetual growth {g}%. '
         f'Terminal value via Gordon growth (₹ cr)?')
    sol = f'TV = FCF / (r − g) = {fcf} / ({r}% − {g}%) = {fcf} / {(r-g)/100} = ₹{ans} cr'
    return q, ans, sol


def drill_margin_of_safety(rng):
    iv = rng.randrange(400, 1200, 50)
    mos_pct = rng.choice([-30, -20, -10, 15, 20, 25, 30, 40])
    price = round(iv * (1 - mos_pct / 100))
    q = (f'You estimate intrinsic value at ₹{iv}/share; the stock trades at ₹{price}. '
         f'Margin of safety (%)? (negative if price exceeds value)')
    sol = f'MoS = (IV − P) / IV = ({iv} − {price}) / {iv} = {mos_pct}%'
    return q, mos_pct, sol


def drill_cagr(rng):
    start = rng.choice([100, 150, 200, 250])
    mult = rng.choice([2, 2.5, 3, 4, 5])
    n = rng.choice([5, 8, 10, 12])
    end = round(start * mult)
    ans = round(((end / start) ** (1 / n) - 1) * 100, 1)
    q = f'An investment grows from ₹{start} to ₹{end} in {n} years. CAGR (%)?'
    sol = f'CAGR = ({end}/{start})^(1/{n}) − 1 = {mult}^{round(1/n, 3)} − 1 ≈ {ans}%'
    return q, ans, sol


def drill_return_decomposition(rng):
    growth = rng.choice([8, 10, 12, 15])
    n = 10
    entry_pe = rng.choice([40, 45, 50, 60])
    exit_pe = rng.choice([25, 30, 35])
    earnings_mult = (1 + growth / 100) ** n
    ans = round(earnings_mult * exit_pe / entry_pe, 2)
    q = (f'You buy at {entry_pe}× earnings. Earnings grow {growth}%/yr for {n} years; '
         f'the exit multiple is {exit_pe}×. Total return multiple on your money?')
    sol = (f'Return = earnings growth × multiple change = (1.{growth:02d})^{n} × '
           f'({exit_pe}/{entry_pe}) = {round(earnings_mult, 2)} × '
           f'{round(exit_pe/entry_pe, 3)} ≈ {ans}×')
    return q, ans, sol


DRILL_TEMPLATES = {
    'fcf-bridge': drill_fcf_bridge,
    'roe': drill_roe,
    'sustainable-growth': drill_sustainable_growth,
    'present-value': drill_present_value,
    'terminal-value': drill_terminal_value,
    'margin-of-safety': drill_margin_of_safety,
    'cagr': drill_cagr,
    'return-decomposition': drill_return_decomposition,
}

# Which drill concepts map to which weak-concept ids (for weighting)
DRILL_CONCEPT_ALIASES = {
    'fcf-bridge': 'fcf-bridge',
    'roe': 'dcf-mechanics',
    'sustainable-growth': 'dcf-mechanics',
    'present-value': 'dcf-mechanics',
    'terminal-value': 'dcf-mechanics',
    'margin-of-safety': 'margin-of-safety',
    'cagr': 'compounding-math',
    'return-decomposition': 'return-decomposition',
}


def pick_drill(rng, learner):
    weights = concept_weights(learner)
    names = sorted(DRILL_TEMPLATES.keys())
    ws = [weights.get(DRILL_CONCEPT_ALIASES[n], 1.0) for n in names]
    name = rng.choices(names, weights=ws, k=1)[0]
    q, ans, sol = DRILL_TEMPLATES[name](rng)
    return name, q, ans, sol


# ── Telegram formatting & API ────────────────────────────────────────────

MDV2_SPECIALS = r'_*[]()~`>#+-=|{}.!'


def esc(text):
    """Escape a plain-text string for Telegram MarkdownV2."""
    out = []
    for ch in str(text):
        if ch in MDV2_SPECIALS:
            out.append('\\' + ch)
        else:
            out.append(ch)
    return ''.join(out)


def tg_call(token, method, payload, dry_run=False):
    if dry_run:
        print(f'--- [dry-run] {method} ---')
        if 'text' in payload:
            print(payload['text'])
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        print()
        return {'ok': True, 'dry_run': True}
    url = f'https://api.telegram.org/bot{token}/{method}'
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    if not result.get('ok'):
        raise RuntimeError(f'Telegram {method} failed: {result}')
    return result


def send_message(token, chat_id, text, dry_run=False):
    return tg_call(token, 'sendMessage', {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2',
    }, dry_run)


def send_quiz_poll(token, chat_id, question, options, correct_index, explanation, dry_run=False):
    return tg_call(token, 'sendPoll', {
        'chat_id': chat_id,
        'question': question[:300],
        'options': json.dumps(options[:10], ensure_ascii=False),
        'type': 'quiz',
        'correct_option_id': correct_index,
        'explanation': explanation[:200],
        'is_anonymous': 'true',
    }, dry_run)


# ── Digest composition ───────────────────────────────────────────────────

def build_digest(date_str, slot):
    """Return a list of ('message', text) / ('poll', dict) parts."""
    learner = load_learner()
    bank = load_bank()
    titles = topic_titles()
    weights = concept_weights(learner)
    parts = []

    cards = [it for it in bank if it['type'] == 'card']
    mcqs = [it for it in bank if it['type'] == 'mcq']

    slot_label = 'Morning' if slot == 'morning' else 'Evening'
    nice_date = datetime.date.fromisoformat(date_str).strftime('%a %d %b')
    header = f'*{esc("📈 " + slot_label + " micro-digest")}* — {esc(nice_date)}'

    if slot == 'morning':
        # 1. Weakness-targeted concept card
        rng = make_rng(date_str, slot, 'card')
        card = pick_weighted(rng, cards, weights)
        if card:
            topic = titles.get(card['topicId'], '')
            parts.append(('message',
                f'{header}\n\n'
                f'*{esc("💡 Concept · Topic " + str(card["topicId"]) + ": " + topic)}*\n\n'
                f'{esc(card["text"])}'))

        # 2. MCQ as native quiz poll
        rng = make_rng(date_str, slot, 'mcq')
        mcq = pick_weighted(rng, mcqs, weights)
        if mcq:
            parts.append(('poll', {
                'question': f'🧠 {mcq["text"]}',
                'options': mcq['options'],
                'correct_index': mcq['correctIndex'],
                'explanation': mcq.get('explanation', ''),
            }))

        # 3. Numeric drill (spoiler answer)
        rng = make_rng(date_str, slot, 'drill')
        name, q, ans, sol = pick_drill(rng, learner)
        parts.append(('message',
            f'*{esc("🧮 Numeric drill — " + name)}*\n\n'
            f'{esc(q)}\n\n'
            f'{esc("Tap to reveal the answer:")}\n'
            f'||{esc(sol)}||'))

        # 4. Resurfaced highlight
        highlights = learner.get('highlights', [])
        if highlights:
            rng = make_rng(date_str, slot, 'highlight')
            hl = rng.choice(highlights)
            topic = titles.get(hl['topicId'], '')
            note = f'\n\n{esc("Your note: " + hl["note"])}' if hl.get('note') else ''
            parts.append(('message',
                f'*{esc("🔖 You highlighted this — Topic " + str(hl["topicId"]) + ": " + topic)}*\n\n'
                f'_{esc(hl["text"])}_{note}\n\n'
                f'{esc("Still true? Still important? 30 seconds of re-reading beats an hour of forgetting.")}'))
    else:
        # Evening: shorter — MCQ poll + drill (different salts → different picks)
        parts.append(('message', header))

        rng = make_rng(date_str, slot, 'mcq')
        mcq = pick_weighted(rng, mcqs, weights)
        if mcq:
            parts.append(('poll', {
                'question': f'🧠 {mcq["text"]}',
                'options': mcq['options'],
                'correct_index': mcq['correctIndex'],
                'explanation': mcq.get('explanation', ''),
            }))

        rng = make_rng(date_str, slot, 'drill')
        name, q, ans, sol = pick_drill(rng, learner)
        parts.append(('message',
            f'*{esc("🧮 Numeric drill — " + name)}*\n\n'
            f'{esc(q)}\n\n'
            f'{esc("Tap to reveal the answer:")}\n'
            f'||{esc(sol)}||'))

    return parts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--slot', choices=['morning', 'evening'], required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--date', default=None, help='Override date (YYYY-MM-DD) for testing')
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()

    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not args.dry_run and (not token or not chat_id):
        print('ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (or use --dry-run)')
        return 1

    parts = build_digest(date_str, args.slot)
    if not parts:
        print('No content available for digest — nothing sent.')
        return 0

    for kind, payload in parts:
        if kind == 'message':
            send_message(token, chat_id, payload, args.dry_run)
        elif kind == 'poll':
            send_quiz_poll(token, chat_id, payload['question'], payload['options'],
                           payload['correct_index'], payload['explanation'], args.dry_run)

    print(f'{"[dry-run] " if args.dry_run else ""}Digest sent: {args.slot} {date_str}, {len(parts)} parts')
    return 0


if __name__ == '__main__':
    sys.exit(main())
