#!/usr/bin/env python3
"""
goodboy PreCompact hook.

Fires before conversation compaction. In behavior-first mode,
injects a summary of all confirmed behaviors so they survive
the context compression.

Exit code: always 0
"""

import os
import sys
import json
import glob
import re


def is_behavior_first_mode() -> bool:
    return os.path.exists('.behavior-first-mode')


def collect_behavior_summaries() -> list:
    summaries = []
    for filepath in sorted(glob.glob('docs/goodboy/behaviors/*.feature')):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            feature_match = re.search(r'^Feature:\s*(.+)$', content, re.MULTILINE)
            scenarios = re.findall(r'^\s+Scenario:\s*(.+)$', content, re.MULTILINE)
            if feature_match:
                title = feature_match.group(1)
                summary = f"- {title}: {len(scenarios)} scenario(s)"
                summaries.append(summary)
        except OSError:
            continue
    return summaries


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        sys.exit(0)

    if not is_behavior_first_mode():
        print(json.dumps({}))
        sys.exit(0)

    summaries = collect_behavior_summaries()
    if not summaries:
        print(json.dumps({}))
        sys.exit(0)

    behavior_list = "\n".join(summaries)
    result = {
        "systemMessage": (
            "PRESERVE THIS CONTEXT — conversation is being compressed.\n\n"
            "Confirmed behaviors saved to docs/goodboy/behaviors/:\n"
            f"{behavior_list}\n\n"
            "These behaviors have been confirmed by the user and saved "
            "to .feature files. Do not re-ask about them."
        )
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == '__main__':
    main()
