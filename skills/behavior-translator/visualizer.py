#!/usr/bin/env python3
"""
HTML Visualizer

Generates interactive HTML pages from behavioral specs, including:
  - Mermaid flow diagrams with auto-refresh
  - Expected vs Actual comparison views
  - Feature file dashboards

All output uses the dark theme from references/mermaid-styles.css
and includes <meta http-equiv="refresh"> for live updates.

Usage (by the agent, not directly by users):
    from visualizer import BehaviorVisualizer

    viz = BehaviorVisualizer('/path/to/project')
    viz.generate_flow_diagram('Cancellation', mermaid_code, '/tmp/flow.html')
    viz.generate_comparison('Cancellation', expected, actual, gap, '/tmp/cmp.html')
    viz.generate_dashboard()  # writes to docs/behaviors/dashboard.html
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils import slugify, escape_html


class BehaviorVisualizer:
    """Generate HTML visualizations for behavioral specs."""

    REFRESH_INTERVAL = 3  # seconds

    def __init__(self, project_dir: str) -> None:
        self.project_dir = project_dir
        self.behaviors_dir = os.path.join(project_dir, 'docs', 'behaviors')
        self.css_path = os.path.join(
            os.path.dirname(__file__),
            'references',
            'mermaid-styles.css',
        )
        os.makedirs(self.behaviors_dir, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────

    def generate_flow_diagram(
        self,
        title: str,
        mermaid_code: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate an HTML page with a Mermaid flow diagram.

        Returns the output file path.
        """
        if output_path is None:
            slug = slugify(title)
            output_path = os.path.join(self.behaviors_dir, f'{slug}-flow.html')

        body = f"""\
  <h1>🐕 Behavior Flow: {escape_html(title)}</h1>
  <div class="mermaid">
{self._indent(mermaid_code, 4)}
  </div>"""

        html = self._wrap_html(title, body)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def generate_comparison(
        self,
        title: str,
        expected: str,
        actual: str,
        gap: str,
        output_path: Optional[str] = None,
        status: str = 'failing',
    ) -> str:
        """Generate an Expected vs Actual comparison page.

        Returns the output file path.
        """
        if output_path is None:
            slug = slugify(title)
            output_path = os.path.join(
                self.behaviors_dir, f'{slug}-comparison.html'
            )

        body = f"""\
  <h1>🐕 Behavior Check: {escape_html(title)}</h1>
  <div class="comparison">
    <div class="expected">
      <h3>✓ Expected Behavior</h3>
      <p>{escape_html(expected)}</p>
    </div>
    <div class="actual {status}">
      <h3>{'✓' if status == 'passing' else '✗'} Actual Behavior</h3>
      <p>{escape_html(actual)}</p>
    </div>
    <div class="gap">
      <h3>Gap Analysis</h3>
      <p>{escape_html(gap)}</p>
    </div>
  </div>"""

        html = self._wrap_html(title, body)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def generate_dashboard(
        self, output_path: Optional[str] = None
    ) -> str:
        """Generate the behavioral spec dashboard.

        Reads all .feature files and creates an overview page.
        Returns the output file path.
        """
        if output_path is None:
            output_path = os.path.join(self.behaviors_dir, 'dashboard.html')

        features = self._scan_features()

        total_passing = sum(f['passing'] for f in features)
        total_failing = sum(f['failing'] for f in features)
        total_untested = sum(f['untested'] for f in features)

        # Build feature list HTML
        feature_items = []
        for f in features:
            if f['failing'] > 0:
                indicator = 'failing'
            elif f['passing'] > 0:
                indicator = 'passing'
            else:
                indicator = 'untested'

            feature_items.append(
                f'    <div class="feature-item">\n'
                f'      <span class="indicator {indicator}"></span>\n'
                f'      <span>{escape_html(f["title"])}</span>\n'
                f'      <span class="status-badge {indicator}">'
                f'{f["passing"]}✓ {f["failing"]}✗ {f["untested"]}?</span>\n'
                f'    </div>'
            )

        feature_list = '\n'.join(feature_items) if feature_items else (
            '    <p>No behaviors described yet. Start by telling the agent '
            'what you want the system to do.</p>'
        )

        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        body = f"""\
  <h1>🐕 Behavioral Spec Dashboard</h1>
  <p class="updated">Last updated: {now}</p>

  <div class="dashboard">
    <div class="stats">
      <span class="status-passing">{total_passing} passing</span>
      <span class="status-failing">{total_failing} failing</span>
      <span class="status-untested">{total_untested} untested</span>
    </div>

    <h2>Features</h2>
    <div class="feature-list">
{feature_list}
    </div>
  </div>"""

        html = self._wrap_html('Dashboard', body)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    # ── Private helpers ─────────────────────────────────────────

    def _wrap_html(self, title: str, body: str) -> str:
        """Wrap content in a full HTML page with styles and auto-refresh."""
        css = self._load_css()
        return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="{self.REFRESH_INTERVAL}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🐕 goodboy — {escape_html(title)}</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({{startOnLoad: true, theme: 'dark'}});</script>
  <style>
{css}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

    def _load_css(self) -> str:
        """Load the Mermaid styles CSS file."""
        try:
            with open(self.css_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback minimal styles
            return """\
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #1a1a2e; color: #e0e0e0;
  max-width: 960px; margin: 0 auto; padding: 2rem;
}
h1 { color: #7dd3fc; }
.mermaid { background: #16213e; padding: 1.5rem; border-radius: 8px; }
.status-passing { color: #4ade80; }
.status-failing { color: #f87171; }
.status-untested { color: #fbbf24; }
"""

    def _scan_features(self) -> List[Dict[str, Any]]:
        """Scan .feature files for dashboard data."""
        features = []
        if not os.path.isdir(self.behaviors_dir):
            return features

        for filename in sorted(os.listdir(self.behaviors_dir)):
            if not filename.endswith('.feature'):
                continue
            filepath = os.path.join(self.behaviors_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()

            title_match = re.search(
                r'^Feature: (.+)$', content, re.MULTILINE
            )
            title = title_match.group(1) if title_match else filename

            total = len(re.findall(r'  Scenario:', content))
            passing = len(re.findall(r'# PASSING', content))
            failing = len(re.findall(r'# FAILING', content))
            untested = total - passing - failing

            features.append({
                'filename': filename,
                'title': title,
                'passing': passing,
                'failing': failing,
                'untested': max(0, untested),
            })

        return features

    @staticmethod
    def _indent(text: str, spaces: int) -> str:
        """Indent each line of text."""
        prefix = ' ' * spaces
        return '\n'.join(prefix + line for line in text.split('\n'))
