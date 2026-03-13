#!/usr/bin/env bash
# Tests for SKILL.md files
#
# Validates that skill files have proper YAML frontmatter,
# required sections, and correct formatting.
#
# Run:
#   bash tests/test_skills.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

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
echo "━━━ Skill files validation ━━━"
echo ""

# ── Test: skill files exist ──

echo "── File existence ──"

SKILL_FILES=(
    "skills/being-a-goodboy/SKILL.md"
    "skills/behavior-translator/SKILL.md"
)

for skill in "${SKILL_FILES[@]}"; do
    if [ -f "${PROJECT_ROOT}/${skill}" ]; then
        pass_test "${skill} exists"
    else
        fail_test "${skill} exists"
    fi
done

# ── Test: reference files exist ──

echo ""
echo "── Reference files ──"

REF_FILES=(
    "skills/behavior-translator/references/word-flow-patterns.md"
    "skills/behavior-translator/references/behavioral-templates.md"
    "skills/behavior-translator/references/mermaid-styles.css"
)

for ref in "${REF_FILES[@]}"; do
    if [ -f "${PROJECT_ROOT}/${ref}" ]; then
        pass_test "${ref} exists"
    else
        fail_test "${ref} exists"
    fi
done

# ── Test: YAML frontmatter ──

echo ""
echo "── YAML frontmatter ──"

for skill in "${SKILL_FILES[@]}"; do
    filepath="${PROJECT_ROOT}/${skill}"
    [ -f "$filepath" ] || continue

    # Check starts with --- (after optional HTML comment)
    has_frontmatter=$(python3 -c "
content = open('$filepath').read()
# Strip leading HTML comment if present
import re
content = re.sub(r'^<!--.*?-->\s*', '', content, flags=re.DOTALL)
lines = content.strip().split('\n')
if lines[0].strip() == '---':
    # Find closing ---
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            print('yes')
            break
    else:
        print('no')
else:
    print('no')
")

    if [ "$has_frontmatter" = "yes" ]; then
        pass_test "${skill} has YAML frontmatter"
    else
        fail_test "${skill} has YAML frontmatter"
    fi

    # Check frontmatter has name and description
    has_name=$(python3 -c "
content = open('$filepath').read()
import re
content = re.sub(r'^<!--.*?-->\s*', '', content, flags=re.DOTALL)
print('yes' if 'name:' in content.split('---')[1] else 'no')
")

    if [ "$has_name" = "yes" ]; then
        pass_test "${skill} frontmatter has 'name' field"
    else
        fail_test "${skill} frontmatter has 'name' field"
    fi

    has_desc=$(python3 -c "
content = open('$filepath').read()
import re
content = re.sub(r'^<!--.*?-->\s*', '', content, flags=re.DOTALL)
print('yes' if 'description:' in content.split('---')[1] else 'no')
")

    if [ "$has_desc" = "yes" ]; then
        pass_test "${skill} frontmatter has 'description' field"
    else
        fail_test "${skill} frontmatter has 'description' field"
    fi
done

# ── Test: behavior-translator has HARD-GATE ──

echo ""
echo "── Behavioral enforcement sections ──"

BT_SKILL="${PROJECT_ROOT}/skills/behavior-translator/SKILL.md"

if grep -q '<HARD-GATE>' "$BT_SKILL" 2>/dev/null; then
    pass_test "behavior-translator has <HARD-GATE> section"
else
    fail_test "behavior-translator has <HARD-GATE> section"
fi

if grep -q '</HARD-GATE>' "$BT_SKILL" 2>/dev/null; then
    pass_test "behavior-translator has closing </HARD-GATE>"
else
    fail_test "behavior-translator has closing </HARD-GATE>"
fi

# ── Test: behavior-translator HARD-GATE forbids code ──

if grep -qi 'FORBIDDEN.*showing code\|showing code.*forbidden\|FORBIDDEN FROM' "$BT_SKILL" 2>/dev/null; then
    pass_test "HARD-GATE explicitly forbids showing code"
else
    fail_test "HARD-GATE explicitly forbids showing code"
fi

# ── Test: being-a-goodboy has EXTREMELY-IMPORTANT ──

UG_SKILL="${PROJECT_ROOT}/skills/being-a-goodboy/SKILL.md"

if grep -q '<EXTREMELY-IMPORTANT>' "$UG_SKILL" 2>/dev/null; then
    pass_test "being-a-goodboy has <EXTREMELY-IMPORTANT> section"
else
    fail_test "being-a-goodboy has <EXTREMELY-IMPORTANT> section"
fi

# ── Test: being-a-goodboy lists activation phrases ──

if grep -q 'You are a goodboy' "$UG_SKILL" 2>/dev/null; then
    pass_test "being-a-goodboy lists 'You are a goodboy' activation phrase"
else
    fail_test "being-a-goodboy lists 'You are a goodboy' activation phrase"
fi

if grep -q "I don't know code" "$UG_SKILL" 2>/dev/null; then
    pass_test "being-a-goodboy lists 'I don't know code' activation phrase"
else
    fail_test "being-a-goodboy lists 'I don't know code' activation phrase"
fi

# ── Test: being-a-goodboy references behavior-translator ──

if grep -q 'behavior-translator' "$UG_SKILL" 2>/dev/null; then
    pass_test "being-a-goodboy references behavior-translator skill"
else
    fail_test "being-a-goodboy references behavior-translator skill"
fi

# ── Test: being-a-goodboy has SUBAGENT-STOP ──

if grep -q '<SUBAGENT-STOP>' "$UG_SKILL" 2>/dev/null; then
    pass_test "being-a-goodboy has <SUBAGENT-STOP> section"
else
    fail_test "being-a-goodboy has <SUBAGENT-STOP> section"
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
