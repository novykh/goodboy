#!/usr/bin/env bash
# Tests for plugin.json
#
# Validates the plugin manifest is well-formed and contains
# required fields.
#
# Run:
#   bash tests/test_plugin_json.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLUGIN_JSON="${PROJECT_ROOT}/.claude-plugin/plugin.json"

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
echo "━━━ plugin.json validation ━━━"
echo ""

# ── Test: file exists ──

if [ -f "$PLUGIN_JSON" ]; then
    pass_test "plugin.json exists"
else
    fail_test "plugin.json exists"
    exit 1
fi

# ── Test: valid JSON ──

if python3 -c "import json; json.load(open('$PLUGIN_JSON'))" 2>/dev/null; then
    pass_test "plugin.json is valid JSON"
else
    fail_test "plugin.json is valid JSON"
    exit 1
fi

# ── Test: required fields ──

for field in name version description; do
    has_field=$(python3 -c "
import json
d = json.load(open('$PLUGIN_JSON'))
print('yes' if '$field' in d and d['$field'] else 'no')
")
    if [ "$has_field" = "yes" ]; then
        pass_test "Has '$field' field"
    else
        fail_test "Has '$field' field"
    fi
done

# ── Test: name is "goodboy" ──

name=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON')).get('name', ''))")

if [ "$name" = "goodboy" ]; then
    pass_test "Name is 'goodboy'"
else
    fail_test "Name is 'goodboy'" "Got: $name"
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
