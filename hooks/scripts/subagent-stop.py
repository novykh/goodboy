#!/usr/bin/env python3
"""
goodboy SubagentStop hook.

Fires when a subagent completes. In behavior-first mode,
reminds the parent agent to translate any technical output
from the subagent into behavioral language.

Exit code: always 0
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

    result = {
        "systemMessage": (
            "A subagent just completed. Its output may contain "
            "technical details. You MUST translate everything to "
            "behavioral language before presenting to the user. "
            "No code, no file paths, no jargon."
        )
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == '__main__':
    main()
