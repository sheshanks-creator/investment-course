#!/usr/bin/env python3
"""
Value Investing Course — Regression Test Runner
================================================
Usage:
  python3 tests/run_tests.py          # run all suites
  python3 tests/run_tests.py --no-api # skip API tests (no server started)

Exits 0 if all tests pass, 1 if any fail.
Writes a test report to tests/test-report.md.
"""
import sys
import os
import argparse
import datetime
import unittest
import traceback

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ── Custom result collector ───────────────────────────────────────────────

class CollectingResult(unittest.TestResult):
    """Captures per-test outcomes for report generation."""

    def __init__(self):
        super().__init__()
        self.records = []  # (suite_name, test_desc, status, detail)

    def _record(self, test, status, detail=''):
        suite = type(test).__name__
        method = test._testMethodName
        desc = method.replace('test_', '').replace('_', ' ')
        self.records.append((suite, desc, status, detail))

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, 'PASS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        detail = traceback.format_exception(*err)[-1].strip()
        self._record(test, 'FAIL', detail)

    def addError(self, test, err):
        super().addError(test, err)
        detail = traceback.format_exception(*err)[-1].strip()
        self._record(test, 'ERROR', detail)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, 'SKIP', reason)


# ── Report generator ─────────────────────────────────────────────────────

SUITE_LABELS = {
    'TestStaticServing':        'API — Static file serving',
    'TestCORSAndOptions':       'API — CORS & OPTIONS preflight',
    'TestGetState':             'API — GET /api/state',
    'TestPostState':            'API — POST /api/state',
    'TestSaveQuizResponses':    'API — POST /api/save-quiz-responses',
    'TestSaveCaseResponses':    'API — POST /api/save-case-responses',
    'TestUnknownEndpoints':     'API — Unknown endpoints',
    'TestIndexHTMLExists':      'Frontend — index.html existence',
    'TestJSDataObjects':        'Frontend — JS data objects',
    'TestJSFunctions':          'Frontend — JS functions',
    'TestCSSVariables':         'Frontend — CSS variables',
    'TestAPIEndpointStrings':   'Frontend — API endpoint strings',
    'TestHTMLStructure':        'Frontend — HTML structure',
    'TestStateExampleJSON':     'Content — state.example.json',
    'TestTopicFolders':         'Content — topic folders',
    'TestDocsFolder':           'Content — docs/ folder',
    'TestQuizAndCaseFolders':   'Content — quiz & case folders',
    'TestProjectRootFiles':     'Content — project root files',
    'TestManifest':             'Schema — content manifest',
    'TestTopicsJSON':           'Schema — topics.json',
    'TestQuizSchemas':          'Schema — quiz files',
    'TestCaseSchemas':          'Schema — case study files',
    'TestCoachSchemas':         'Schema — coach files',
    'TestNumQuizSchemas':       'Schema — numerical quiz files',
    'TestMicroSchemas':         'Schema — micro-content files',
    'TestDrillTemplates':       'Digest — numeric drill templates',
    'TestEscaping':             'Digest — MarkdownV2 escaping',
    'TestSelector':             'Digest — weighted selector',
    'TestDigestBuild':          'Digest — full digest builds',
}

STATUS_ICON = {'PASS': '✅', 'FAIL': '❌', 'ERROR': '💥', 'SKIP': '⏭️'}


def generate_report(records, elapsed, run_date, api_skipped=False):
    total  = len(records)
    passed = sum(1 for _, _, s, _ in records if s == 'PASS')
    failed = sum(1 for _, _, s, _ in records if s in ('FAIL', 'ERROR'))
    skipped= sum(1 for _, _, s, _ in records if s == 'SKIP')

    overall = '✅ ALL PASS' if failed == 0 else f'❌ {failed} FAILED'

    lines = [
        '# Test Report — Value Investing Course',
        '',
        f'**Run date:** {run_date}',
        f'**Duration:** {elapsed:.1f}s',
        f'**Result:** {overall}',
        f'**Summary:** {passed} passed · {failed} failed · {skipped} skipped · {total} total',
    ]

    if api_skipped:
        lines += ['', '> ⚠️ API tests were skipped (pass `--no-api` omitted to include them).']

    lines += ['', '---', '']

    # Group by suite
    from collections import OrderedDict
    suites = OrderedDict()
    for suite, desc, status, detail in records:
        suites.setdefault(suite, []).append((desc, status, detail))

    for suite, cases in suites.items():
        label = SUITE_LABELS.get(suite, suite)
        suite_pass   = sum(1 for _, s, _ in cases if s == 'PASS')
        suite_total  = len(cases)
        suite_badge  = '✅' if suite_pass == suite_total else '❌'

        lines += [f'## {suite_badge} {label} ({suite_pass}/{suite_total})', '']
        lines += ['| Test | Status | Detail |', '|------|--------|--------|']

        for desc, status, detail in cases:
            icon = STATUS_ICON.get(status, status)
            safe_detail = detail.replace('\n', ' ').replace('|', '│')[:120]
            lines.append(f'| {desc} | {icon} {status} | {safe_detail} |')

        lines.append('')

    # Failures section
    failures = [(s, d, det) for s, d, st, det in records if st in ('FAIL', 'ERROR')]
    if failures:
        lines += ['---', '', '## Failure Details', '']
        for suite, desc, detail in failures:
            lines += [f'### {suite} → {desc}', '', f'```', detail, f'```', '']

    return '\n'.join(lines)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-api', action='store_true',
                        help='Skip API tests (do not start test server)')
    args = parser.parse_args()

    print('\n📋  Value Investing Course — Regression Tests')
    print('─' * 50)

    start_time = datetime.datetime.now()

    result = CollectingResult()

    # ── Content & Frontend tests (no server needed) ───────────────────────
    from tests import test_content, test_frontend, test_content_schema, test_digest

    for module in (test_content, test_frontend, test_content_schema, test_digest):
        loader = unittest.TestLoader()
        suite  = loader.loadTestsFromModule(module)
        suite.run(result)

    # ── API tests (requires live server) ─────────────────────────────────
    api_skipped = args.no_api
    if not api_skipped:
        from tests.helpers import start_test_server, stop_test_server
        print('  Starting test server on port 18080 ... ', end='', flush=True)
        ok = start_test_server()
        if not ok:
            print('FAILED ❌')
            print('  Cannot start test server. Run with --no-api to skip API tests.')
            api_skipped = True
        else:
            print('ready ✅')
            try:
                from tests import test_api
                loader = unittest.TestLoader()
                suite  = loader.loadTestsFromModule(test_api)
                suite.run(result)
            finally:
                stop_test_server()
                print('  Test server stopped.')
    else:
        print('  API tests skipped (--no-api).')

    elapsed  = (datetime.datetime.now() - start_time).total_seconds()
    run_date = start_time.strftime('%Y-%m-%d %H:%M')

    # ── Print summary ─────────────────────────────────────────────────────
    total   = len(result.records)
    passed  = sum(1 for _, _, s, _ in result.records if s == 'PASS')
    failed  = sum(1 for _, _, s, _ in result.records if s in ('FAIL', 'ERROR'))
    skipped = sum(1 for _, _, s, _ in result.records if s == 'SKIP')

    print()
    print(f'  Results: {passed} passed · {failed} failed · {skipped} skipped · {total} total')
    print(f'  Duration: {elapsed:.1f}s')

    if failed:
        print()
        print('  Failed tests:')
        for suite, desc, status, detail in result.records:
            if status in ('FAIL', 'ERROR'):
                print(f'    ❌  [{suite}] {desc}')
                if detail:
                    print(f'       {detail[:100]}')

    # ── Write report ──────────────────────────────────────────────────────
    report = generate_report(result.records, elapsed, run_date, api_skipped)
    report_path = os.path.join(ROOT, 'tests', 'test-report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print()
    print(f'  Report written → tests/test-report.md')

    if failed:
        print('\n❌  Tests FAILED — commit blocked.\n')
        return 1
    else:
        print('\n✅  All tests passed.\n')
        return 0


if __name__ == '__main__':
    sys.exit(main())
