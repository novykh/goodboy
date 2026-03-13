#!/usr/bin/env python3
"""
goodboy PreToolUse enforcement hook.

Intercepts Write and Edit tool calls to ensure output uses behavioral
language instead of code. Reads hook input from stdin in Claude Code
plugin format and outputs a JSON decision.

Exit codes:
  0 — allow (output is behavioral or not a communication tool)
  2 — deny (output contains code; agent must rethink behaviorally)
"""

import re
import sys
import json


def contains_code(content: str) -> bool:
    """Detect if content has code-like patterns."""
    patterns = [
        r'```',                     # code blocks
        r'import\s+\w+',           # imports
        r'function\s+\w+\(',       # function definitions
        r'class\s+\w+',            # class definitions
        r'def\s+\w+\(',            # Python functions
        r'\.\w+\(',                # method calls
        r'src/|lib/|components/',  # file paths
        r'=>|->',                   # arrow operators
    ]
    return any(re.search(p, content) for p in patterns)


def is_behavioral(content: str) -> bool:
    """Check if content uses behavioral language."""
    behavioral_markers = [
        'user sees', 'user clicks', 'system shows',
        'expected behavior', 'actual behavior',
        'when', 'then', 'should', 'flow:',
        'behavior flow', 'word-flow',
        'scenario:', 'given', 'feature:',
    ]
    return any(marker in content.lower() for marker in behavioral_markers)


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        # Can't parse input — allow to avoid blocking the agent
        print(json.dumps({}))
        sys.exit(0)

    tool_name = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})

    if tool_name in ('Write', 'Edit', 'MultiEdit'):
        content = tool_input.get('content', '') or tool_input.get('new_string', '')

        if contains_code(content) and not is_behavioral(content):
            # DENY — block the tool use
            result = {
                "hookSpecificOutput": {
                    "permissionDecision": "deny"
                },
                "systemMessage": (
                    "⛔ Output contains code. You must express this in "
                    "behavioral terms only. Rethink using behavioral mapping: "
                    "What does the user SEE or EXPERIENCE?"
                )
            }
            print(json.dumps(result))
            sys.exit(2)
        else:
            # ALLOW — output is behavioral
            print(json.dumps({}))
            sys.exit(0)
    else:
        # Not a communication tool — allow
        print(json.dumps({}))
        sys.exit(0)


if __name__ == '__main__':
    main()
