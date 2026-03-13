#!/usr/bin/env bash
# Tests for hooks/hooks.json
#
# Validates the hook registration file is well-formed JSON,
# contains the expected hooks, and references files that exist.
#
# Run:
#   bash tests/test_hooks_json.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOKS_JSON="${PROJECT_ROOT}/hooks/hooks.json"

PASS=0
FAIL=0
TOTAL=0

pass_test() {
    PASS=$((PASS + 1))
    TOTAL=$((TOTAL + 1))
    echo "  ✓ $1"
}

fail_test() {
    FAIL=$((FAIL + 1))
    TOTAL=$((TOTAL + 1))
    echo "  ✗ $1"
    if [ -n "${2:-}" ]; then
        echo "    → $2"
    fi
}

echo ""
echo "━━━ hooks.json validation ━━━"
echo ""

# ── Test: file exists ──

if [ -f "$HOOKS_JSON" ]; then
    pass_test "hooks/hooks.json exists"
else
    fail_test "hooks/hooks.json exists"
    echo "Cannot continue without hooks.json"
    exit 1
fi

# ── Test: valid JSON ──

if python3 -c "import json; json.load(open('$HOOKS_JSON'))" 2>/dev/null; then
    pass_test "hooks.json is valid JSON"
else
    fail_test "hooks.json is valid JSON"
    echo "Cannot continue with invalid JSON"
    exit 1
fi

# ── Test: has PreToolUse hook ──

has_pretool=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
print('yes' if 'PreToolUse' in d.get('hooks', {}) else 'no')
")

if [ "$has_pretool" = "yes" ]; then
    pass_test "Has PreToolUse hook"
else
    fail_test "Has PreToolUse hook"
fi

# ── Test: PreToolUse matches Write|Edit ──

pretool_matcher=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
hooks = d.get('hooks', {}).get('PreToolUse', [])
if hooks:
    print(hooks[0].get('matcher', ''))
else:
    print('')
")

if [ "$pretool_matcher" = "Write|Edit|MultiEdit" ]; then
    pass_test "PreToolUse matcher is 'Write|Edit|MultiEdit'"
else
    fail_test "PreToolUse matcher is 'Write|Edit|MultiEdit'" "Got: $pretool_matcher"
fi

# ── Test: has UserPromptSubmit hook ──

has_prompt=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
print('yes' if 'UserPromptSubmit' in d.get('hooks', {}) else 'no')
")

if [ "$has_prompt" = "yes" ]; then
    pass_test "Has UserPromptSubmit hook"
else
    fail_test "Has UserPromptSubmit hook"
fi

# ── Test: UserPromptSubmit is a prompt-type hook ──

prompt_type=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
hooks = d.get('hooks', {}).get('UserPromptSubmit', [])
if hooks and hooks[0].get('hooks'):
    print(hooks[0]['hooks'][0].get('type', ''))
else:
    print('')
")

if [ "$prompt_type" = "prompt" ]; then
    pass_test "UserPromptSubmit hook type is 'prompt'"
else
    fail_test "UserPromptSubmit hook type is 'prompt'" "Got: $prompt_type"
fi

# ── Test: UserPromptSubmit prompt mentions activation phrases ──

prompt_content=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
hooks = d.get('hooks', {}).get('UserPromptSubmit', [])
if hooks and hooks[0].get('hooks'):
    p = hooks[0]['hooks'][0].get('prompt', '')
    has_goodboy = 'goodboy' in p.lower()
    has_code = 'code' in p.lower()
    print('yes' if has_goodboy and has_code else 'no')
else:
    print('no')
")

if [ "$prompt_content" = "yes" ]; then
    pass_test "UserPromptSubmit prompt references activation phrases"
else
    fail_test "UserPromptSubmit prompt references activation phrases"
fi

# ── Test: has SessionStart hook ──

has_session=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
print('yes' if 'SessionStart' in d.get('hooks', {}) else 'no')
")

if [ "$has_session" = "yes" ]; then
    pass_test "Has SessionStart hook"
else
    fail_test "Has SessionStart hook"
fi

# ── Test: SessionStart command references run-hook.cmd ──

session_cmd=$(python3 -c "
import json
d = json.load(open('$HOOKS_JSON'))
hooks = d.get('hooks', {}).get('SessionStart', [])
if hooks and hooks[0].get('hooks'):
    print(hooks[0]['hooks'][0].get('command', ''))
else:
    print('')
")

if echo "$session_cmd" | grep -q "run-hook.cmd"; then
    pass_test "SessionStart command uses run-hook.cmd wrapper"
else
    fail_test "SessionStart command uses run-hook.cmd wrapper" "Got: $session_cmd"
fi

if echo "$session_cmd" | grep -q "session-start"; then
    pass_test "SessionStart command invokes session-start hook"
else
    fail_test "SessionStart command invokes session-start hook" "Got: $session_cmd"
fi

# ── Test: referenced scripts exist ──

echo ""
echo "── Referenced file existence ──"

if [ -f "${PROJECT_ROOT}/hooks/scripts/enforce-behavioral.py" ]; then
    pass_test "hooks/scripts/enforce-behavioral.py exists"
else
    fail_test "hooks/scripts/enforce-behavioral.py exists"
fi

if [ -f "${PROJECT_ROOT}/hooks/run-hook.cmd" ]; then
    pass_test "hooks/run-hook.cmd exists"
else
    fail_test "hooks/run-hook.cmd exists"
fi

if [ -f "${PROJECT_ROOT}/hooks/session-start" ]; then
    pass_test "hooks/session-start exists"
else
    fail_test "hooks/session-start exists"
fi

# ── Test: scripts are executable ──

echo ""
echo "── File permissions ──"

if [ -x "${PROJECT_ROOT}/hooks/scripts/enforce-behavioral.py" ]; then
    pass_test "enforce-behavioral.py is executable"
else
    fail_test "enforce-behavioral.py is executable"
fi

if [ -x "${PROJECT_ROOT}/hooks/session-start" ]; then
    pass_test "session-start is executable"
else
    fail_test "session-start is executable"
fi

if [ -x "${PROJECT_ROOT}/hooks/run-hook.cmd" ]; then
    pass_test "run-hook.cmd is executable"
else
    fail_test "run-hook.cmd is executable"
fi

# ── Summary ──

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Results: $PASS passed, $FAIL failed (of $TOTAL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
