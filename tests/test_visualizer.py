#!/usr/bin/env python3
"""
Unit tests for skills/behavior-translator/visualizer.py

Tests HTML generation, dashboard, comparison, and flow diagram output.

Run:
    python3 -m pytest tests/test_visualizer.py -v
    # or directly:
    python3 tests/test_visualizer.py
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'skills', 'behavior-translator'),
)
from visualizer import BehaviorVisualizer
from utils import slugify, escape_html


class TestFlowDiagram(unittest.TestCase):
    """Test Mermaid flow diagram generation."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = BehaviorVisualizer(self.tmpdir)

    def test_generates_html_file(self):
        path = self.viz.generate_flow_diagram(
            'Cancellation',
            'graph TD\n  A[Start] --> B[End]',
        )
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(path.endswith('-flow.html'))

    def test_custom_output_path(self):
        out = os.path.join(self.tmpdir, 'custom', 'flow.html')
        path = self.viz.generate_flow_diagram(
            'Signup', 'graph TD\n  A --> B', output_path=out
        )
        self.assertEqual(path, out)
        self.assertTrue(os.path.isfile(out))

    def test_contains_mermaid_code(self):
        mermaid = 'graph TD\n  A[User clicks] --> B{Confirm?}'
        path = self.viz.generate_flow_diagram('Test', mermaid)
        with open(path) as f:
            html = f.read()
        self.assertIn('A[User clicks]', html)
        self.assertIn('class="mermaid"', html)

    def test_contains_title(self):
        path = self.viz.generate_flow_diagram('My Flow', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn('Behavior Flow: My Flow', html)
        self.assertIn('<title>', html)
        self.assertIn('goodboy', html)

    def test_contains_meta_refresh(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn('http-equiv="refresh"', html)
        self.assertIn(f'content="{BehaviorVisualizer.REFRESH_INTERVAL}"', html)

    def test_contains_mermaid_js(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn('mermaid', html)
        self.assertIn('cdn.jsdelivr.net', html)

    def test_escapes_html_in_title(self):
        path = self.viz.generate_flow_diagram(
            '<script>alert("xss")</script>', 'graph TD\n  A --> B'
        )
        with open(path) as f:
            html = f.read()
        self.assertNotIn('<script>alert', html)
        self.assertIn('&lt;script&gt;', html)

    def test_default_path_uses_slug(self):
        path = self.viz.generate_flow_diagram(
            'User Payment Flow', 'graph TD\n  A --> B'
        )
        basename = os.path.basename(path)
        self.assertIn('user-payment-flow', basename)


class TestComparison(unittest.TestCase):
    """Test expected vs actual comparison page generation."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = BehaviorVisualizer(self.tmpdir)

    def test_generates_html_file(self):
        path = self.viz.generate_comparison(
            'Email Sending',
            expected='Email arrives within 5 minutes',
            actual='No email is sent',
            gap='Queue is stuck',
        )
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(path.endswith('-comparison.html'))

    def test_contains_expected_actual_gap(self):
        path = self.viz.generate_comparison(
            'Login',
            expected='User sees dashboard',
            actual='User sees error page',
            gap='Auth token expired',
        )
        with open(path) as f:
            html = f.read()
        self.assertIn('User sees dashboard', html)
        self.assertIn('User sees error page', html)
        self.assertIn('Auth token expired', html)
        self.assertIn('Expected Behavior', html)
        self.assertIn('Actual Behavior', html)
        self.assertIn('Gap Analysis', html)

    def test_failing_status_indicator(self):
        path = self.viz.generate_comparison(
            'Test', 'a', 'b', 'c', status='failing'
        )
        with open(path) as f:
            html = f.read()
        self.assertIn('class="actual failing"', html)
        self.assertIn('✗', html)

    def test_passing_status_indicator(self):
        path = self.viz.generate_comparison(
            'Test', 'a', 'b', 'c', status='passing'
        )
        with open(path) as f:
            html = f.read()
        self.assertIn('class="actual passing"', html)
        self.assertIn('✓', html)

    def test_contains_meta_refresh(self):
        path = self.viz.generate_comparison('Test', 'a', 'b', 'c')
        with open(path) as f:
            html = f.read()
        self.assertIn('http-equiv="refresh"', html)

    def test_custom_output_path(self):
        out = os.path.join(self.tmpdir, 'out', 'cmp.html')
        path = self.viz.generate_comparison(
            'Test', 'a', 'b', 'c', output_path=out
        )
        self.assertEqual(path, out)
        self.assertTrue(os.path.isfile(out))

    def test_escapes_html_in_content(self):
        path = self.viz.generate_comparison(
            'Test',
            expected='<b>bold</b>',
            actual='a & b',
            gap='"quoted"',
        )
        with open(path) as f:
            html = f.read()
        self.assertIn('&lt;b&gt;bold&lt;/b&gt;', html)
        self.assertIn('a &amp; b', html)
        self.assertIn('&quot;quoted&quot;', html)


class TestDashboard(unittest.TestCase):
    """Test the behavioral spec dashboard generation."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = BehaviorVisualizer(self.tmpdir)
        self.behaviors_dir = os.path.join(self.tmpdir, 'docs', 'behaviors')
        os.makedirs(self.behaviors_dir, exist_ok=True)

    def test_generates_dashboard_file(self):
        path = self.viz.generate_dashboard()
        self.assertTrue(os.path.isfile(path))
        self.assertIn('dashboard.html', path)

    def test_empty_dashboard(self):
        path = self.viz.generate_dashboard()
        with open(path) as f:
            html = f.read()
        self.assertIn('Dashboard', html)
        self.assertIn('No behaviors described yet', html)

    def test_dashboard_with_features(self):
        # Create some .feature files
        with open(os.path.join(self.behaviors_dir, 'signup.feature'), 'w') as f:
            f.write(
                'Feature: User Signup\n'
                '  Scenario: Successful signup\n'
                '    Given a visitor\n'
                '    # PASSING\n'
                '  Scenario: Duplicate email\n'
                '    Given a visitor\n'
                '    # FAILING\n'
            )
        with open(os.path.join(self.behaviors_dir, 'login.feature'), 'w') as f:
            f.write(
                'Feature: User Login\n'
                '  Scenario: Valid credentials\n'
                '    Given a user\n'
                '    # PASSING\n'
                '  Scenario: Forgot password\n'
                '    Given a user\n'
            )

        path = self.viz.generate_dashboard()
        with open(path) as f:
            html = f.read()

        self.assertIn('User Signup', html)
        self.assertIn('User Login', html)
        # Stats: 2 passing, 1 failing, 1 untested
        self.assertIn('2 passing', html)
        self.assertIn('1 failing', html)
        self.assertIn('1 untested', html)

    def test_dashboard_status_indicators(self):
        with open(os.path.join(self.behaviors_dir, 'ok.feature'), 'w') as f:
            f.write(
                'Feature: All Good\n'
                '  Scenario: Works\n'
                '    Given a thing\n'
                '    # PASSING\n'
            )
        with open(os.path.join(self.behaviors_dir, 'bad.feature'), 'w') as f:
            f.write(
                'Feature: Broken\n'
                '  Scenario: Fails\n'
                '    Given a thing\n'
                '    # FAILING\n'
            )

        path = self.viz.generate_dashboard()
        with open(path) as f:
            html = f.read()

        self.assertIn('indicator passing', html)
        self.assertIn('indicator failing', html)

    def test_dashboard_contains_meta_refresh(self):
        path = self.viz.generate_dashboard()
        with open(path) as f:
            html = f.read()
        self.assertIn('http-equiv="refresh"', html)

    def test_custom_output_path(self):
        out = os.path.join(self.tmpdir, 'custom', 'dash.html')
        path = self.viz.generate_dashboard(output_path=out)
        self.assertEqual(path, out)
        self.assertTrue(os.path.isfile(out))


class TestCSSLoading(unittest.TestCase):
    """Test CSS loading and fallback behavior."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = BehaviorVisualizer(self.tmpdir)

    def test_css_in_output(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn('<style>', html)

    def test_fallback_css_when_missing(self):
        # Point to a non-existent CSS path
        self.viz.css_path = '/nonexistent/path/styles.css'
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        # Should still have inline fallback styles
        self.assertIn('<style>', html)
        self.assertIn('background', html)
        self.assertIn('#1a1a2e', html)


class TestHTMLStructure(unittest.TestCase):
    """Test the overall HTML structure of generated pages."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = BehaviorVisualizer(self.tmpdir)

    def test_valid_html_doctype(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertTrue(html.startswith('<!DOCTYPE html>'))

    def test_has_charset(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn('charset="utf-8"', html)

    def test_has_viewport(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn('viewport', html)

    def test_dark_theme_init(self):
        path = self.viz.generate_flow_diagram('Test', 'graph TD\n  A --> B')
        with open(path) as f:
            html = f.read()
        self.assertIn("theme: 'dark'", html)


class TestHelpers(unittest.TestCase):
    """Test static helper methods."""

    def test_escape_html(self):
        self.assertEqual(
            escape_html('<b>"a & b"</b>'),
            '&lt;b&gt;&quot;a &amp; b&quot;&lt;/b&gt;',
        )

    def test_indent(self):
        result = BehaviorVisualizer._indent('line1\nline2', 4)
        self.assertEqual(result, '    line1\n    line2')

    def test_slugify_simple(self):
        self.assertEqual(slugify('Hello World'), 'hello-world')

    def test_slugify_special_chars(self):
        self.assertEqual(
            slugify('My Flow (v2)!'),
            'my-flow-v2',
        )

    def test_slugify_extra_spaces(self):
        self.assertEqual(
            slugify('  lots   of   spaces  '),
            'lots-of-spaces',
        )

    def test_slugify_dashes(self):
        self.assertEqual(
            slugify('a---b'),
            'a-b',
        )


class TestScanFeatures(unittest.TestCase):
    """Test the feature file scanning logic."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = BehaviorVisualizer(self.tmpdir)
        self.behaviors_dir = os.path.join(self.tmpdir, 'docs', 'behaviors')
        os.makedirs(self.behaviors_dir, exist_ok=True)

    def test_empty_dir(self):
        features = self.viz._scan_features()
        self.assertEqual(features, [])

    def test_nonexistent_dir(self):
        self.viz.behaviors_dir = '/nonexistent/path'
        features = self.viz._scan_features()
        self.assertEqual(features, [])

    def test_scans_feature_files(self):
        with open(os.path.join(self.behaviors_dir, 'a.feature'), 'w') as f:
            f.write('Feature: Alpha\n  Scenario: One\n    Given x\n')
        with open(os.path.join(self.behaviors_dir, 'b.feature'), 'w') as f:
            f.write('Feature: Beta\n  Scenario: Two\n    Given y\n    # PASSING\n')

        features = self.viz._scan_features()
        self.assertEqual(len(features), 2)
        titles = [fe['title'] for fe in features]
        self.assertIn('Alpha', titles)
        self.assertIn('Beta', titles)

    def test_counts_statuses(self):
        with open(os.path.join(self.behaviors_dir, 'test.feature'), 'w') as f:
            f.write(
                'Feature: Mixed\n'
                '  Scenario: A\n    Given a\n    # PASSING\n'
                '  Scenario: B\n    Given b\n    # FAILING\n'
                '  Scenario: C\n    Given c\n'
            )

        features = self.viz._scan_features()
        self.assertEqual(len(features), 1)
        feat = features[0]
        self.assertEqual(feat['passing'], 1)
        self.assertEqual(feat['failing'], 1)
        self.assertEqual(feat['untested'], 1)

    def test_ignores_non_feature_files(self):
        with open(os.path.join(self.behaviors_dir, 'dashboard.html'), 'w') as f:
            f.write('<html></html>')
        with open(os.path.join(self.behaviors_dir, 'notes.txt'), 'w') as f:
            f.write('some notes')
        features = self.viz._scan_features()
        self.assertEqual(features, [])

    def test_sorted_alphabetically(self):
        with open(os.path.join(self.behaviors_dir, 'z.feature'), 'w') as f:
            f.write('Feature: Zulu\n  Scenario: A\n    Given x\n')
        with open(os.path.join(self.behaviors_dir, 'a.feature'), 'w') as f:
            f.write('Feature: Alpha\n  Scenario: B\n    Given y\n')

        features = self.viz._scan_features()
        self.assertEqual(features[0]['title'], 'Alpha')
        self.assertEqual(features[1]['title'], 'Zulu')


if __name__ == '__main__':
    unittest.main(verbosity=2)
