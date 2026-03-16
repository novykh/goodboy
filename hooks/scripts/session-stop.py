#!/usr/bin/env python3
"""
goodboy Stop hook.

Fires when the session ends. In behavior-first mode, generates
a summary of behaviors described and saved during the session.

Exit code: always 0
"""

import os
import sys
import json
import glob


def is_behavior_first_mode() -> bool:
    return os.path.exists('.behavior-first-mode')


def count_feature_files() -> int:
    return len(glob.glob('docs/goodboy/behaviors/*.feature'))


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        sys.exit(0)

    if not is_behavior_first_mode():
        print(json.dumps({}))
        sys.exit(0)

    count = count_feature_files()
    if count > 0:
        result = {
            "systemMessage": (
                f"Session ending. There are {count} behavioral spec(s) "
                f"saved in docs/goodboy/behaviors/. Summarize what was "
                f"accomplished this session in behavioral terms before "
                f"closing."
            )
        }
        print(json.dumps(result))
    else:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == '__main__':
    main()
