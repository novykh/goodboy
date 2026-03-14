#!/usr/bin/env python3
"""
Unit tests for hooks/scripts/enforce-behavioral.py

Tests the PreToolUse enforcement hook that blocks code output
and allows behavioral language output.

Run:
    python3 -m pytest tests/test_enforce_behavioral.py -v
    # or directly:
    python3 tests/test_enforce_behavioral.py
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

# Path to the hook script under test
HOOK_SCRIPT = os.path.join(
    os.path.dirname(__file__), '..', 'hooks', 'scripts', 'enforce-behavioral.py'
)


def run_hook(input_data: dict) -> Tuple[str, int]:
    """Run the enforce-behavioral hook with given JSON input.

    Returns (stdout, exit_code).
    """
    proc = subprocess.run(
        [sys.executable, HOOK_SCRIPT],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip(), proc.returncode


def parse_output(stdout: str) -> dict:
    """Parse JSON output from hook."""
    return json.loads(stdout) if stdout else {}


# ── Deny cases: code content in Write/Edit tools ──


class TestDenyCodeOutput(unittest.TestCase):
    """Hook must DENY (exit 2) when Write/Edit contains code."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.tmpdir)
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_deny_import_statement(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "import os\nprint('hello')"}
        })
        assert code == 2, f"Expected exit 2 (deny), got {code}"
        result = parse_output(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_deny_function_definition(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "function handleClick(event) {\n  return true;\n}"}
        })
        assert code == 2

    def test_deny_python_def(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "def process_payment(amount):\n    pass"}
        })
        assert code == 2

    def test_deny_class_definition(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "class UserService:\n    pass"}
        })
        assert code == 2

    def test_deny_code_block(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "Here is the solution:\n```python\nprint('hi')\n```"}
        })
        assert code == 2

    def test_deny_file_paths(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "Check src/services/email.ts for the implementation"}
        })
        assert code == 2

    def test_deny_arrow_function_syntax(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "const handler = () => { return data; }"}
        })
        assert code == 2

    def test_deny_method_call(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "Call user.getProfile() to fetch the data"}
        })
        assert code == 2

    def test_deny_edit_tool_with_code(self):
        stdout, code = run_hook({
            "tool_name": "Edit",
            "tool_input": {"new_string": "import stripe\nstripe.Charge.create(amount=100)"}
        })
        assert code == 2

    def test_deny_multiedit_tool_with_code(self):
        stdout, code = run_hook({
            "tool_name": "MultiEdit",
            "tool_input": {"content": "class PaymentProcessor:\n    def charge(self): pass"}
        })
        assert code == 2

    def test_deny_message_includes_system_guidance(self):
        """Denied output should include a systemMessage guiding the agent."""
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "import json\njson.loads(data)"}
        })
        assert code == 2
        result = parse_output(stdout)
        assert "systemMessage" in result
        assert "behavioral" in result["systemMessage"].lower()


# ── Allow cases: behavioral content ──


class TestAllowBehavioralOutput(unittest.TestCase):
    """Hook must ALLOW (exit 0) when content uses behavioral language."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.tmpdir)
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_allow_user_sees(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "When the user sees the confirmation page, they click Continue."}
        })
        assert code == 0

    def test_allow_user_clicks(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "The user clicks 'Submit' and the system shows a success message."}
        })
        assert code == 0

    def test_allow_expected_behavior(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "content": "Expected behavior: welcome email arrives within 5 minutes. "
                           "Actual behavior: no email sent."
            }
        })
        assert code == 0

    def test_allow_gherkin_scenario(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "content": (
                    "Feature: Signup\n"
                    "  Scenario: Successful signup\n"
                    "    Given a visitor on the signup page\n"
                    "    When they enter a valid email\n"
                    "    Then they see a welcome message"
                )
            }
        })
        assert code == 0

    def test_allow_word_flow_diagram(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "content": (
                    "Behavior Flow: Cancellation\n"
                    "User clicks Cancel → Show confirmation → "
                    "User confirms → Access continues until billing period ends"
                )
            }
        })
        assert code == 0

    def test_allow_status_report(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "This behavior is working as expected. When the customer cancels, they keep access."}
        })
        assert code == 0


# ── Allow cases: non-communication tools ──


class TestAllowNonCommunicationTools(unittest.TestCase):
    """Hook must ALLOW (exit 0) for tools that aren't Write/Edit."""

    def test_allow_read_tool(self):
        stdout, code = run_hook({
            "tool_name": "Read",
            "tool_input": {"path": "src/main.py"}
        })
        assert code == 0

    def test_allow_bash_tool(self):
        stdout, code = run_hook({
            "tool_name": "Bash",
            "tool_input": {"command": "npm test"}
        })
        assert code == 0

    def test_allow_list_tool(self):
        stdout, code = run_hook({
            "tool_name": "ListFiles",
            "tool_input": {"path": "."}
        })
        assert code == 0

    def test_allow_unknown_tool(self):
        stdout, code = run_hook({
            "tool_name": "SomeNewTool",
            "tool_input": {}
        })
        assert code == 0


# ── Edge cases ──


class TestEdgeCases(unittest.TestCase):
    """Edge cases and error handling."""

    def test_invalid_json_input(self):
        """Invalid JSON should not crash — safe fallback to allow."""
        proc = subprocess.run(
            [sys.executable, HOOK_SCRIPT],
            input="this is not json",
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, "Invalid JSON should fallback to allow"

    def test_empty_input(self):
        """Empty stdin should not crash."""
        proc = subprocess.run(
            [sys.executable, HOOK_SCRIPT],
            input="",
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0

    def test_missing_tool_name(self):
        stdout, code = run_hook({"tool_input": {"content": "import os"}})
        assert code == 0, "Missing tool_name should fallback to allow"

    def test_missing_tool_input(self):
        stdout, code = run_hook({"tool_name": "Write"})
        assert code == 0, "Missing tool_input with no content should allow"

    def test_empty_content(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": ""}
        })
        assert code == 0, "Empty content should allow"

    def test_prose_with_braces_no_behavioral_markers(self):
        """Prose containing braces but no code should be allowed."""
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "The customer receives a confirmation message with {their name} and {order number}."}
        })
        assert code == 0, "Braces in prose should not trigger code detection"

    def test_behavioral_content_with_incidental_braces(self):
        """Content with braces and behavioral markers should be allowed."""
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "When the user sees {name} in the greeting, the system shows their profile."}
        })
        assert code == 0


# ── Behavior-first mode gate ──


class TestBehaviorFirstModeGate(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_allow_code_when_mode_inactive(self):
        os.chdir(self.tmpdir)
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "import os\nprint('hello')"}
        })
        assert code == 0, f"Expected allow when behavior-first mode inactive, got exit {code}"

    def test_deny_code_when_mode_active(self):
        os.chdir(self.tmpdir)
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "import os\nprint('hello')"}
        })
        assert code == 2, f"Expected deny when behavior-first mode active, got exit {code}"


# ── Markdown auto-translate ──


class TestMarkdownAutoTranslate(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.tmpdir)
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_allow_markdown_with_code(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/design.md",
                "content": "# Design\n```python\nimport os\n```"
            }
        })
        assert code == 0, f"Expected allow for .md with code, got exit {code}"

    def test_inject_translation_message_for_markdown_with_code(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/design.md",
                "content": "# Design\n```python\nimport os\n```"
            }
        })
        result = parse_output(stdout)
        assert "systemMessage" in result, "Expected systemMessage for .md with code"
        assert "behavioral" in result["systemMessage"].lower()

    def test_no_message_for_markdown_without_code(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/notes.md",
                "content": "# Notes\nThe user should see a welcome page."
            }
        })
        assert code == 0
        result = parse_output(stdout)
        assert result == {} or "systemMessage" not in result

    def test_still_deny_non_markdown_with_code(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "src/main.py",
                "content": "import os\nprint('hello')"
            }
        })
        assert code == 2, "Non-.md files with code should still be denied"

    def test_markdown_case_insensitive(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "docs/DESIGN.MD",
                "content": "# Design\n```js\nconst x = 1;\n```"
            }
        })
        assert code == 0, "Should detect .MD (uppercase) as markdown"

    def test_edit_tool_markdown_with_code(self):
        stdout, code = run_hook({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "docs/spec.md",
                "new_string": "def process():\n    pass"
            }
        })
        assert code == 0, "Edit on .md with code should be allowed"
        result = parse_output(stdout)
        assert "systemMessage" in result


# ── Full decision tree integration ──


class TestFullDecisionTree(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_mode_inactive_allows_everything(self):
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "import os", "file_path": "main.py"}
        })
        assert code == 0

    def test_mode_active_md_with_code_allows_with_message(self):
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "```python\nimport os\n```", "file_path": "doc.md"}
        })
        assert code == 0
        result = parse_output(stdout)
        assert "systemMessage" in result

    def test_mode_active_py_with_code_denies(self):
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "import os", "file_path": "main.py"}
        })
        assert code == 2

    def test_mode_active_md_no_code_allows_silently(self):
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "# Just a heading\nSome notes.", "file_path": "notes.md"}
        })
        assert code == 0
        result = parse_output(stdout)
        assert result == {} or "systemMessage" not in result

    def test_mode_active_behavioral_content_allows(self):
        Path(os.path.join(self.tmpdir, '.behavior-first-mode')).touch()
        stdout, code = run_hook({
            "tool_name": "Write",
            "tool_input": {"content": "When the user sees the page, the system shows a message."}
        })
        assert code == 0


# ── Run with unittest if executed directly ──

if __name__ == '__main__':
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestDenyCodeOutput, TestAllowBehavioralOutput,
                TestAllowNonCommunicationTools, TestEdgeCases,
                TestBehaviorFirstModeGate, TestMarkdownAutoTranslate,
                TestFullDecisionTree]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
