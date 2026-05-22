"""API endpoint tests — run against a live test server on port 18080.
Do not run this file directly; use tests/run_tests.py."""
import json
import os
import unittest

import requests

from tests.helpers import ROOT, SERVER_URL

# Unique prefix so test artefacts don't collide with real quiz/case folders
_QUIZ_FOLDER  = 'quiz-TEST-regression'
_CASE_FOLDER  = 'cs-TEST-regression'
_QUIZ_RESP    = os.path.join(ROOT, 'quizzes',      _QUIZ_FOLDER, 'responses.md')
_CASE_RESP    = os.path.join(ROOT, 'case-studies', _CASE_FOLDER, 'responses.md')


def teardown_test_files():
    import shutil
    for path in [
        os.path.join(ROOT, 'quizzes',      _QUIZ_FOLDER),
        os.path.join(ROOT, 'case-studies', _CASE_FOLDER),
    ]:
        shutil.rmtree(path, ignore_errors=True)


# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------
class TestStaticServing(unittest.TestCase):

    def test_root_returns_200(self):
        r = requests.get(f'{SERVER_URL}/', timeout=5)
        self.assertEqual(r.status_code, 200)

    def test_index_html_returns_html(self):
        r = requests.get(f'{SERVER_URL}/index.html', timeout=5)
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/html', r.headers.get('Content-Type', ''))

    def test_state_example_json_served(self):
        r = requests.get(f'{SERVER_URL}/data/state.example.json', timeout=5)
        self.assertEqual(r.status_code, 200)

    def test_unknown_path_returns_404(self):
        r = requests.get(f'{SERVER_URL}/does-not-exist.html', timeout=5)
        self.assertEqual(r.status_code, 404)

    def test_unknown_path_has_cors_header(self):
        r = requests.get(f'{SERVER_URL}/does-not-exist.html', timeout=5)
        self.assertIn('Access-Control-Allow-Origin', r.headers)


# ---------------------------------------------------------------------------
# CORS & OPTIONS preflight
# ---------------------------------------------------------------------------
class TestCORSAndOptions(unittest.TestCase):

    def test_options_preflight_returns_200(self):
        r = requests.options(f'{SERVER_URL}/api/state', timeout=5)
        self.assertEqual(r.status_code, 200)

    def test_options_has_allow_methods(self):
        r = requests.options(f'{SERVER_URL}/api/state', timeout=5)
        self.assertIn('Access-Control-Allow-Methods', r.headers)

    def test_get_state_has_cors_origin_wildcard(self):
        r = requests.get(f'{SERVER_URL}/api/state', timeout=5)
        self.assertEqual(r.headers.get('Access-Control-Allow-Origin'), '*')


# ---------------------------------------------------------------------------
# GET /api/state
# ---------------------------------------------------------------------------
class TestGetState(unittest.TestCase):

    def _state(self):
        return requests.get(f'{SERVER_URL}/api/state', timeout=5)

    def test_returns_200(self):
        self.assertEqual(self._state().status_code, 200)

    def test_content_type_is_json(self):
        ct = self._state().headers.get('Content-Type', '')
        self.assertIn('application/json', ct)

    def test_body_is_valid_json(self):
        data = self._state().json()
        self.assertIsInstance(data, dict)

    def test_required_key_completed(self):
        self.assertIn('completed', self._state().json())

    def test_required_key_available_through(self):
        self.assertIn('availableThrough', self._state().json())

    def test_required_key_current_topic(self):
        self.assertIn('currentTopic', self._state().json())

    def test_required_key_highlights(self):
        self.assertIn('highlights', self._state().json())

    def test_required_key_topic_notes(self):
        self.assertIn('topicNotes', self._state().json())

    def test_required_key_qa(self):
        self.assertIn('qa', self._state().json())

    def test_required_key_quizzes(self):
        self.assertIn('quizzes', self._state().json())

    def test_required_key_quiz_responses(self):
        self.assertIn('quizResponses', self._state().json())

    def test_required_key_case_responses(self):
        self.assertIn('caseResponses', self._state().json())


# ---------------------------------------------------------------------------
# POST /api/state
# ---------------------------------------------------------------------------
class TestPostState(unittest.TestCase):

    def _minimal_state(self, **overrides):
        base = {
            'completed': [], 'availableThrough': 3, 'currentTopic': 1,
            'highlights': {}, 'topicNotes': {}, 'qa': {}, 'quizzes': {},
            'quizResponses': {}, 'caseResponses': {},
        }
        base.update(overrides)
        return base

    def test_returns_200(self):
        r = requests.post(f'{SERVER_URL}/api/state', json=self._minimal_state(), timeout=5)
        self.assertEqual(r.status_code, 200)

    def test_returns_ok_true(self):
        r = requests.post(f'{SERVER_URL}/api/state', json=self._minimal_state(), timeout=5)
        self.assertEqual(r.json(), {'ok': True})

    def test_has_cors_header(self):
        r = requests.post(f'{SERVER_URL}/api/state', json=self._minimal_state(), timeout=5)
        self.assertIn('Access-Control-Allow-Origin', r.headers)

    def test_saved_value_retrievable(self):
        payload = self._minimal_state(completed=[1, 2, 3], availableThrough=5)
        requests.post(f'{SERVER_URL}/api/state', json=payload, timeout=5)
        data = requests.get(f'{SERVER_URL}/api/state', timeout=5).json()
        self.assertEqual(data['completed'], [1, 2, 3])
        self.assertEqual(data['availableThrough'], 5)

    def test_highlights_persisted(self):
        hl = {'1': [{'id': '123', 'text': 'Test highlight', 'color': 'y', 'note': ''}]}
        payload = self._minimal_state(highlights=hl)
        requests.post(f'{SERVER_URL}/api/state', json=payload, timeout=5)
        data = requests.get(f'{SERVER_URL}/api/state', timeout=5).json()
        self.assertEqual(data['highlights'], hl)


# ---------------------------------------------------------------------------
# POST /api/save-quiz-responses
# ---------------------------------------------------------------------------
class TestSaveQuizResponses(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        teardown_test_files()  # clean any leftover from previous run
        payload = {
            'quizId': 99,
            'folder': _QUIZ_FOLDER,
            'title': 'Test Quiz',
            'topicIds': [1, 2, 3],
            'topicTitles': ['Intrinsic value', 'Margin of safety', 'Time horizon'],
            'questions': ['What is intrinsic value?', 'Explain margin of safety.'],
            'responses': {'0': 'My answer to Q1', '1': 'My answer to Q2'},
        }
        cls.response = requests.post(
            f'{SERVER_URL}/api/save-quiz-responses', json=payload, timeout=5
        )

    @classmethod
    def tearDownClass(cls):
        teardown_test_files()

    def test_endpoint_returns_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_endpoint_returns_ok(self):
        self.assertEqual(self.response.json().get('ok'), True)

    def test_responses_md_created(self):
        self.assertTrue(os.path.exists(_QUIZ_RESP), f'responses.md not found at {_QUIZ_RESP}')

    def test_responses_md_contains_title(self):
        content = open(_QUIZ_RESP).read()
        self.assertIn('Test Quiz', content)

    def test_responses_md_contains_question(self):
        content = open(_QUIZ_RESP).read()
        self.assertIn('What is intrinsic value?', content)

    def test_responses_md_contains_user_answer(self):
        content = open(_QUIZ_RESP).read()
        self.assertIn('My answer to Q1', content)

    def test_responses_md_contains_evaluation_placeholder(self):
        content = open(_QUIZ_RESP).read()
        self.assertIn('Pending', content)

    def test_responses_md_contains_submitted_status(self):
        content = open(_QUIZ_RESP).read()
        self.assertIn('submitted', content)

    def test_state_quiz_responses_updated(self):
        data = requests.get(f'{SERVER_URL}/api/state', timeout=5).json()
        self.assertIn('99', data.get('quizResponses', {}))

    def test_has_cors_header(self):
        self.assertIn('Access-Control-Allow-Origin', self.response.headers)


# ---------------------------------------------------------------------------
# POST /api/save-case-responses
# ---------------------------------------------------------------------------
class TestSaveCaseResponses(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        teardown_test_files()
        payload = {
            'caseId': 99,
            'folder': _CASE_FOLDER,
            'title': 'Test Case Study',
            'subtitle': 'Applied Analysis',
            'topicIds': [1, 2, 3],
            'topicTitles': ['Intrinsic value', 'Margin of safety', 'Time horizon'],
            'questions': ['Analyse this company.', 'What is the margin of safety?'],
            'responses': {'0': 'My case answer to Q1', '1': ''},
            'rubric': {
                'dimensions': [
                    {'name': 'Framework Accuracy', 'max': 3, 'desc': 'Correct use of frameworks'},
                ],
                'grades': [
                    {'min': 80, 'label': 'Distinction', 'note': 'Exceptional'},
                ],
            },
        }
        cls.response = requests.post(
            f'{SERVER_URL}/api/save-case-responses', json=payload, timeout=5
        )

    @classmethod
    def tearDownClass(cls):
        teardown_test_files()

    def test_endpoint_returns_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_endpoint_returns_ok(self):
        self.assertEqual(self.response.json().get('ok'), True)

    def test_responses_md_created(self):
        self.assertTrue(os.path.exists(_CASE_RESP), f'responses.md not found at {_CASE_RESP}')

    def test_responses_md_contains_title(self):
        content = open(_CASE_RESP).read()
        self.assertIn('Test Case Study', content)

    def test_responses_md_contains_question(self):
        content = open(_CASE_RESP).read()
        self.assertIn('Analyse this company.', content)

    def test_responses_md_contains_user_answer(self):
        content = open(_CASE_RESP).read()
        self.assertIn('My case answer to Q1', content)

    def test_responses_md_no_response_handled(self):
        content = open(_CASE_RESP).read()
        self.assertIn('no response', content)

    def test_responses_md_contains_rubric(self):
        content = open(_CASE_RESP).read()
        self.assertIn('Framework Accuracy', content)

    def test_responses_md_contains_evaluation_placeholder(self):
        content = open(_CASE_RESP).read()
        self.assertIn('Pending', content)

    def test_state_case_responses_updated(self):
        data = requests.get(f'{SERVER_URL}/api/state', timeout=5).json()
        self.assertIn('99', data.get('caseResponses', {}))

    def test_has_cors_header(self):
        self.assertIn('Access-Control-Allow-Origin', self.response.headers)


# ---------------------------------------------------------------------------
# Unknown endpoints
# ---------------------------------------------------------------------------
class TestUnknownEndpoints(unittest.TestCase):

    def test_unknown_post_returns_404(self):
        r = requests.post(f'{SERVER_URL}/api/nonexistent', json={}, timeout=5)
        self.assertEqual(r.status_code, 404)

    def test_unknown_post_returns_json_error(self):
        r = requests.post(f'{SERVER_URL}/api/nonexistent', json={}, timeout=5)
        body = r.json()
        self.assertIn('error', body)
