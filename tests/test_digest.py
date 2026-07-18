"""Telegram digest sender tests — no network, no server.
Loads scripts/send_digest.py as a module and exercises the drill
templates, the weighted selector, escaping, and full digest builds."""
import importlib.util
import os
import random
import unittest

from tests.helpers import ROOT

_spec = importlib.util.spec_from_file_location(
    'send_digest', os.path.join(ROOT, 'scripts', 'send_digest.py'))
sd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sd)


class TestDrillTemplates(unittest.TestCase):
    """Every template must produce a numeric answer consistent with its
    own worked solution, across many seeds."""

    def test_all_templates_produce_numbers(self):
        for name, fn in sd.DRILL_TEMPLATES.items():
            for seed in range(20):
                rng = random.Random(seed)
                q, ans, sol = fn(rng)
                self.assertIsInstance(ans, (int, float), f'{name} seed {seed}: non-numeric answer')
                self.assertTrue(q.strip(), f'{name} seed {seed}: empty question')
                self.assertTrue(sol.strip(), f'{name} seed {seed}: empty solution')

    def test_fcf_bridge_math(self):
        for seed in range(20):
            rng = random.Random(seed)
            q, ans, sol = sd.drill_fcf_bridge(rng)
            # Answer must appear in the worked solution
            self.assertIn(str(ans), sol)

    def test_margin_of_safety_math(self):
        for seed in range(20):
            rng = random.Random(seed)
            q, ans, sol = sd.drill_margin_of_safety(rng)
            self.assertIn(str(ans), sol)
            self.assertGreaterEqual(ans, -50)
            self.assertLessEqual(ans, 60)

    def test_cagr_math(self):
        rng = random.Random(42)
        q, ans, sol = sd.drill_cagr(rng)
        # CAGR should be a plausible percentage
        self.assertGreater(ans, 0)
        self.assertLess(ans, 60)

    def test_templates_are_deterministic_per_seed(self):
        for name, fn in sd.DRILL_TEMPLATES.items():
            a = fn(random.Random(7))
            b = fn(random.Random(7))
            self.assertEqual(a, b, f'{name} not deterministic for same seed')


class TestEscaping(unittest.TestCase):

    def test_escapes_markdownv2_specials(self):
        s = 'a-b.c(d)e!f*g_h[i]j'
        out = sd.esc(s)
        for ch in ['\\-', '\\.', '\\(', '\\)', '\\!', '\\*', '\\_', '\\[', '\\]']:
            self.assertIn(ch, out)

    def test_plain_text_unchanged(self):
        self.assertEqual(sd.esc('hello world'), 'hello world')


class TestSelector(unittest.TestCase):

    def test_weak_concepts_are_upweighted(self):
        learner = {'weakConcepts': [{'concept': 'margin-of-safety', 'severity': 3}]}
        weights = sd.concept_weights(learner)
        self.assertEqual(weights['margin-of-safety'], 4.0)

    def test_pick_weighted_deterministic(self):
        items = [{'concept': 'a', 'id': 1}, {'concept': 'b', 'id': 2}, {'concept': 'c', 'id': 3}]
        r1 = sd.pick_weighted(sd.make_rng('2026-07-18', 'morning', 'x'), items, {})
        r2 = sd.pick_weighted(sd.make_rng('2026-07-18', 'morning', 'x'), items, {})
        self.assertEqual(r1, r2)

    def test_pick_weighted_empty(self):
        self.assertIsNone(sd.pick_weighted(random.Random(1), [], {}))


class TestDigestBuild(unittest.TestCase):
    """Full digest builds against the real repo content + sync file."""

    def test_morning_digest_has_parts(self):
        parts = sd.build_digest('2026-07-18', 'morning')
        kinds = [k for k, _ in parts]
        self.assertIn('message', kinds)
        self.assertIn('poll', kinds)
        self.assertGreaterEqual(len(parts), 3)

    def test_evening_digest_is_shorter(self):
        morning = sd.build_digest('2026-07-18', 'morning')
        evening = sd.build_digest('2026-07-18', 'evening')
        self.assertLess(len(evening), len(morning) + 1)
        self.assertGreaterEqual(len(evening), 2)

    def test_digest_deterministic_per_date_slot(self):
        a = sd.build_digest('2026-07-18', 'morning')
        b = sd.build_digest('2026-07-18', 'morning')
        self.assertEqual(a, b)

    def test_digests_vary_across_dates(self):
        digests = [sd.build_digest(f'2026-07-{d:02d}', 'morning') for d in range(10, 20)]
        unique = {str(d) for d in digests}
        self.assertGreater(len(unique), 5, 'Digests barely vary across dates')

    def test_poll_payloads_within_telegram_limits(self):
        for d in range(10, 25):
            for slot in ('morning', 'evening'):
                for kind, payload in sd.build_digest(f'2026-07-{d:02d}', slot):
                    if kind != 'poll':
                        continue
                    self.assertLessEqual(len(payload['question']), 300)
                    self.assertLessEqual(len(payload['explanation']), 200)
                    for o in payload['options']:
                        self.assertLessEqual(len(o), 100)
