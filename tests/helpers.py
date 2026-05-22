"""Shared test utilities: server lifecycle, constants."""
import os
import sys
import time
import subprocess
import tempfile
import shutil

# Resolve paths relative to project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_PORT = 18080
SERVER_URL = f'http://localhost:{TEST_PORT}'

_server_proc = None
_tmp_dir = None


def start_test_server():
    """Start server.py on TEST_PORT with an isolated state file.
    Returns True when the server is accepting connections."""
    global _server_proc, _tmp_dir

    _tmp_dir = tempfile.mkdtemp(prefix='vic_test_')
    state_file = os.path.join(_tmp_dir, 'state.json')

    env = os.environ.copy()
    env['COURSE_PORT'] = str(TEST_PORT)
    env['COURSE_STATE'] = state_file

    _server_proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, 'server.py')],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Poll until the server responds (max 6 s)
    try:
        import requests
    except ImportError:
        return False

    deadline = time.time() + 6
    while time.time() < deadline:
        try:
            requests.get(f'{SERVER_URL}/', timeout=1)
            return True
        except Exception:
            time.sleep(0.2)

    return False


def stop_test_server():
    """Terminate the test server and delete the temp directory."""
    global _server_proc, _tmp_dir
    if _server_proc:
        _server_proc.terminate()
        try:
            _server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_proc.kill()
        _server_proc = None
    if _tmp_dir and os.path.exists(_tmp_dir):
        shutil.rmtree(_tmp_dir, ignore_errors=True)
        _tmp_dir = None
