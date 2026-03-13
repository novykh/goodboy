#!/usr/bin/env python3
"""
Unit tests for skills/behavior-translator/test_runner.py

Tests the result translation logic. Does NOT require behave/cucumber
to be installed — tests the translation layer independently.

Run:
    python3 -m pytest tests/test_test_runner.py -v
    # or directly:
    python3 tests/test_test_runner.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'skills', 'behavior-translator'),
)
from test_runner import BehaviorTestRunner


class TestTranslateResults(unittest.TestCase):
    """Test the result translation from raw output to behavioral language."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.runner = BehaviorTestRunner(self.tmpdir)

    def test_all_passing(self):
        raw = {
            'runner': 'behave',
            'exit_code': 0,
            'stdout': '',
            'stderr': '',
            'scenarios': [
                {'name': 'Successful signup', 'status': 'passed', 'failed_step': None},
                {'name': 'Duplicate email', 'status': 'passed', 'failed_step': None},
            ],
        }
        result = self.runner._translate_results(raw)
        self.assertEqual(result['status'], 'passing')
        self.assertIn('✓', result['message'])
        self.assertIn('2', result['message'])

    def test_single_passing(self):
        raw = {
            'runner': 'behave',
            'exit_code': 0,
            'stdout': '',
            'stderr': '',
            'scenarios': [
                {'name': 'Login', 'status': 'passed', 'failed_step': None},
            ],
        }
        result = self.runner._translate_results(raw)
        self.assertEqual(result['status'], 'passing')
        self.assertIn('working as expected', result['message'])

    def test_single_failure(self):
        raw = {
            'runner': 'behave',
            'exit_code': 1,
            'stdout': '',
            'stderr': '',
            'scenarios': [
                {
                    'name': 'Welcome email',
                    'status': 'failed',
                    'failed_step': {
                        'name': 'email arrives within 5 minutes',
                        'result': {
                            'status': 'failed',
                            'error_message': 'AssertionError: expected email not found',
                        },
                    },
                },
            ],
        }
        result = self.runner._translate_results(raw)
        self.assertEqual(result['status'], 'failing')
        self.assertIn('Welcome email', result['message'])
        self.assertIn('failing', result['message'].lower())

    def test_mixed_results(self):
        raw = {
            'runner': 'behave',
            'exit_code': 1,
            'stdout': '',
            'stderr': '',
            'scenarios': [
                {'name': 'Login works', 'status': 'passed', 'failed_step': None},
                {
                    'name': 'Password reset',
                    'status': 'failed',
                    'failed_step': {
                        'name': 'reset email sent',
                        'result': {'status': 'failed', 'error_message': 'timeout'},
                    },
                },
                {
                    'name': 'Account deletion',
                    'status': 'failed',
                    'failed_step': {
                        'name': 'account removed',
                        'result': {'status': 'failed', 'error_message': 'not implemented'},
                    },
                },
            ],
        }
        result = self.runner._translate_results(raw)
        self.assertEqual(result['status'], 'failing')
        self.assertIn('2 of 3', result['message'])

    def test_no_scenarios_passing_exit(self):
        raw = {
            'runner': 'behave',
            'exit_code': 0,
            'stdout': '',
            'stderr': '',
            'scenarios': [],
        }
        result = self.runner._translate_results(raw)
        self.assertEqual(result['status'], 'passing')

    def test_no_scenarios_error_exit(self):
        raw = {
            'runner': 'behave',
            'exit_code': 1,
            'stdout': '',
            'stderr': 'ConfigError: no features found',
            'scenarios': [],
        }
        result = self.runner._translate_results(raw)
        self.assertEqual(result['status'], 'error')


class TestStepFailureTranslation(unittest.TestCase):
    """Test that technical step failures are cleaned up."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.runner = BehaviorTestRunner(self.tmpdir)

    def test_strips_file_paths(self):
        step = {
            'result': {
                'status': 'failed',
                'error_message': 'File "/usr/src/app/services/email.py", line 42\nAssertionError: email not sent',
            },
        }
        translated = self.runner._translate_step_failure(step)
        self.assertNotIn('/usr/src/', translated)
        self.assertNotIn('line 42', translated)

    def test_strips_stack_trace(self):
        step = {
            'result': {
                'status': 'failed',
                'error_message': (
                    'Traceback (most recent call last):\n'
                    '  at Object.run (test.js:14:3)\n'
                    '  at Context.<anonymous> (step.js:8:5)\n'
                    'Error: expected true to be false'
                ),
            },
        }
        translated = self.runner._translate_step_failure(step)
        self.assertNotIn('Traceback', translated)
        self.assertNotIn('test.js', translated)

    def test_empty_error(self):
        step = {'result': {'status': 'failed', 'error_message': ''}}
        translated = self.runner._translate_step_failure(step)
        self.assertIn('not matching', translated)

    def test_no_result(self):
        step = {}
        translated = self.runner._translate_step_failure(step)
        self.assertIn('not matching', translated)


class TestRunnerDetection(unittest.TestCase):
    """Test runner detection and no-runner fallback."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.runner = BehaviorTestRunner(self.tmpdir)

    def test_run_feature_no_runner(self):
        """When no test runner is installed, return a clear message."""
        # This test is environment-dependent — if behave IS installed, skip
        if self.runner.check_runner_available():
            self.skipTest('A test runner is installed; cannot test no-runner path')

        # Create a dummy feature file
        behaviors_dir = os.path.join(self.tmpdir, 'docs', 'behaviors')
        os.makedirs(behaviors_dir, exist_ok=True)
        feature_path = os.path.join(behaviors_dir, 'test.feature')
        with open(feature_path, 'w') as f:
            f.write('Feature: Test\n  Scenario: A\n    Given something\n')

        result = self.runner.run_feature(feature_path)
        self.assertEqual(result['status'], 'no_runner')
        self.assertIn('cannot be verified', result['message'])

    def test_run_all_no_features(self):
        result = self.runner.run_all()
        self.assertEqual(result['status'], 'no_features')


class TestAggregateResults(unittest.TestCase):
    """Test result aggregation across multiple features."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.runner = BehaviorTestRunner(self.tmpdir)

    def test_all_passing(self):
        results = [
            {'feature': 'a.feature', 'status': 'passing', 'message': '', 'details': []},
            {'feature': 'b.feature', 'status': 'passing', 'message': '', 'details': []},
        ]
        agg = self.runner._aggregate_results(results)
        self.assertEqual(agg['status'], 'passing')
        self.assertIn('2 behaviors passing', agg['message'])

    def test_mixed(self):
        results = [
            {'feature': 'a.feature', 'status': 'passing', 'message': '', 'details': []},
            {'feature': 'b.feature', 'status': 'failing', 'message': '', 'details': []},
        ]
        agg = self.runner._aggregate_results(results)
        self.assertEqual(agg['status'], 'failing')

    def test_empty(self):
        agg = self.runner._aggregate_results([])
        self.assertIn('No behaviors', agg['message'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
