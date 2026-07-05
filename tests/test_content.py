"""Content and file structure tests — no server required.
Verifies that all expected folders, lesson files, docs, and config files exist."""
import json
import os
import unittest

from tests.helpers import ROOT

TOPICS_DIR       = os.path.join(ROOT, 'topics')
DOCS_DIR         = os.path.join(ROOT, 'docs')
QUIZZES_DIR      = os.path.join(ROOT, 'quizzes')
CASE_STUDIES_DIR = os.path.join(ROOT, 'case-studies')
DATA_DIR         = os.path.join(ROOT, 'data')

# Topics expected in the current phase (1-10 are authored)
EXPECTED_TOPIC_IDS = list(range(1, 11))

STATE_REQUIRED_KEYS = [
    'completed', 'availableThrough', 'currentTopic',
    'highlights', 'topicNotes', 'qa', 'quizzes',
    'quizResponses', 'caseResponses',
]


# ---------------------------------------------------------------------------
# state.example.json
# ---------------------------------------------------------------------------
class TestStateExampleJSON(unittest.TestCase):

    def _path(self):
        return os.path.join(DATA_DIR, 'state.example.json')

    def test_file_exists(self):
        self.assertTrue(os.path.exists(self._path()), 'data/state.example.json not found')

    def test_file_is_valid_json(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_has_completed_key(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIn('completed', data)

    def test_has_available_through_key(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIn('availableThrough', data)

    def test_has_quiz_responses_key(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIn('quizResponses', data)

    def test_has_case_responses_key(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIn('caseResponses', data)

    def test_has_coach_visits_key(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIn('coachVisits', data)

    def test_has_num_quiz_responses_key(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertIn('numQuizResponses', data)

    def test_completed_is_empty_list(self):
        with open(self._path()) as f:
            data = json.load(f)
        self.assertEqual(data['completed'], [])


# ---------------------------------------------------------------------------
# Topic folders
# ---------------------------------------------------------------------------
class TestTopicFolders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.folders = os.listdir(TOPICS_DIR) if os.path.isdir(TOPICS_DIR) else []

    def _folder_for(self, topic_id):
        prefix = f'{topic_id:02d}-'
        matches = [f for f in self.folders if f.startswith(prefix)]
        return matches[0] if matches else None

    def test_topics_dir_exists(self):
        self.assertTrue(os.path.isdir(TOPICS_DIR), 'topics/ directory not found')

    def test_all_ten_topic_folders_exist(self):
        missing = []
        for tid in EXPECTED_TOPIC_IDS:
            if not self._folder_for(tid):
                missing.append(tid)
        self.assertEqual(missing, [], f'Missing topic folders: {missing}')

    def test_all_topics_have_lesson_md(self):
        missing = []
        for tid in EXPECTED_TOPIC_IDS:
            folder = self._folder_for(tid)
            if folder:
                path = os.path.join(TOPICS_DIR, folder, 'lesson.md')
                if not os.path.exists(path):
                    missing.append(tid)
        self.assertEqual(missing, [], f'Topics missing lesson.md: {missing}')

    def test_all_topics_have_qa_md(self):
        missing = []
        for tid in EXPECTED_TOPIC_IDS:
            folder = self._folder_for(tid)
            if folder:
                path = os.path.join(TOPICS_DIR, folder, 'qa.md')
                if not os.path.exists(path):
                    missing.append(tid)
        self.assertEqual(missing, [], f'Topics missing qa.md: {missing}')

    def test_lesson_md_files_are_non_empty(self):
        empty = []
        for tid in EXPECTED_TOPIC_IDS:
            folder = self._folder_for(tid)
            if folder:
                path = os.path.join(TOPICS_DIR, folder, 'lesson.md')
                if os.path.exists(path) and os.path.getsize(path) == 0:
                    empty.append(tid)
        self.assertEqual(empty, [], f'Topics with empty lesson.md: {empty}')


# ---------------------------------------------------------------------------
# Docs folder
# ---------------------------------------------------------------------------
class TestDocsFolder(unittest.TestCase):

    def test_docs_dir_exists(self):
        self.assertTrue(os.path.isdir(DOCS_DIR), 'docs/ directory not found')

    def test_requirements_md_exists(self):
        self.assertTrue(os.path.exists(os.path.join(DOCS_DIR, 'requirements.md')))

    def test_master_topic_list_exists(self):
        self.assertTrue(os.path.exists(os.path.join(DOCS_DIR, 'master-topic-list.md')))

    def test_quiz_evaluation_rubric_exists(self):
        self.assertTrue(os.path.exists(os.path.join(DOCS_DIR, 'quiz-evaluation-rubric.md')))

    def test_case_study_prompt_exists(self):
        self.assertTrue(os.path.exists(os.path.join(DOCS_DIR, 'case-study-prompt.md')))

    def test_quiz_generation_prompt_exists(self):
        self.assertTrue(os.path.exists(os.path.join(DOCS_DIR, 'quiz-generation-prompt.md')))


# ---------------------------------------------------------------------------
# Quiz and case study folders
# ---------------------------------------------------------------------------
class TestQuizAndCaseFolders(unittest.TestCase):

    def test_quizzes_dir_exists(self):
        self.assertTrue(os.path.isdir(QUIZZES_DIR), 'quizzes/ directory not found')

    def test_quiz_01_folder_exists(self):
        self.assertTrue(
            os.path.isdir(os.path.join(QUIZZES_DIR, 'quiz-01-topics-1-3')),
            'quizzes/quiz-01-topics-1-3/ not found',
        )

    def test_case_studies_dir_exists(self):
        self.assertTrue(os.path.isdir(CASE_STUDIES_DIR), 'case-studies/ directory not found')

    def test_cs_01_folder_exists(self):
        self.assertTrue(
            os.path.isdir(os.path.join(CASE_STUDIES_DIR, 'cs-01-topics-1-3')),
            'case-studies/cs-01-topics-1-3/ not found',
        )

    def test_coach_cases_dir_exists(self):
        self.assertTrue(
            os.path.isdir(os.path.join(ROOT, 'coach-cases')),
            'coach-cases/ directory not found',
        )

    def test_coach_01_folder_exists(self):
        self.assertTrue(
            os.path.isdir(os.path.join(ROOT, 'coach-cases', 'coach-01-topics-1-3')),
            'coach-cases/coach-01-topics-1-3/ not found',
        )


# ---------------------------------------------------------------------------
# Project root files
# ---------------------------------------------------------------------------
class TestProjectRootFiles(unittest.TestCase):

    def test_requirements_txt_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'requirements.txt')))

    def test_requirements_txt_contains_anthropic(self):
        with open(os.path.join(ROOT, 'requirements.txt')) as f:
            content = f.read()
        self.assertIn('anthropic', content)

    def test_readme_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'README.md')))

    def test_readme_has_setup_instructions(self):
        with open(os.path.join(ROOT, 'README.md')) as f:
            content = f.read()
        self.assertIn('python3', content.lower())
        self.assertIn('venv', content)

    def test_gitignore_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, '.gitignore')))

    def test_gitignore_excludes_venv(self):
        with open(os.path.join(ROOT, '.gitignore')) as f:
            content = f.read()
        self.assertIn('venv/', content)

    def test_gitignore_excludes_state_json(self):
        with open(os.path.join(ROOT, '.gitignore')) as f:
            content = f.read()
        self.assertIn('state.json', content)

    def test_server_py_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'server.py')))

    def test_index_html_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'index.html')))
