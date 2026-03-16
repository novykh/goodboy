#!/usr/bin/env python3
"""
goodboy UserPromptSubmit hook.

Fires when the user sends a message. In behavior-first mode,
detects technical language and reminds the agent to reframe
in behavioral terms.

Exit code: always 0 (UserPromptSubmit cannot block)
"""

import os
import re
import sys
import json


TECHNICAL_PATTERNS = [
    r'\bAPI\b',
    r'\bendpoint\b',
    r'\bdatabase\b',
    r'\bquery\b',
    r'\blatency\b',
    r'\bserver\b',
    r'\bdeploy\b',
    r'\bmigration\b',
    r'\bschema\b',
    r'\bcache\b',
    r'\bCPU\b',
    r'\bmemory\b',
    r'\bcontainer\b',
    r'\bDocker\b',
    r'\bKubernetes\b',
]


def is_behavior_first_mode() -> bool:
    return os.path.exists('.behavior-first-mode')


def contains_technical_language(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in TECHNICAL_PATTERNS)


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        sys.exit(0)

    if not is_behavior_first_mode():
        print(json.dumps({}))
        sys.exit(0)

    user_prompt = hook_input.get('user_prompt', '')

    if contains_technical_language(user_prompt):
        result = {
            "systemMessage": (
                "The user's message contains technical terms. "
                "Reframe your response in behavioral language: "
                "what does the user SEE or EXPERIENCE? Do not "
                "echo the technical terms back."
            )
        }
        print(json.dumps(result))
        sys.exit(0)

    print(json.dumps({}))
    sys.exit(0)


if __name__ == '__main__':
    main()
