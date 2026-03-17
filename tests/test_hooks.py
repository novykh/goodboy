#!/usr/bin/env python3
"""
Tests for all goodboy hook scripts.

Covers: post-tool-use.py, user-prompt.py, session-stop.py,
subagent-stop.py, pre-compact.py, and the feature file quality
gate in enforce-behavioral.py.

Run:
    python3 tests/test_hooks.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Tuple

HOOKS_DIR = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'scripts')


def run_hook(script_name: str, input_data: dict) -> Tuple[str, int]:
    script = os.path.join(HOOKS_DIR, script_name)
    proc = subprocess.run(
        [sys.executable, script],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip(), proc.returncode


def parse_output(stdout: str) -> dict:
    return json.loads(stdout) if stdout else {}


class HookTestBase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def activate_mode(self):
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()


class TestPostToolUseBash(HookTestBase):

    def test_no_message_when_mode_inactive(self):
        stdout, code = run_hook('post-tool-use.py', {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"}
        })
        assert code == 0
        assert parse_output(stdout) == {}

    def test_translate_message_when_mode_active(self):
        self.activate_mode()
        stdout, code = run_hook('post-tool-use.py', {
            "tool_name": "Bash",
            "tool_input": {"command": "npm test"}
        })
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "translate" in result["systemMessage"].lower()

    def test_no_message_for_non_bash_non_write(self):
        self.activate_mode()
        stdout, code = run_hook('post-tool-use.py', {
            "tool_name": "Read",
            "tool_input": {"file_path": "foo.txt"}
        })
        assert code == 0
        assert parse_output(stdout) == {}


class TestPostToolUseFeatureWrite(HookTestBase):

    def test_confirm_message_on_feature_write(self):
        self.activate_mode()
        stdout, code = run_hook('post-tool-use.py', {
            "tool_name": "Write",
            "tool_input": {"file_path": "docs/goodboy/behaviors/signup.feature"}
        })
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "saved" in result["systemMessage"].lower()

    def test_no_message_on_non_feature_write(self):
        self.activate_mode()
        stdout, code = run_hook('post-tool-use.py', {
            "tool_name": "Write",
            "tool_input": {"file_path": "src/main.py"}
        })
        assert code == 0
        assert parse_output(stdout) == {}


class TestUserPrompt(HookTestBase):

    def test_no_message_when_mode_inactive(self):
        stdout, code = run_hook('user-prompt.py', {
            "user_prompt": "What's the API latency?"
        })
        assert code == 0
        assert parse_output(stdout) == {}

    def test_reframe_technical_question(self):
        self.activate_mode()
        stdout, code = run_hook('user-prompt.py', {
            "user_prompt": "What's the API latency?"
        })
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "behavioral" in result["systemMessage"].lower()

    def test_no_reframe_for_behavioral_question(self):
        self.activate_mode()
        stdout, code = run_hook('user-prompt.py', {
            "user_prompt": "What happens when someone cancels?"
        })
        assert code == 0
        assert parse_output(stdout) == {}

    def test_detects_database_keyword(self):
        self.activate_mode()
        stdout, code = run_hook('user-prompt.py', {
            "user_prompt": "Can we switch the database?"
        })
        result = parse_output(stdout)
        assert "systemMessage" in result

    def test_detects_deploy_keyword(self):
        self.activate_mode()
        stdout, code = run_hook('user-prompt.py', {
            "user_prompt": "When do we deploy this?"
        })
        result = parse_output(stdout)
        assert "systemMessage" in result


class TestSessionStop(HookTestBase):

    def test_no_message_when_mode_inactive(self):
        stdout, code = run_hook('session-stop.py', {
            "stop_reason": "user_requested"
        })
        assert code == 0
        assert parse_output(stdout) == {}

    def test_no_message_when_no_features(self):
        self.activate_mode()
        stdout, code = run_hook('session-stop.py', {
            "stop_reason": "user_requested"
        })
        assert code == 0
        assert parse_output(stdout) == {}

    def test_summary_when_features_exist(self):
        self.activate_mode()
        behaviors_dir = os.path.join(self.tmpdir, 'docs', 'goodboy', 'behaviors')
        os.makedirs(behaviors_dir)
        Path(os.path.join(behaviors_dir, 'signup.feature')).write_text(
            "Feature: Signup\n  Scenario: Valid email\n    Given a visitor\n    When they sign up\n    Then they see welcome"
        )
        stdout, code = run_hook('session-stop.py', {
            "stop_reason": "user_requested"
        })
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "1" in result["systemMessage"]


class TestSubagentStop(HookTestBase):

    def test_no_message_when_mode_inactive(self):
        stdout, code = run_hook('subagent-stop.py', {
            "agent_id": "sub_123",
            "agent_type": "research"
        })
        assert code == 0
        assert parse_output(stdout) == {}

    def test_translate_message_when_mode_active(self):
        self.activate_mode()
        stdout, code = run_hook('subagent-stop.py', {
            "agent_id": "sub_123",
            "agent_type": "research"
        })
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "translate" in result["systemMessage"].lower()


class TestPreCompact(HookTestBase):

    def test_no_message_when_mode_inactive(self):
        stdout, code = run_hook('pre-compact.py', {})
        assert code == 0
        assert parse_output(stdout) == {}

    def test_no_message_when_no_features(self):
        self.activate_mode()
        stdout, code = run_hook('pre-compact.py', {})
        assert code == 0
        assert parse_output(stdout) == {}

    def test_preserves_context_when_features_exist(self):
        self.activate_mode()
        behaviors_dir = os.path.join(self.tmpdir, 'docs', 'goodboy', 'behaviors')
        os.makedirs(behaviors_dir)
        Path(os.path.join(behaviors_dir, 'cancellation.feature')).write_text(
            "Feature: Subscription Cancellation\n  Scenario: Keep access\n    Given a subscriber\n    When they cancel\n    Then access continues"
        )
        stdout, code = run_hook('pre-compact.py', {})
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "Subscription Cancellation" in result["systemMessage"]
        assert "PRESERVE" in result["systemMessage"]

    def test_lists_multiple_features(self):
        self.activate_mode()
        behaviors_dir = os.path.join(self.tmpdir, 'docs', 'goodboy', 'behaviors')
        os.makedirs(behaviors_dir)
        Path(os.path.join(behaviors_dir, 'signup.feature')).write_text(
            "Feature: Signup\n  Scenario: Valid\n    Given a visitor\n    When signup\n    Then welcome"
        )
        Path(os.path.join(behaviors_dir, 'login.feature')).write_text(
            "Feature: Login\n  Scenario: Valid\n    Given a user\n    When login\n    Then dashboard"
        )
        stdout, code = run_hook('pre-compact.py', {})
        result = parse_output(stdout)
        assert "Signup" in result["systemMessage"]
        assert "Login" in result["systemMessage"]


class TestFeatureFileQualityGate(HookTestBase):

    def test_deny_malformed_feature(self):
        self.activate_mode()
        stdout, code = run_hook('enforce-behavioral.py', {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/goodboy/behaviors/bad.feature",
                "content": "This is not valid gherkin at all"
            }
        })
        assert code == 2
        result = parse_output(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_allow_valid_feature(self):
        self.activate_mode()
        stdout, code = run_hook('enforce-behavioral.py', {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/goodboy/behaviors/good.feature",
                "content": "Feature: Signup\n  Scenario: Valid email\n    Given a visitor\n    When they sign up\n    Then they see welcome"
            }
        })
        assert code == 0

    def test_no_validation_when_mode_inactive(self):
        stdout, code = run_hook('enforce-behavioral.py', {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/goodboy/behaviors/bad.feature",
                "content": "not gherkin"
            }
        })
        assert code == 0


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestPostToolUseBash, TestPostToolUseFeatureWrite,
                TestUserPrompt, TestSessionStop, TestSubagentStop,
                TestPreCompact, TestFeatureFileQualityGate]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
