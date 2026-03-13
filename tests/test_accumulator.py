#!/usr/bin/env python3
"""
Unit tests for skills/behavior-translator/accumulator.py

Run:
    python3 -m pytest tests/test_accumulator.py -v
    # or directly:
    python3 tests/test_accumulator.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

# Add the skill module to the path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'skills', 'behavior-translator'),
)
from accumulator import FeatureAccumulator
from utils import slugify


class TestCreateFeature(unittest.TestCase):
    """Test creating new .feature files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.acc = FeatureAccumulator(self.tmpdir)

    def test_create_feature_returns_path(self):
        path = self.acc.create_feature('User Signup', 'New visitors can create an account.')
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(path.endswith('.feature'))

    def test_create_feature_content(self):
        path = self.acc.create_feature('User Signup', 'New visitors can create an account.')
        with open(path) as f:
            content = f.read()
        self.assertIn('Feature: User Signup', content)
        self.assertIn('New visitors can create an account.', content)
        self.assertIn('# Status:', content)

    def test_create_feature_with_scenarios(self):
        scenarios = [
            {
                'name': 'Successful signup',
                'steps': [
                    {'keyword': 'Given', 'text': 'a visitor on the signup page'},
                    {'keyword': 'When', 'text': 'they enter a valid email'},
                    {'keyword': 'Then', 'text': 'they see "Welcome!"'},
                ],
            },
        ]
        path = self.acc.create_feature('User Signup', 'Description.', scenarios)
        with open(path) as f:
            content = f.read()
        self.assertIn('Scenario: Successful signup', content)
        self.assertIn('Given a visitor on the signup page', content)
        self.assertIn('Then they see "Welcome!"', content)

    def test_create_feature_slug_in_filename(self):
        path = self.acc.create_feature('Payment Processing', 'Handles payments.')
        self.assertIn('payment-processing', os.path.basename(path))

    def test_behaviors_dir_created(self):
        self.acc.create_feature('Test', 'Test.')
        self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, 'docs', 'behaviors')))


class TestAppendScenario(unittest.TestCase):
    """Test appending scenarios to existing features."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.acc = FeatureAccumulator(self.tmpdir)

    def test_append_to_existing_feature(self):
        path = self.acc.create_feature('Login', 'User login.')
        self.acc.append_scenario('Login', {
            'name': 'Wrong password',
            'steps': [
                {'keyword': 'Given', 'text': 'a registered user'},
                {'keyword': 'When', 'text': 'they enter wrong password'},
                {'keyword': 'Then', 'text': 'they see an error'},
            ],
        })
        with open(path) as f:
            content = f.read()
        self.assertIn('Scenario: Wrong password', content)

    def test_append_creates_feature_if_missing(self):
        path = self.acc.append_scenario('New Feature', {
            'name': 'First scenario',
            'steps': [
                {'keyword': 'Given', 'text': 'something'},
                {'keyword': 'Then', 'text': 'something else'},
            ],
        })
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            content = f.read()
        self.assertIn('Scenario: First scenario', content)

    def test_append_with_notes(self):
        self.acc.create_feature('Cart', 'Shopping cart.')
        self.acc.append_scenario('Cart', {
            'name': 'Empty cart',
            'steps': [
                {'keyword': 'Given', 'text': 'an empty cart'},
                {'keyword': 'Then', 'text': 'show message'},
            ],
            'notes': 'Current behavior: shows 404 instead',
        })
        path = self.acc._find_feature('Cart')
        with open(path) as f:
            content = f.read()
        self.assertIn('# Current behavior: shows 404 instead', content)


class TestListFeatures(unittest.TestCase):
    """Test listing feature files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.acc = FeatureAccumulator(self.tmpdir)

    def test_list_empty(self):
        features = self.acc.list_features()
        self.assertEqual(features, [])

    def test_list_features(self):
        self.acc.create_feature('Signup', 'Signup flow.')
        self.acc.create_feature('Login', 'Login flow.')
        features = self.acc.list_features()
        self.assertEqual(len(features), 2)
        titles = [f['title'] for f in features]
        self.assertIn('Signup', titles)
        self.assertIn('Login', titles)

    def test_feature_metadata(self):
        self.acc.create_feature('Checkout', 'Checkout flow.', [
            {
                'name': 'Successful purchase',
                'steps': [
                    {'keyword': 'Given', 'text': 'items in cart'},
                    {'keyword': 'Then', 'text': 'order confirmed'},
                ],
            },
        ])
        features = self.acc.list_features()
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['title'], 'Checkout')
        self.assertEqual(features[0]['scenario_count'], 1)
        self.assertIn('Successful purchase', features[0]['scenarios'])


class TestUpdateStatus(unittest.TestCase):
    """Test updating scenario status."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.acc = FeatureAccumulator(self.tmpdir)

    def test_mark_passing(self):
        path = self.acc.create_feature('Test', 'Test.', [
            {
                'name': 'Scenario A',
                'steps': [{'keyword': 'Given', 'text': 'something'}],
            },
        ])
        self.acc.update_scenario_status(path, 'Scenario A', 'passing')
        with open(path) as f:
            content = f.read()
        self.assertIn('# PASSING', content)

    def test_mark_failing_with_note(self):
        path = self.acc.create_feature('Test', 'Test.', [
            {
                'name': 'Scenario B',
                'steps': [{'keyword': 'Given', 'text': 'something'}],
            },
        ])
        self.acc.update_scenario_status(
            path, 'Scenario B', 'failing', 'emails not sending'
        )
        with open(path) as f:
            content = f.read()
        self.assertIn('# FAILING', content)
        self.assertIn('emails not sending', content)

    def test_status_counts_updated(self):
        path = self.acc.create_feature('Test', 'Test.', [
            {
                'name': 'Pass',
                'steps': [{'keyword': 'Given', 'text': 'a'}],
            },
            {
                'name': 'Fail',
                'steps': [{'keyword': 'Given', 'text': 'b'}],
            },
        ])
        self.acc.update_scenario_status(path, 'Pass', 'passing')
        self.acc.update_scenario_status(path, 'Fail', 'failing')
        with open(path) as f:
            content = f.read()
        self.assertIn('1 passing', content)
        self.assertIn('1 failing', content)


class TestSlugify(unittest.TestCase):
    """Test the slugify helper."""

    def test_simple(self):
        self.assertEqual(slugify('User Signup'), 'user-signup')

    def test_special_chars(self):
        self.assertEqual(
            slugify('Payment (v2) — Processing!'),
            'payment-v2-processing',
        )

    def test_multiple_spaces(self):
        self.assertEqual(
            slugify('  lots   of   spaces  '),
            'lots-of-spaces',
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
