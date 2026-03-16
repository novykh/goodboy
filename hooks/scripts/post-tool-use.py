#!/usr/bin/env python3
"""
goodboy PostToolUse hook.

Fires after Bash or Write tool calls complete. In behavior-first mode:
- Bash: reminds agent to translate technical output to behavioral language
- Write (.feature): confirms behavior was saved, suggests dashboard
- Write (.feature): triggers dashboard regeneration

Exit code: always 0 (PostToolUse cannot block)
"""

import os
import sys
import json


def is_behavior_first_mode() -> bool:
    return os.path.exists('.behavior-first-mode')


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        sys.exit(0)

    if not is_behavior_first_mode():
        print(json.dumps({}))
        sys.exit(0)

    tool_name = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})

    if tool_name == 'Bash':
        result = {
            "systemMessage": (
                "The command output above may contain technical content. "
                "You MUST translate it to behavioral language before "
                "presenting anything to the user. No error codes, no "
                "stack traces, no file paths. Describe what happened "
                "in terms the user can understand."
            )
        }
        print(json.dumps(result))
        sys.exit(0)

    if tool_name in ('Write', 'Edit', 'MultiEdit'):
        file_path = tool_input.get('file_path', '')
        if file_path.lower().endswith('.feature'):
            result = {
                "systemMessage": (
                    "Behavior saved successfully. Tell the user their "
                    "behavior has been captured. Offer to show the "
                    "dashboard with /goodboy-dashboard."
                )
            }
            print(json.dumps(result))
            sys.exit(0)

    print(json.dumps({}))
    sys.exit(0)


if __name__ == '__main__':
    main()
