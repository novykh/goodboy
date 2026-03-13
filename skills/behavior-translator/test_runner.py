#!/usr/bin/env python3
"""
Silent Test Runner

Runs Gherkin/Behave tests against .feature files and translates
technical output into behavioral language for non-technical users.

The user never sees test output directly. They see:
  - "This behavior is working as expected ✓"
  - "Expected: X. Actual: Y. Gap: Z."
  - "Something prevented us from checking this behavior."

Usage (by the agent, not directly by users):
    from test_runner import BehaviorTestRunner

    runner = BehaviorTestRunner('/path/to/project')
    result = runner.run_feature('docs/behaviors/2026-03-06-signup.feature')
    print(result['message'])  # behavioral-language summary
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Any, Dict, List, Optional


class BehaviorTestRunner:
    """Run behavioral tests and translate results."""

    def __init__(self, project_dir: str) -> None:
        self.project_dir = project_dir
        self.behaviors_dir = os.path.join(project_dir, 'docs', 'behaviors')
        self.steps_dir = os.path.join(project_dir, 'tests', 'step_definitions')

    # ── Public API ──────────────────────────────────────────────

    def run_feature(self, feature_path: str) -> Dict[str, Any]:
        """Run tests for a single .feature file.

        Returns a dict with:
          - status: 'passing' | 'failing' | 'error' | 'no_runner'
          - message: behavioral-language summary
          - details: list of per-scenario results
        """
        runner = self._detect_runner()
        if runner is None:
            return {
                'status': 'no_runner',
                'message': (
                    'This behavior is described but cannot be verified yet. '
                    'A test framework (Behave or Cucumber) needs to be set up first.'
                ),
                'details': [],
            }

        try:
            raw = self._execute_runner(runner, feature_path)
            return self._translate_results(raw)
        except Exception as e:
            return {
                'status': 'error',
                'message': (
                    'Something prevented us from checking this behavior. '
                    "Let's try again."
                ),
                'details': [{'error': str(e)}],
            }

    def run_all(self) -> Dict[str, Any]:
        """Run tests for all .feature files.

        Returns an aggregate summary.
        """
        if not os.path.isdir(self.behaviors_dir):
            return {
                'status': 'no_features',
                'message': 'No behaviors have been described yet.',
                'details': [],
            }

        features = [
            os.path.join(self.behaviors_dir, f)
            for f in sorted(os.listdir(self.behaviors_dir))
            if f.endswith('.feature')
        ]

        if not features:
            return {
                'status': 'no_features',
                'message': 'No behaviors have been described yet.',
                'details': [],
            }

        results = []
        for feature_path in features:
            result = self.run_feature(feature_path)
            results.append({
                'feature': os.path.basename(feature_path),
                **result,
            })

        return self._aggregate_results(results)

    def check_runner_available(self) -> bool:
        """Check if a test runner is available."""
        return self._detect_runner() is not None

    # ── Private helpers ─────────────────────────────────────────

    def _detect_runner(self) -> Optional[str]:
        """Detect which test runner is available.

        Returns 'behave', 'cucumber', or None.
        """
        # Check for behave (Python)
        try:
            subprocess.run(
                ['behave', '--version'],
                capture_output=True,
                timeout=5,
            )
            return 'behave'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check for cucumber (Ruby/JS)
        try:
            subprocess.run(
                ['cucumber', '--version'],
                capture_output=True,
                timeout=5,
            )
            return 'cucumber'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check for npx cucumber-js
        try:
            result = subprocess.run(
                ['npx', '--no-install', 'cucumber-js', '--version'],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return 'cucumber-js'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return None

    def _execute_runner(
        self, runner: str, feature_path: str
    ) -> Dict[str, Any]:
        """Execute the test runner and capture raw output."""
        if runner == 'behave':
            return self._run_behave(feature_path)
        elif runner == 'cucumber':
            return self._run_cucumber(feature_path)
        elif runner == 'cucumber-js':
            return self._run_cucumber_js(feature_path)
        else:
            raise ValueError(f'Unknown runner: {runner}')

    def _run_behave(self, feature_path: str) -> Dict[str, Any]:
        """Run behave and parse output."""
        result = subprocess.run(
            [
                'behave',
                '--format', 'json',
                '--no-capture',
                feature_path,
            ],
            capture_output=True,
            text=True,
            cwd=self.project_dir,
            timeout=120,
        )

        return {
            'runner': 'behave',
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'scenarios': self._parse_json_output(result.stdout),
        }

    def _run_cucumber(self, feature_path: str) -> Dict[str, Any]:
        """Run cucumber and parse output."""
        result = subprocess.run(
            [
                'cucumber',
                '--format', 'json',
                feature_path,
            ],
            capture_output=True,
            text=True,
            cwd=self.project_dir,
            timeout=120,
        )

        return {
            'runner': 'cucumber',
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'scenarios': self._parse_json_output(result.stdout),
        }

    def _run_cucumber_js(self, feature_path: str) -> Dict[str, Any]:
        """Run cucumber-js and parse output."""
        result = subprocess.run(
            [
                'npx', 'cucumber-js',
                '--format', 'json',
                feature_path,
            ],
            capture_output=True,
            text=True,
            cwd=self.project_dir,
            timeout=120,
        )

        return {
            'runner': 'cucumber-js',
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'scenarios': self._parse_json_output(result.stdout),
        }

    def _parse_json_output(self, stdout: str) -> List[Dict[str, Any]]:
        """Parse JSON output from behave or cucumber into scenario results."""
        import json

        try:
            data = json.loads(stdout)
        except (json.JSONDecodeError, ValueError):
            return self._parse_text_output(stdout)

        scenarios = []
        for feature in data:
            for element in feature.get('elements', []):
                if element.get('type') != 'scenario':
                    continue
                steps = element.get('steps', [])
                failed_step = next(
                    (s for s in steps if s.get('result', {}).get('status') == 'failed'),
                    None,
                )
                scenarios.append({
                    'name': element.get('name', 'Unknown'),
                    'status': 'passed' if failed_step is None else 'failed',
                    'failed_step': failed_step,
                })
        return scenarios

    def _parse_text_output(self, stdout: str) -> List[Dict[str, Any]]:
        """Fallback: parse plain text output for pass/fail indicators."""
        scenarios = []
        # Look for common patterns like "1 scenario (1 passed)"
        passed_match = re.search(r'(\d+) passed', stdout)
        failed_match = re.search(r'(\d+) failed', stdout)

        if passed_match:
            for i in range(int(passed_match.group(1))):
                scenarios.append({
                    'name': f'Scenario {i + 1}',
                    'status': 'passed',
                    'failed_step': None,
                })

        if failed_match:
            for i in range(int(failed_match.group(1))):
                scenarios.append({
                    'name': f'Failed scenario {i + 1}',
                    'status': 'failed',
                    'failed_step': None,
                })

        return scenarios

    def _translate_results(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Translate raw test output into behavioral language."""
        scenarios = raw.get('scenarios', [])

        if not scenarios:
            if raw.get('exit_code', 1) != 0:
                return {
                    'status': 'error',
                    'message': (
                        'Something prevented us from checking this behavior. '
                        'The test setup may need attention.'
                    ),
                    'details': [{'stderr': raw.get('stderr', '')}],
                }
            return {
                'status': 'passing',
                'message': 'This behavior is working as expected ✓',
                'details': [],
            }

        passing = [s for s in scenarios if s['status'] == 'passed']
        failing = [s for s in scenarios if s['status'] == 'failed']

        if not failing:
            if len(passing) == 1:
                msg = 'This behavior is working as expected ✓'
            else:
                msg = f'All {len(passing)} behaviors are working as expected ✓'
            return {
                'status': 'passing',
                'message': msg,
                'details': [
                    {'scenario': s['name'], 'status': 'passing'}
                    for s in passing
                ],
            }

        # Build failure messages in behavioral language
        details = []
        for s in failing:
            detail = {
                'scenario': s['name'],
                'status': 'failing',
            }
            if s.get('failed_step'):
                step = s['failed_step']
                step_name = step.get('name', step.get('keyword', 'unknown'))
                detail['gap'] = self._translate_step_failure(step)
                detail['expected'] = step_name
            details.append(detail)

        for s in passing:
            details.append({
                'scenario': s['name'],
                'status': 'passing',
            })

        if len(failing) == 1:
            f = failing[0]
            gap = details[0].get('gap', 'The behavior is not matching what was described.')
            msg = (
                f"The behavior '{f['name']}' is failing.\n"
                f'{gap}\n'
                f'Want me to fix it?'
            )
        else:
            msg = (
                f'{len(failing)} of {len(scenarios)} behaviors are failing.\n'
                + '\n'.join(
                    f"  ✗ {f['name']}" for f in failing
                )
                + '\nWant me to fix them?'
            )

        return {
            'status': 'failing',
            'message': msg,
            'details': details,
        }

    def _translate_step_failure(self, step: Dict[str, Any]) -> str:
        """Translate a single step failure to behavioral language.

        Strips stack traces, file paths, and technical details.
        """
        result = step.get('result', {})
        error_message = result.get('error_message', '')

        if not error_message:
            return 'The behavior is not matching what was described.'

        # Strip file paths
        cleaned = re.sub(r'(?:File|at) ["\']?[\w/\\._-]+["\']?', '', error_message)
        # Strip line numbers
        cleaned = re.sub(r', line \d+', '', cleaned)
        # Strip stack trace lines
        cleaned = re.sub(r'^\s+at .+$', '', cleaned, flags=re.MULTILINE)
        # Strip traceback header
        cleaned = re.sub(r'Traceback \(most recent call last\):', '', cleaned)
        # Strip parenthesized file:line:col references like (test.js:14:3)
        cleaned = re.sub(r'\([\w./\\-]+:\d+(?::\d+)?\)', '', cleaned)

        # Take the first meaningful line
        lines = [l.strip() for l in cleaned.strip().split('\n') if l.strip()]
        if lines:
            return f'Gap: {lines[0]}'

        return 'The behavior is not matching what was described.'

    def _aggregate_results(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate results from multiple feature files."""
        total_passing = sum(
            1 for r in results if r['status'] == 'passing'
        )
        total_failing = sum(
            1 for r in results if r['status'] == 'failing'
        )
        total_errors = sum(
            1 for r in results if r['status'] == 'error'
        )
        total_no_runner = sum(
            1 for r in results if r['status'] == 'no_runner'
        )

        parts = []
        if total_passing:
            parts.append(f'{total_passing} behaviors passing ✓')
        if total_failing:
            parts.append(f'{total_failing} behaviors failing')
        if total_errors:
            parts.append(f'{total_errors} could not be checked')
        if total_no_runner:
            parts.append(f'{total_no_runner} untested (no test runner)')

        overall = 'passing' if total_failing == 0 and total_errors == 0 else 'failing'

        return {
            'status': overall,
            'message': ' | '.join(parts) if parts else 'No behaviors found.',
            'details': results,
        }
