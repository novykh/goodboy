#!/usr/bin/env python3
"""
Feature File Accumulator

Manages .feature files in the project's docs/behaviors/ directory.
Creates, appends, and updates Gherkin scenarios as users confirm behaviors
through the behavior-translator skill.

Usage (by the agent, not directly by users):
    from accumulator import FeatureAccumulator

    acc = FeatureAccumulator('/path/to/project')
    acc.create_feature('User Signup', 'New visitors can create an account.')
    acc.append_scenario('User Signup', {
        'name': 'Successful signup with new email',
        'steps': [
            {'keyword': 'Given', 'text': 'a visitor on the signup page'},
            {'keyword': 'When', 'text': 'they enter a valid email and password'},
            {'keyword': 'Then', 'text': 'they see "Welcome!"'},
        ],
    })
"""

from __future__ import annotations

import os
import re
from datetime import date
from typing import Any, Dict, List, Optional

from utils import slugify


class FeatureAccumulator:
    """Manage behavioral .feature files."""

    def __init__(self, project_dir: str) -> None:
        self.behaviors_dir = os.path.join(project_dir, 'docs', 'behaviors')
        os.makedirs(self.behaviors_dir, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────

    def create_feature(
        self,
        title: str,
        description: str,
        scenarios: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Create a new .feature file. Returns the file path."""
        slug = slugify(title)
        today = date.today().isoformat()
        filename = f'{today}-{slug}.feature'
        filepath = os.path.join(self.behaviors_dir, filename)

        lines = [
            f'# Behavioral Spec: {title}',
            f'# Created: {today}',
            f'# Status: untested',
            '',
            f'Feature: {title}',
            f'  {description}',
        ]

        if scenarios:
            for scenario in scenarios:
                lines.append('')
                lines.extend(self._format_scenario(scenario))

        lines.append('')  # trailing newline
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        return filepath

    def append_scenario(self, title: str, scenario: Dict[str, Any]) -> str:
        """Append a scenario to an existing feature file.

        Finds the most recent .feature file matching *title*. If none
        exists, creates a new feature file first.

        Returns the file path that was updated.
        """
        filepath = self._find_feature(title)
        if filepath is None:
            filepath = self.create_feature(title, '')

        formatted = self._format_scenario(scenario)
        with open(filepath, 'a') as f:
            f.write('\n')
            f.write('\n'.join(formatted))
            f.write('\n')

        self._update_header_date(filepath)
        return filepath

    def update_scenario_status(
        self,
        filepath: str,
        scenario_name: str,
        status: str,
        note: Optional[str] = None,
    ) -> None:
        """Mark a scenario as passing, failing, or untested.

        Inserts a comment line after the Scenario: line.
        """
        with open(filepath, 'r') as f:
            content = f.read()

        today = date.today().isoformat()
        marker = f'  # {status.upper()} - marked {today}'
        if note:
            marker += f' - {note}'

        # Remove any existing status marker for this scenario
        pattern = re.compile(
            rf'(  Scenario: {re.escape(scenario_name)}\n)'
            r'(  # (?:PASSING|FAILING|UNTESTED) - .*\n)?'
        )
        replacement = rf'\g<1>{marker}\n'
        new_content = pattern.sub(replacement, content)

        with open(filepath, 'w') as f:
            f.write(new_content)

        self._update_status_counts(filepath)

    def list_features(self) -> List[Dict[str, Any]]:
        """List all .feature files with basic metadata."""
        features = []
        if not os.path.isdir(self.behaviors_dir):
            return features

        for filename in sorted(os.listdir(self.behaviors_dir)):
            if not filename.endswith('.feature'):
                continue
            filepath = os.path.join(self.behaviors_dir, filename)
            features.append(self._parse_feature_metadata(filepath))

        return features

    def get_feature_content(self, title: str) -> Optional[str]:
        """Read the full content of a feature file by title."""
        filepath = self._find_feature(title)
        if filepath is None:
            return None
        with open(filepath, 'r') as f:
            return f.read()

    # ── Private helpers ─────────────────────────────────────────

    def _find_feature(self, title: str) -> Optional[str]:
        """Find the most recent .feature file whose title matches."""
        slug = slugify(title)
        candidates = []
        if not os.path.isdir(self.behaviors_dir):
            return None

        for filename in os.listdir(self.behaviors_dir):
            if filename.endswith('.feature') and slug in filename:
                candidates.append(
                    os.path.join(self.behaviors_dir, filename)
                )

        if not candidates:
            # Try matching by Feature: line inside the file
            for filename in os.listdir(self.behaviors_dir):
                if not filename.endswith('.feature'):
                    continue
                filepath = os.path.join(self.behaviors_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                if f'Feature: {title}' in content:
                    candidates.append(filepath)

        return sorted(candidates)[-1] if candidates else None

    def _format_scenario(self, scenario: Dict[str, Any]) -> List[str]:
        """Format a scenario dict into Gherkin lines."""
        lines = [f"  Scenario: {scenario['name']}"]
        for step in scenario.get('steps', []):
            lines.append(f"    {step['keyword']} {step['text']}")
        if scenario.get('notes'):
            lines.append(f"    # {scenario['notes']}")
        return lines

    def _update_header_date(self, filepath: str) -> None:
        """Update the 'Last Updated' comment in the header."""
        with open(filepath, 'r') as f:
            content = f.read()

        today = date.today().isoformat()
        # Update or add Last Updated line
        if '# Last Updated:' in content:
            content = re.sub(
                r'# Last Updated: .*',
                f'# Last Updated: {today}',
                content,
            )
        elif '# Created:' in content:
            content = content.replace(
                f'# Created:',
                f'# Last Updated: {today}\n# Created:',
                1,
            )

        with open(filepath, 'w') as f:
            f.write(content)

    def _update_status_counts(self, filepath: str) -> None:
        """Recount passing/failing/untested and update the Status header."""
        with open(filepath, 'r') as f:
            content = f.read()

        passing = len(re.findall(r'# PASSING', content))
        failing = len(re.findall(r'# FAILING', content))
        # Count scenarios without a status marker
        total_scenarios = len(re.findall(r'  Scenario:', content))
        untested = total_scenarios - passing - failing

        parts = []
        if passing:
            parts.append(f'{passing} passing')
        if failing:
            parts.append(f'{failing} failing')
        if untested:
            parts.append(f'{untested} untested')

        status_line = ', '.join(parts) if parts else 'no scenarios'
        content = re.sub(
            r'# Status: .*',
            f'# Status: {status_line}',
            content,
        )

        with open(filepath, 'w') as f:
            f.write(content)

    def _parse_feature_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from a .feature file header."""
        with open(filepath, 'r') as f:
            content = f.read()

        title_match = re.search(r'^Feature: (.+)$', content, re.MULTILINE)
        status_match = re.search(r'^# Status: (.+)$', content, re.MULTILINE)
        scenarios = re.findall(r'  Scenario: (.+)', content)

        return {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'title': title_match.group(1) if title_match else 'Unknown',
            'status': status_match.group(1) if status_match else 'unknown',
            'scenario_count': len(scenarios),
            'scenarios': scenarios,
        }

