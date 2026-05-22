"""Frontend structure tests — static analysis of index.html.
No server required. Checks that required JS objects, functions, and CSS
variables exist and API endpoint strings are wired correctly."""
import os
import unittest

from tests.helpers import ROOT

INDEX_HTML = os.path.join(ROOT, 'index.html')


class TestIndexHTMLExists(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(os.path.exists(INDEX_HTML), 'index.html not found')

    def test_file_is_non_trivial(self):
        size = os.path.getsize(INDEX_HTML)
        self.assertGreater(size, 10_000, f'index.html is suspiciously small ({size} bytes)')


class TestJSDataObjects(unittest.TestCase):
    """Pre-authored quiz and case content must be embedded."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, encoding='utf-8') as f:
            cls.src = f.read()

    def test_QUIZ_DATA_present(self):
        self.assertIn('QUIZ_DATA', self.src)

    def test_CASE_DATA_present(self):
        self.assertIn('CASE_DATA', self.src)

    def test_LESSONS_present(self):
        self.assertIn('LESSONS', self.src)


class TestJSFunctions(unittest.TestCase):
    """Key functions must be declared in index.html."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, encoding='utf-8') as f:
            cls.src = f.read()

    def _has(self, name):
        return f'function {name}(' in self.src or f'function {name} (' in self.src

    def test_mdToHtml(self):
        self.assertTrue(self._has('mdToHtml'), 'mdToHtml not found')

    def test_renderSidebar(self):
        self.assertTrue(self._has('renderSidebar'), 'renderSidebar not found')

    def test_loadTopic(self):
        self.assertTrue(self._has('loadTopic'), 'loadTopic not found')

    def test_showQuiz(self):
        self.assertTrue(self._has('showQuiz'), 'showQuiz not found')

    def test_submitQuiz(self):
        self.assertTrue(self._has('submitQuiz'), 'submitQuiz not found')

    def test_loadEvaluation(self):
        self.assertTrue(self._has('loadEvaluation'), 'loadEvaluation not found')

    def test_autoSaveQuizResponse(self):
        self.assertTrue(self._has('autoSaveQuizResponse'), 'autoSaveQuizResponse not found')

    def test_showCaseStudy(self):
        self.assertTrue(self._has('showCaseStudy'), 'showCaseStudy not found')

    def test_submitCaseStudy(self):
        self.assertTrue(self._has('submitCaseStudy'), 'submitCaseStudy not found')

    def test_loadCaseEvaluation(self):
        self.assertTrue(self._has('loadCaseEvaluation'), 'loadCaseEvaluation not found')

    def test_autoSaveCaseResponse(self):
        self.assertTrue(self._has('autoSaveCaseResponse'), 'autoSaveCaseResponse not found')

    def test_showFromCase(self):
        self.assertTrue(self._has('showFromCase'), 'showFromCase not found')

    def test_fetchState(self):
        self.assertIn('fetchState', self.src)

    def test_pushState(self):
        self.assertIn('pushState', self.src)

    def test_markDone(self):
        self.assertTrue(self._has('markDone'), 'markDone not found')

    def test_init(self):
        self.assertTrue(self._has('init'), 'init not found')


class TestCSSVariables(unittest.TestCase):
    """Theme CSS variables must be declared."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, encoding='utf-8') as f:
            cls.src = f.read()

    def test_amber_variable(self):
        self.assertIn('--amber:', self.src)

    def test_amber_bg_variable(self):
        self.assertIn('--amber-bg:', self.src)

    def test_amber_bdr_variable(self):
        self.assertIn('--amber-bdr:', self.src)

    def test_blue_variable(self):
        self.assertIn('--blue:', self.src)

    def test_accent_variable(self):
        self.assertIn('--accent:', self.src)

    def test_ok_variable(self):
        self.assertIn('--ok:', self.src)


class TestAPIEndpointStrings(unittest.TestCase):
    """Correct API paths must be referenced in JS."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, encoding='utf-8') as f:
            cls.src = f.read()

    def test_api_state_get_referenced(self):
        self.assertIn('/api/state', self.src)

    def test_api_save_quiz_responses_referenced(self):
        self.assertIn('/api/save-quiz-responses', self.src)

    def test_api_save_case_responses_referenced(self):
        self.assertIn('/api/save-case-responses', self.src)

    def test_api_generate_referenced(self):
        self.assertIn('/api/generate', self.src)


class TestHTMLStructure(unittest.TestCase):
    """Basic HTML structure checks."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, encoding='utf-8') as f:
            cls.src = f.read()

    def test_has_doctype(self):
        self.assertIn('<!DOCTYPE html>', self.src)

    def test_has_inter_font_link(self):
        self.assertIn('fonts.googleapis.com', self.src)
        self.assertIn('Inter', self.src)

    def test_has_sidebar_element(self):
        self.assertIn('id="sidebar"', self.src)

    def test_has_main_element(self):
        self.assertIn('id="main"', self.src)

    def test_has_quiz_view(self):
        self.assertIn('quiz-view', self.src)

    def test_has_case_view(self):
        self.assertIn('case-view', self.src)

    def test_quiz_submit_button(self):
        self.assertIn('btn-submit-quiz', self.src)

    def test_case_submit_button(self):
        self.assertIn('btn-submit-case', self.src)
