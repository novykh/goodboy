#!/usr/bin/env bash
# Tests for hooks/session-start
#
# Verifies the SessionStart hook produces valid JSON output,
# injects being-a-goodboy skill content, and detects .behavior-first-mode.
#
# Run:
#   bash tests/test_session_start.sh
#   # or from project root:
#   bash tests/run-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOK="${PROJECT_ROOT}/hooks/session-start"

PASS=0
FAIL=0
TOTAL=0

# ── Helpers ──

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

# Create a temp directory for .behavior-first-mode tests
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# ── Test: produces valid JSON (Claude Code platform) ──

echo ""
echo "━━━ session-start hook ━━━"
echo ""
echo "── JSON output ──"

output=$(CLAUDE_PLUGIN_ROOT="$PROJECT_ROOT" CLAUDE_PROJECT_DIR="$TMPDIR" bash "$HOOK" 2>&1)

if echo "$output" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    pass_test "Produces valid JSON"
else
    fail_test "Produces valid JSON" "Output was: $output"
fi

# ── Test: contains hookSpecificOutput.additionalContext (Claude Code) ──

has_context=$(echo "$output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
print('yes' if ctx else 'no')
" 2>/dev/null || echo "error")

if [ "$has_context" = "yes" ]; then
    pass_test "Contains hookSpecificOutput.additionalContext"
else
    fail_test "Contains hookSpecificOutput.additionalContext" "Got: $has_context"
fi

# ── Test: context includes being-a-goodboy skill content ──

has_skill=$(echo "$output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
print('yes' if 'being-a-goodboy' in ctx else 'no')
" 2>/dev/null || echo "error")

if [ "$has_skill" = "yes" ]; then
    pass_test "Context includes being-a-goodboy skill content"
else
    fail_test "Context includes being-a-goodboy skill content"
fi

# ── Test: context includes EXTREMELY_IMPORTANT wrapper ──

has_wrapper=$(echo "$output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
print('yes' if 'EXTREMELY_IMPORTANT' in ctx else 'no')
" 2>/dev/null || echo "error")

if [ "$has_wrapper" = "yes" ]; then
    pass_test "Context wrapped in EXTREMELY_IMPORTANT"
else
    fail_test "Context wrapped in EXTREMELY_IMPORTANT"
fi

# ── Test: no .behavior-first-mode → no activation message ──

echo ""
echo "── Activation detection (no flag) ──"

no_flag_output=$(CLAUDE_PLUGIN_ROOT="$PROJECT_ROOT" CLAUDE_PROJECT_DIR="$TMPDIR" bash "$HOOK" 2>&1)

has_activation=$(echo "$no_flag_output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
print('yes' if 'BEHAVIOR-FIRST MODE ACTIVE' in ctx else 'no')
" 2>/dev/null || echo "error")

if [ "$has_activation" = "no" ]; then
    pass_test "No .behavior-first-mode file → no activation message"
else
    fail_test "No .behavior-first-mode file → no activation message" "Found activation message when it shouldn't be there"
fi

# ── Test: with .behavior-first-mode → activation message ──

echo ""
echo "── Activation detection (with flag) ──"

touch "$TMPDIR/.behavior-first-mode"

flag_output=$(CLAUDE_PLUGIN_ROOT="$PROJECT_ROOT" CLAUDE_PROJECT_DIR="$TMPDIR" bash "$HOOK" 2>&1)

has_flag_activation=$(echo "$flag_output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
print('yes' if 'BEHAVIOR-FIRST MODE ACTIVE' in ctx else 'no')
" 2>/dev/null || echo "error")

if [ "$has_flag_activation" = "yes" ]; then
    pass_test ".behavior-first-mode present → activation message injected"
else
    fail_test ".behavior-first-mode present → activation message injected"
fi

rm "$TMPDIR/.behavior-first-mode"

# ── Test: non-Claude-Code platform (no CLAUDE_PLUGIN_ROOT) ──

echo ""
echo "── Platform detection ──"

other_output=$(unset CLAUDE_PLUGIN_ROOT; CLAUDE_PROJECT_DIR="$TMPDIR" bash "$HOOK" 2>&1)

has_additional_context=$(echo "$other_output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('yes' if 'additional_context' in d else 'no')
" 2>/dev/null || echo "error")

if [ "$has_additional_context" = "yes" ]; then
    pass_test "Non-Claude-Code platform → uses additional_context field"
else
    fail_test "Non-Claude-Code platform → uses additional_context field" "Got: $(echo "$other_output" | head -1)"
fi

# Does NOT have hookSpecificOutput in non-CC mode
has_hook_specific=$(echo "$other_output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('yes' if 'hookSpecificOutput' in d else 'no')
" 2>/dev/null || echo "error")

if [ "$has_hook_specific" = "no" ]; then
    pass_test "Non-Claude-Code platform → no hookSpecificOutput"
else
    fail_test "Non-Claude-Code platform → no hookSpecificOutput" "Should only emit additional_context"
fi

# ── Test: exit code is 0 ──

echo ""
echo "── Exit code ──"

CLAUDE_PLUGIN_ROOT="$PROJECT_ROOT" CLAUDE_PROJECT_DIR="$TMPDIR" bash "$HOOK" > /dev/null 2>&1
exit_code=$?

if [ "$exit_code" -eq 0 ]; then
    pass_test "Exit code is 0"
else
    fail_test "Exit code is 0" "Got: $exit_code"
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
