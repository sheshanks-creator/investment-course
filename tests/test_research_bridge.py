"""Research-bridge tests — classification, index read/unread, path safety,
watchlist export, digest personalisation, and graceful degradation.

Uses only temp fixtures — never the user's real wealth-agents/vault files."""
import importlib.util
import json
import os
import tempfile
import unittest

from tests.helpers import ROOT

_spec = importlib.util.spec_from_file_location(
    'research_lib', os.path.join(ROOT, 'scripts', 'research_lib.py'))
rl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rl)

_dspec = importlib.util.spec_from_file_location(
    'send_digest', os.path.join(ROOT, 'scripts', 'send_digest.py'))
sd = importlib.util.module_from_spec(_dspec)
_dspec.loader.exec_module(sd)


class TestClassification(unittest.TestCase):

    def test_thesis_filename(self):
        self.assertEqual(rl._classify('investment_thesis_POKARNA.md'), ('thesis', False))

    def test_template_excluded(self):
        self.assertEqual(rl._classify('investment_thesis_template.md')[1], True)

    def test_types_from_filenames(self):
        self.assertEqual(rl._classify('pokarna.ns-research-2026-05-29.md')[0], 'research')
        self.assertEqual(rl._classify('pidilite.ns-bull-bear-2026-06-04.md')[0], 'bull-bear')
        self.assertEqual(rl._classify('pokarna.ns-thesis-evaluation-phase1-2026-06-03.md')[0], 'evaluation')

    def test_ticker_extraction(self):
        self.assertEqual(rl._ticker('investment_thesis_POKARNA.md', 'thesis'), 'POKARNA')
        self.assertEqual(rl._ticker('pidilite.ns-bull-bear-2026-06-04.md', 'bull-bear'), 'PIDILITE.NS')
        self.assertEqual(rl._ticker('atlassian-research-2026-06-08.md', 'research'), 'ATLASSIAN')

    def test_company_strips_suffix(self):
        self.assertEqual(rl._company('POKARNA.NS'), 'POKARNA')
        self.assertEqual(rl._company('PIDILITE.BO'), 'PIDILITE')
        self.assertEqual(rl._company('ATLASSIAN'), 'ATLASSIAN')

    def test_market_detection(self):
        self.assertEqual(rl._market('POKARNA.NS'), 'IN')
        self.assertEqual(rl._market('ATLASSIAN'), 'US')


class TestScanAndIndex(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='rbridge_')
        self.roots_dir = os.path.join(self.tmp, 'analyses')
        os.makedirs(self.roots_dir)
        # fixture docs
        with open(os.path.join(self.roots_dir, 'acme.ns-research-2026-01-01.md'), 'w') as f:
            f.write('# Acme\n\nAcme makes widgets and sells them cheaply.\n')
        with open(os.path.join(self.roots_dir, 'investment_thesis_ACME.md'), 'w') as f:
            f.write('# Thesis ACME\n\n## 3. Variant Perception\ntext\n## 11. Pre-Mortem\ntext\n')
        # point research_lib at temp config + index
        self._cfg, self._idx = rl.CONFIG_FILE, rl.INDEX_FILE
        rl.CONFIG_FILE = os.path.join(self.tmp, 'cfg.json')
        rl.INDEX_FILE = os.path.join(self.tmp, 'index.json')
        with open(rl.CONFIG_FILE, 'w') as f:
            json.dump({'roots': [{'path': self.roots_dir, 'kind': 'analyses'}]}, f)

    def tearDown(self):
        rl.CONFIG_FILE, rl.INDEX_FILE = self._cfg, self._idx
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scan_finds_and_classifies(self):
        idx = rl.scan()
        types = sorted(e['type'] for e in idx['entries'])
        self.assertEqual(types, ['research', 'thesis'])

    def test_thesis_section_map(self):
        idx = rl.scan()
        thesis = [e for e in idx['entries'] if e['type'] == 'thesis'][0]
        topics = sorted(s['topicId'] for s in thesis['sectionMap'])
        self.assertIn(7, topics)   # Variant Perception
        self.assertIn(6, topics)   # Pre-Mortem

    def test_sha_change_resets_read(self):
        idx = rl.scan()
        # mark all read
        for e in idx['entries']:
            e['read'] = True
        rl.save_index(idx)
        # modify one file
        p = os.path.join(self.roots_dir, 'acme.ns-research-2026-01-01.md')
        with open(p, 'a') as f:
            f.write('\nNew line changes the hash.\n')
        idx2 = rl.scan(previous=rl.load_index())
        changed = [e for e in idx2['entries'] if e['filename'].startswith('acme')][0]
        unchanged = [e for e in idx2['entries'] if e['type'] == 'thesis'][0]
        self.assertFalse(changed['read'], 'changed file should reset to unread')
        self.assertTrue(unchanged['read'], 'unchanged file should stay read')

    def test_path_safety(self):
        good = os.path.join(self.roots_dir, 'acme.ns-research-2026-01-01.md')
        self.assertTrue(rl.path_is_safe(good))
        self.assertFalse(rl.path_is_safe('/etc/passwd'))
        self.assertFalse(rl.path_is_safe(os.path.join(self.roots_dir, '..', '..', 'secret.md')))


class TestGracefulDegradation(unittest.TestCase):

    def test_no_config_means_no_roots(self):
        cfg = rl.CONFIG_FILE
        rl.CONFIG_FILE = '/nonexistent/path/cfg.json'
        try:
            self.assertEqual(rl.configured_roots(), [])
            self.assertEqual(rl.scan()['entries'], [])
        finally:
            rl.CONFIG_FILE = cfg


class TestWatchlistPersonalisation(unittest.TestCase):

    def _wl(self):
        return [
            {'company': 'POKARNA', 'market': 'IN', 'hasThesis': True,
             'concepts': ['pre-mortem', 'variant-perception', 'margin-of-safety']},
            {'company': 'ATLASSIAN', 'market': 'US', 'hasThesis': False,
             'concepts': ['second-order-thinking', 'circle-of-competence']},
        ]

    def test_matching_concept_personalises(self):
        import random
        txt = sd.personalised_exercise(random.Random(1), 'pre-mortem', self._wl())
        self.assertIsNotNone(txt)
        self.assertIn('POKARNA', txt)
        self.assertIn('research task', txt)

    def test_unmatched_concept_returns_none(self):
        import random
        txt = sd.personalised_exercise(random.Random(1), 'fcf-bridge', self._wl())
        self.assertIsNone(txt)

    def test_empty_watchlist_returns_none(self):
        import random
        self.assertIsNone(sd.personalised_exercise(random.Random(1), 'pre-mortem', []))

    def test_no_sensitive_fields_referenced(self):
        # personalisation must only use company/concepts/hasThesis — never prose
        import random
        txt = sd.personalised_exercise(random.Random(1), 'variant-perception', self._wl())
        self.assertNotIn('conviction', txt.lower())
        self.assertNotIn('sizing', txt.lower())
