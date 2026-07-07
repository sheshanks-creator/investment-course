"""Content schema validation — no server required.
Validates the content/ tree: manifest integrity, per-type schemas,
topic references, and lesson file existence. This is the guardrail
that keeps generated content structurally sound."""
import json
import os
import unittest

from tests.helpers import ROOT

CONTENT = os.path.join(ROOT, 'content')


def _load(relpath):
    with open(os.path.join(CONTENT, relpath), encoding='utf-8') as f:
        return json.load(f)


class TestManifest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest = _load('manifest.json')
        cls.topics = _load('topics.json')
        cls.topic_ids = {t['id'] for t in cls.topics}

    def test_manifest_has_required_keys(self):
        for key in ['lessonTopics', 'quizzes', 'cases', 'coaches', 'numQuizzes']:
            self.assertIn(key, self.manifest, f'manifest missing key: {key}')

    def test_all_referenced_files_exist(self):
        missing = []
        for key in ['quizzes', 'cases', 'coaches', 'numQuizzes']:
            for item in self.manifest[key]:
                if not os.path.exists(os.path.join(CONTENT, item['file'])):
                    missing.append(item['file'])
        self.assertEqual(missing, [], f'Manifest references missing files: {missing}')

    def test_ids_unique_per_type(self):
        for key in ['quizzes', 'cases', 'coaches', 'numQuizzes']:
            ids = [item['id'] for item in self.manifest[key]]
            self.assertEqual(len(ids), len(set(ids)), f'Duplicate ids in manifest.{key}')

    def test_lesson_topics_are_valid_topic_ids(self):
        invalid = [t for t in self.manifest['lessonTopics'] if t not in self.topic_ids]
        self.assertEqual(invalid, [], f'lessonTopics not in topics.json: {invalid}')

    def test_lesson_files_exist_for_all_lesson_topics(self):
        folder_of = {t['id']: t['folder'] for t in self.topics}
        missing = []
        for tid in self.manifest['lessonTopics']:
            path = os.path.join(ROOT, 'topics', folder_of[tid], 'lesson.md')
            if not os.path.exists(path):
                missing.append(tid)
        self.assertEqual(missing, [], f'lessonTopics missing lesson.md on disk: {missing}')


class TestTopicsJSON(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.topics = _load('topics.json')

    def test_has_120_topics(self):
        self.assertEqual(len(self.topics), 120)

    def test_every_topic_has_required_keys(self):
        for t in self.topics:
            self.assertIn('id', t)
            self.assertIn('title', t)
            self.assertIn('folder', t)

    def test_ids_sequential_1_to_120(self):
        ids = sorted(t['id'] for t in self.topics)
        self.assertEqual(ids, list(range(1, 121)))

    def test_folders_match_id_prefix(self):
        bad = [t['id'] for t in self.topics if not t['folder'].startswith(f"{t['id']:02d}-")]
        self.assertEqual(bad, [], f'Folder prefix mismatch for topics: {bad}')


class TestQuizSchemas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest = _load('manifest.json')
        cls.topic_ids = {t['id'] for t in _load('topics.json')}

    def test_quiz_required_keys(self):
        for item in self.manifest['quizzes']:
            quiz = _load(item['file'])
            for key in ['id', 'title', 'topicIds', 'folder', 'questions']:
                self.assertIn(key, quiz, f"{item['file']} missing key: {key}")

    def test_quiz_questions_non_empty(self):
        for item in self.manifest['quizzes']:
            quiz = _load(item['file'])
            self.assertGreater(len(quiz['questions']), 0, f"{item['file']} has no questions")
            for q in quiz['questions']:
                self.assertIsInstance(q, str)
                self.assertGreater(len(q.strip()), 10)

    def test_quiz_topic_ids_valid(self):
        for item in self.manifest['quizzes']:
            quiz = _load(item['file'])
            invalid = [t for t in quiz['topicIds'] if t not in self.topic_ids]
            self.assertEqual(invalid, [], f"{item['file']} invalid topicIds: {invalid}")


class TestCaseSchemas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest = _load('manifest.json')
        cls.topic_ids = {t['id'] for t in _load('topics.json')}

    def test_case_required_keys(self):
        for item in self.manifest['cases']:
            cs = _load(item['file'])
            for key in ['id', 'title', 'subtitle', 'topicIds', 'folder', 'rubric', 'scenario', 'questions']:
                self.assertIn(key, cs, f"{item['file']} missing key: {key}")

    def test_case_rubric_shape(self):
        for item in self.manifest['cases']:
            cs = _load(item['file'])
            rubric = cs['rubric']
            self.assertIn('dimensions', rubric, f"{item['file']} rubric missing dimensions")
            self.assertIn('grades', rubric, f"{item['file']} rubric missing grades")
            for d in rubric['dimensions']:
                for key in ['name', 'max', 'desc']:
                    self.assertIn(key, d, f"{item['file']} rubric dimension missing: {key}")
            for g in rubric['grades']:
                for key in ['min', 'label', 'note']:
                    self.assertIn(key, g, f"{item['file']} rubric grade missing: {key}")

    def test_case_scenario_substantial(self):
        for item in self.manifest['cases']:
            cs = _load(item['file'])
            self.assertGreater(len(cs['scenario']), 1000,
                               f"{item['file']} scenario suspiciously short")

    def test_case_topic_ids_valid(self):
        for item in self.manifest['cases']:
            cs = _load(item['file'])
            invalid = [t for t in cs['topicIds'] if t not in self.topic_ids]
            self.assertEqual(invalid, [], f"{item['file']} invalid topicIds: {invalid}")


class TestCoachSchemas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest = _load('manifest.json')
        cls.topic_ids = {t['id'] for t in _load('topics.json')}

    def test_coach_required_keys(self):
        for item in self.manifest['coaches']:
            coach = _load(item['file'])
            for key in ['id', 'title', 'subtitle', 'topicIds', 'folder', 'intro', 'steps', 'application']:
                self.assertIn(key, coach, f"{item['file']} missing key: {key}")

    def test_coach_steps_complete(self):
        for item in self.manifest['coaches']:
            coach = _load(item['file'])
            self.assertGreater(len(coach['steps']), 0, f"{item['file']} has no steps")
            for i, step in enumerate(coach['steps']):
                for key in ['heading', 'body', 'keyIdea', 'applyElsewhere', 'watchOut']:
                    self.assertIn(key, step, f"{item['file']} step {i+1} missing: {key}")
                    self.assertGreater(len(step[key].strip()), 0,
                                       f"{item['file']} step {i+1} empty: {key}")

    def test_coach_topic_ids_valid(self):
        for item in self.manifest['coaches']:
            coach = _load(item['file'])
            invalid = [t for t in coach['topicIds'] if t not in self.topic_ids]
            self.assertEqual(invalid, [], f"{item['file']} invalid topicIds: {invalid}")


class TestNumQuizSchemas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest = _load('manifest.json')
        cls.topic_ids = {t['id'] for t in _load('topics.json')}

    def test_num_quiz_required_keys(self):
        for item in self.manifest['numQuizzes']:
            nq = _load(item['file'])
            for key in ['id', 'title', 'subtitle', 'topicIds', 'folder', 'scenario', 'questions']:
                self.assertIn(key, nq, f"{item['file']} missing key: {key}")

    def test_num_quiz_answers_are_numbers(self):
        for item in self.manifest['numQuizzes']:
            nq = _load(item['file'])
            for i, q in enumerate(nq['questions']):
                self.assertIsInstance(q['answer'], (int, float),
                                      f"{item['file']} Q{i+1} answer is not a number")

    def test_num_quiz_tolerances_sane(self):
        for item in self.manifest['numQuizzes']:
            nq = _load(item['file'])
            for i, q in enumerate(nq['questions']):
                tol = q.get('tolerance', 0.05)
                self.assertGreater(tol, 0, f"{item['file']} Q{i+1} tolerance must be > 0")
                self.assertLessEqual(tol, 0.5, f"{item['file']} Q{i+1} tolerance must be <= 0.5")

    def test_num_quiz_questions_have_explanations(self):
        for item in self.manifest['numQuizzes']:
            nq = _load(item['file'])
            for i, q in enumerate(nq['questions']):
                self.assertIn('explanation', q, f"{item['file']} Q{i+1} missing explanation")
                self.assertGreater(len(q['explanation'].strip()), 50,
                                   f"{item['file']} Q{i+1} explanation too thin")

    def test_num_quiz_topic_ids_valid(self):
        for item in self.manifest['numQuizzes']:
            nq = _load(item['file'])
            invalid = [t for t in nq['topicIds'] if t not in self.topic_ids]
            self.assertEqual(invalid, [], f"{item['file']} invalid topicIds: {invalid}")
