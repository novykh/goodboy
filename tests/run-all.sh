#!/usr/bin/env bash
# goodboy test suite runner
#
# Runs all tests: Python unit tests + bash integration tests.
#
# Usage:
#   bash tests/run-all.sh           # run everything
#   bash tests/run-all.sh --quick   # skip slow tests (future)
#
# Requirements:
#   - Python 3.8+
#   - bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║      🐕 goodboy test suite           ║"
echo "╠══════════════════════════════════════╣"
echo "║  $(date '+%Y-%m-%d %H:%M:%S')                   ║"
echo "╚══════════════════════════════════════╝"
echo ""

SUITES_PASS=0
SUITES_FAIL=0
FAILED_SUITES=()

run_suite() {
    local name="$1"
    local cmd="$2"

    echo "┌──────────────────────────────────────"
    echo "│ $name"
    echo "└──────────────────────────────────────"

    if eval "$cmd"; then
        SUITES_PASS=$((SUITES_PASS + 1))
        echo ""
    else
        SUITES_FAIL=$((SUITES_FAIL + 1))
        FAILED_SUITES+=("$name")
        echo ""
        echo "  ⚠ Suite failed: $name"
        echo ""
    fi
}

# ── Run all test suites ──

run_suite "plugin.json validation" \
    "bash '${SCRIPT_DIR}/test_plugin_json.sh'"

run_suite "hooks.json validation" \
    "bash '${SCRIPT_DIR}/test_hooks_json.sh'"

run_suite "session-start hook" \
    "bash '${SCRIPT_DIR}/test_session_start.sh'"

run_suite "enforce-behavioral.py (Python unit tests)" \
    "python3 '${SCRIPT_DIR}/test_enforce_behavioral.py'"

run_suite "Skill files validation" \
    "bash '${SCRIPT_DIR}/test_skills.sh'"

run_suite "accumulator.py (Python unit tests)" \
    "python3 '${SCRIPT_DIR}/test_accumulator.py'"

run_suite "test_runner.py (Python unit tests)" \
    "python3 '${SCRIPT_DIR}/test_test_runner.py'"

run_suite "visualizer.py (Python unit tests)" \
    "python3 '${SCRIPT_DIR}/test_visualizer.py'"

# ── Final summary ──

TOTAL=$((SUITES_PASS + SUITES_FAIL))

echo "╔══════════════════════════════════════╗"
echo "║           FINAL RESULTS              ║"
echo "╠══════════════════════════════════════╣"
printf "║  Suites passed: %-20s ║\n" "$SUITES_PASS / $TOTAL"

if [ "$SUITES_FAIL" -gt 0 ]; then
    printf "║  Suites failed: %-20s ║\n" "$SUITES_FAIL"
    echo "╠══════════════════════════════════════╣"
    echo "║  Failed:                             ║"
    for suite in "${FAILED_SUITES[@]}"; do
        printf "║    ✗ %-31s ║\n" "$suite"
    done
fi

echo "╚══════════════════════════════════════╝"

if [ "$SUITES_FAIL" -gt 0 ]; then
    exit 1
fi

echo ""
echo "🐕 All tests passed!"
exit 0
