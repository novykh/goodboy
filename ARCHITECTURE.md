# goodboy - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER LAYER                          │
│  Natural language behavior descriptions                     │
│  Visual HTML output (Mermaid diagrams, flow charts)        │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    BEHAVIOR-TRANSLATOR                       │
│  • Forces behavioral mapping before any response            │
│  • Verifies thinking through behavioral coherence           │
│  • Translates technical results to behavioral language      │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                      ENFORCEMENT LAYER                       │
│  PreToolUse hooks block code output mechanically            │
│  permissionDecision: "deny" on non-behavioral content       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    ACCUMULATION LAYER                        │
│  .feature files grow with confirmed behaviors               │
│  Gherkin generation + step definitions (hidden from user)   │
│  Test execution (Cucumber/Behave/etc)                       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   SKILL CHAIN LAYER                          │
│  brainstorming → planning → execution → review              │
│  Failing behaviors trigger implementation chain             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Behavior-Translator Skill

**Location:** `skills/behavior-translator/SKILL.md`

**Core Responsibilities:**
- Intercept all agent thinking before presentation
- Force complete behavioral mapping
- Detect gaps, contradictions, circular logic
- Refuse to surface response until map is valid

**Enforcement Pattern:**
```markdown
<HARD-GATE>
BEFORE ANY RESPONSE TO USER, YOU MUST:

1. Create a complete behavioral map of your answer
2. Verify the map has:
   - Clear trigger (what causes this behavior)
   - No circular paths or dead ends
3. Synthesize rambling or sprawling inputs into clear, pure behavioral steps
4. Ignore explicit CSS or UI styling requests (e.g. "make the button round") - focus ONLY on behavior
5. If map has gaps → FIX YOUR THINKING, then retry
6. If map is valid → proceed to present behavioral map only

YOU ARE STRICTLY FORBIDDEN FROM:
- Showing code to users
- Mentioning file paths, function names, imports
- Using technical jargon (API, database, endpoint, etc.)
- Showing test failures as stack traces
- Describing implementation details

IF YOU CANNOT EXPRESS SOMETHING BEHAVIORALLY:
Ask the user to clarify what they expect to see or experience.
</HARD-GATE>
```

**Word-Flow Diagram Format:**
```
[Trigger Event]
  → [Decision Point]?
    → yes → [Outcome A] → [Next State]
    → no → [Outcome B] → [Alternative Path]
  
Edge: What if [unexpected condition]?
  → [Fallback Behavior] → [Recovery Path]
```

---

### 2. PreToolUse Hook (Enforcement)

**Location:** `hooks/scripts/enforce-behavioral.py`

**Hook Registration (`hooks/hooks.json`):**

goodboy follows the [Claude Code plugin](https://github.com/anthropics/claude-code) hook architecture. Hooks are defined in the plugin's `hooks/hooks.json` using the standard wrapper format:

```json
{
  "description": "goodboy behavioral enforcement hooks",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/enforce-behavioral.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if the user is activating goodboy mode. Look for phrases like 'You are a goodboy', 'I don't know code', or 'show me the behavior'. If detected, respond only in behavioral language for the ENTIRE session per the behavior-translator skill. Return 'approve'.",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Detection Logic:**
```python
import re
import sys
import json

def contains_code(content):
    """Detect if content has code-like patterns"""
    patterns = [
        r'```',                    # code blocks
        r'import\s+\w+',          # imports
        r'function\s+\w+\(',      # function definitions
        r'class\s+\w+',           # class definitions  
        r'def\s+\w+\(',           # Python functions
        r'\.\w+\(',               # method calls
        r'src/|lib/|components/', # file paths
        r'=>|->|\{|\}',           # code syntax
    ]
    return any(re.search(p, content) for p in patterns)

def is_behavioral(content):
    """Check if content uses behavioral language"""
    behavioral_markers = [
        'user sees', 'user clicks', 'system shows',
        'expected behavior', 'actual behavior',
        'when', 'then', 'should', 'flow:'
    ]
    return any(marker in content.lower() for marker in behavioral_markers)

# Read hook input from stdin (Claude Code plugin format)
hook_input = json.loads(sys.stdin.read())

tool_name = hook_input.get('tool_name', '')
tool_input = hook_input.get('tool_input', {})

if tool_name in ['Write', 'Edit', 'MultiEdit']:
    content = tool_input.get('content', '') or tool_input.get('new_text', '')
    
    if contains_code(content) and not is_behavioral(content):
        # DENY - block the tool use
        result = {
            "hookSpecificOutput": {
                "permissionDecision": "deny"
            },
            "systemMessage": "⛔ Output contains code. You must express this in behavioral terms only. Rethink using behavioral mapping: What does the user SEE or EXPERIENCE?"
        }
        print(json.dumps(result))
        sys.exit(2)
    else:
        # ALLOW - output is behavioral
        print(json.dumps({}))
        sys.exit(0)
else:
    # Not a communication tool, allow
    print(json.dumps({}))
    sys.exit(0)
```

---

### 3. Feature File Accumulator

**Location:** `skills/behavior-translator/accumulator.py`

**Purpose:** Persist confirmed behaviors as executable Gherkin

**File Structure:**
```
docs/behaviors/
  ├── YYYY-MM-DD-user-signup.feature
  ├── YYYY-MM-DD-subscription-cancellation.feature  
  └── YYYY-MM-DD-payment-processing.feature
```

**Feature File Format:**
```gherkin
# Behavioral Spec: Subscription Cancellation
# Last Updated: 2026-03-06
# Status: 2 scenarios passing, 1 failing

Feature: Subscription Cancellation
  Users who cancel should maintain access until their billing period ends.
  This ensures fair value delivery and reduces support tickets.

  Scenario: Standard cancellation with time remaining
    Given a customer with an active subscription
    And 15 days remaining in their billing period
    When they click "Cancel Subscription"
    And confirm the cancellation
    Then they see "Your subscription will end on [date]"
    And they maintain full access
    And on the billing period end date their access is removed
    And they receive an email "Your subscription has ended"
    
  Scenario: Immediate cancellation fallback
    Given a customer with 0 days remaining in billing period
    When they cancel their subscription
    Then they see "Your access has ended"
    And they are immediately logged out

  # FAILING - marked 2026-03-06
  Scenario: Cancellation during trial period
    Given a customer in a 14-day trial
    When they cancel
    Then access should end immediately
    # Current behavior: access continues for full 14 days
```

**Append Logic:**
```python
def append_behavior(feature_file, scenario_dict):
    """Add new scenario to feature file"""
    with open(feature_file, 'a') as f:
        f.write(f"\n  Scenario: {scenario_dict['name']}\n")
        for step in scenario_dict['steps']:
            f.write(f"    {step['keyword']} {step['text']}\n")
        if scenario_dict.get('notes'):
            f.write(f"    # {scenario_dict['notes']}\n")
```

---

### 4. HTML Generation & Auto-Refresh Layer

**Location:** `skills/behavior-translator/visualizer.py`

**Based on:** nicobailon/visual-explainer patterns

**Core Responsibilities:**
- Render generated behavioral `.feature` files into interactive Mermaid HTML pages
- Automatically inject meta-refresh tags to auto-refresh the page when underlying files change. This prevents non-technical users from having to manually hit refresh in their browser.

**Output Types:**
- **Word-flow diagrams** — Mermaid flowcharts via `generate_flow_diagram()`
- **Expected vs Actual comparison** — side-by-side gap analysis via `generate_comparison()`
- **Feature dashboard** — overview of all behaviors and their status via `generate_dashboard()`

All pages use the dark theme from `references/mermaid-styles.css`, include `<meta http-equiv="refresh" content="3">` for live updates, and render Mermaid diagrams client-side via CDN.

---

### 5. Test Execution (Silent)

**Location:** `skills/behavior-translator/test_runner.py`

**Flow:**
```
Behavior confirmed by user
  ↓
Generate Gherkin scenario
  ↓
Generate step definitions (if new steps needed)
  ↓
Run Cucumber/Behave test
  ↓
Capture results
  ↓
Translate to behavioral language
  ↓
Return to user: "This behavior passes/fails"
```

**Step Definition Generation:**
```python
def generate_step_definition(step_text, codebase_context):
    """
    Use agent to generate step definition code.
    This part is hidden from user entirely.
    """
    prompt = f"""
    Generate a Cucumber step definition for:
    "{step_text}"
    
    Context: {codebase_context}
    
    The step should:
    - Actually test the behavior
    - Be idiomatic for the project's test framework
    - Handle setup and teardown
    """
    # Agent generates code here (invisible to user)
    return generated_code
```

**Result Translation:**
```python
def translate_test_result(cucumber_output):
    """
    Convert technical test output to behavioral language
    """
    if cucumber_output['status'] == 'passed':
        return {
            'status': 'passing',
            'message': 'This behavior is working as expected.'
        }
    
    elif cucumber_output['status'] == 'failed':
        step_that_failed = cucumber_output['failing_step']
        
        return {
            'status': 'failing',
            'message': f"Expected behavior: {step_that_failed['expected']}\n"
                      f"Actual behavior: {step_that_failed['actual']}\n"
                      f"Gap: {analyze_gap(step_that_failed)}"
        }
```

---

### 6. Session Start & Skill Chaining

**Session Start Hook:**
```bash
# hooks/session-start (extensionless — invoked via run-hook.cmd polyglot wrapper)
# Loads behavior-translator context at session start.
#
# Activation is primarily via natural language (UserPromptSubmit hook above),
# but developers can also drop a .behavior-first-mode file in the project root
# to auto-activate for every session (useful when setting up for non-technical teammates).

if [ -f "$CLAUDE_PROJECT_DIR/.behavior-first-mode" ]; then
  echo "{\"systemMessage\": \"BEHAVIOR-FIRST MODE ACTIVE (via .behavior-first-mode file). Use the behavior-translator skill for ALL interactions this session. Review ${CLAUDE_PLUGIN_ROOT}/skills/behavior-translator/SKILL.md.\"}"
else
  echo "{\"systemMessage\": \"goodboy plugin loaded. Say 'You are a goodboy and I don't know code' to activate behavior-first mode.\"}"
fi
```

> **Two activation paths:**
> 1. **Natural language (primary):** User says the phrase → `UserPromptSubmit` hook detects it → behavior mode for the session.
> 2. **File flag (secondary, developer-facing):** `touch .behavior-first-mode` in project root → `SessionStart` hook auto-activates every session. Useful for persistent team setups or CI.

**Non-Technical User Detection:**
```markdown
## Non-Technical User Detection

Activate behavior-first mode when the user says ANY of:
- "You are a goodboy and I don't know code"
- "I don't know code"
- "Explain this without technical terms"
- "Show me the behavior"

OR when the `.behavior-first-mode` file exists in the project root.

Once activated, maintain behavior-translator for the ENTIRE session.
```

**Skill Chaining:**
```
User describes behavior
  ↓
behavior-translator maps it
  ↓
User confirms
  ↓
behavior-translator appends to .feature
  ↓
Tests run → FAIL
  ↓
behavior-translator invokes brainstorming (as subagent)
  ↓
brainstorming plans implementation (not shown to user)
  ↓
execution (not shown to user)
  ↓
Tests run → PASS
  ↓
User sees: "This behavior is now working ✓"
```

---

## Data Flow Examples

### Example 1: New Behavior Description

```
[USER INPUT]
"When someone tries to sign up with an email that's already registered,
they should see a friendly message suggesting they try logging in instead."

[BEHAVIOR-TRANSLATOR INTERNAL PROCESS]
1. Map behavior:
   User enters email → System checks database → Email exists? 
   → yes → Show "This email is already registered. Try logging in?"
           → Offer password reset link
   → no → Continue with signup

2. Verify map completeness:
   - Trigger: clear ✓
   - Outcome: observable ✓  
   - Edge cases: what if API is down? [MISSING]
   
3. Ask for clarification: "What should happen if the system 
   can't check the email right now?"

[USER RESPONSE]
"Just let them continue with signup. We'll handle duplicates later."

[BEHAVIOR-TRANSLATOR]
4. Update map with edge case
5. Map is now complete
6. Present to user as word-flow diagram (opens in browser)
7. User confirms
8. Append to .feature file
9. Generate step definitions
10. Run tests → FAILING
11. Return: "This behavior is defined. Currently failing because..."

[VISUAL OUTPUT - HTML]
(Mermaid diagram showing full flow with green/red indicators)
```

### Example 2: Debugging Existing Behavior

```
[USER INPUT]
"The welcome email isn't sending when people sign up"

[BEHAVIOR-TRANSLATOR]
1. Map expected behavior:
   User completes signup → Account created → Welcome email sent within 5 min
   
2. Run tests for this behavior
3. Detect failure at "email sent" step
4. Invoke systematic-debugging (as subagent, hidden)
5. Debugging finds: email job queued but worker not processing
6. Translate to behavioral terms

[RESPONSE TO USER]
"Let me check that behavior:

Expected: User signs up → Welcome email arrives within 5 minutes
Actual: User signs up → No email is sent

The gap: The system is preparing to send the email but it's 
getting stuck in a queue. Messages aren't being delivered.

This behavior has been failing since [timestamp]. Want me to fix it?"

[NO CODE SHOWN TO USER DESPITE DETAILED TECHNICAL DEBUG]
```

---

## File Structure

```
goodboy/                             # Claude Code plugin root
├── plugin.json                      # Plugin manifest
├── hooks/
│   ├── hooks.json                   # Hook registration (PreToolUse, SessionStart, UserPromptSubmit)
│   ├── run-hook.cmd                 # Cross-platform polyglot wrapper (Windows batch + bash)
│   ├── session-start                # SessionStart: load being-a-goodboy context, detect .behavior-first-mode
│   └── scripts/
│       └── enforce-behavioral.py    # PreToolUse: block code output
│
├── skills/
│   ├── being-a-goodboy/
│   │   └── SKILL.md                 # Meta-skill: activation, session rules, skill priority
│   └── behavior-translator/
│       ├── SKILL.md                 # Main skill definition (HARD-GATE, checklist, process flow)
│       ├── accumulator.py           # Feature file accumulator (create, append, status tracking)
│       ├── test_runner.py           # Silent test runner (behave/cucumber, result translation)
│       ├── visualizer.py            # HTML visualizer (flow diagrams, comparison, dashboard)
│       └── references/
│           ├── word-flow-patterns.md    # Flow diagram patterns reference
│           ├── behavioral-templates.md  # Ready-to-use Gherkin + word-flow templates
│           └── mermaid-styles.css       # Dark theme for HTML visual output
│
├── tests/
│   ├── run-all.sh                   # Top-level test runner (all suites)
│   ├── test_plugin_json.sh          # Plugin manifest validation
│   ├── test_hooks_json.sh           # Hook registration validation
│   ├── test_session_start.sh        # Session-start hook integration tests
│   ├── test_enforce_behavioral.py   # Enforcement script unit tests
│   ├── test_skills.sh               # Skill file structure validation
│   ├── test_accumulator.py          # Accumulator unit tests
│   ├── test_test_runner.py          # Test runner unit tests
│   └── test_visualizer.py           # Visualizer unit tests
│
├── docs/
│   └── behaviors/                   # Accumulated .feature files (per-project, created at runtime)
│       ├── YYYY-MM-DD-*.feature
│       └── dashboard.html           # Auto-generated overview
│
├── ARCHITECTURE.md                  # You are here
├── COMPARISON.md
├── CONTRIBUTING.md
├── INDEX.md
├── QUICKREF.md
├── README.md
├── REFERENCES.md
└── VISION.md
```

> **Note:** Users can also place a `.behavior-first-mode` file in their **project root** (not inside the plugin) to auto-activate behavioral mode on every session.

---

## Testing Strategy

### Unit Tests (for goodboy itself)
```python
def test_code_detection():
    assert contains_code("```python\nprint('hi')\n```") == True
    assert contains_code("User clicks button → System responds") == False

def test_behavioral_mapping_validation():
    incomplete_map = {"trigger": "user clicks", "outcome": None}
    assert validate_map(incomplete_map) == False
    
def test_feature_file_accumulation():
    # Ensure scenarios append correctly
    # Ensure no duplicates
    # Ensure proper Gherkin syntax
```

### Integration Tests
```python
def test_full_flow():
    """
    1. User describes behavior
    2. Agent maps it
    3. .feature file updated
    4. Tests run
    5. Results translated
    """
    
def test_hook_enforcement():
    """
    Agent tries to output code → PreToolUse denies → Agent retries behaviorally
    """

def test_skill_chaining():
    """
    behavior-translator → brainstorming → execution → back to behavior-translator
    """
```

### User Acceptance Testing
- Can non-technical user understand all output?
- Can they build a complete spec without seeing code?
- Do they know when behaviors are passing/failing?
- Can they correct the agent when it misunderstands?

---

## Performance Considerations

**The cost of verification:**
Every response now has an extra step (behavioral mapping + validation).
Expected slowdown: 10-30% longer response times.
**This is acceptable** because reliability >> speed for behavioral specs.

**Test execution:**
Run tests asynchronously where possible.
Cache step definitions to avoid regeneration.
Use test parallelization for large .feature suites.

**Visual generation:**
HTML pages are lightweight (< 100kb typically).
Mermaid renders client-side (no server load).
Dashboard updates incrementally, not full rebuild.

---

## Security & Privacy

**Code visibility:**
The .feature files are safe to share with non-technical stakeholders.
The step_definitions/ folder contains generated code — treat as sensitive.

**Test data:**
Step definitions may contain API keys, test credentials.
Never include in .feature file output.
Ensure proper .gitignore rules.

---

## Deployment Models

**Model 1: Local Claude Code Plugin**
- Install as a Claude Code plugin in `~/.claude/plugins/goodboy/`
- Runs entirely on user's machine
- No external dependencies (except test runners)

**Model 2: Shared Team Setup**
- .feature files in git repo
- Team members can all describe behaviors
- Agent reconciles across conversations

**Model 3: Standalone Tool**
- Generic "behavior-first agent" framework
- Integrate with any AI agent system

---

## Future Extensions

**Multi-agent collaboration:**
- Different agents for different behavioral domains
- Product agent vs Engineering agent with shared .feature contract

**Behavior evolution tracking:**
- Git history of .feature files shows how product evolved
- "Show me how login behavior changed over time"

**Behavioral regression detection:**
- Previously passing behavior now fails → alert stakeholders
- "Payment confirmation behavior broke in last deploy"

**Natural language queries:**
- "Show me all behaviors related to subscriptions"
- "What happens when payment fails?"
- Agent reads .feature files to answer

---

## Success Metrics

**Adoption:**
- Number of .feature scenarios created by non-technical users
- Time to create first complete behavioral spec
- Ratio of behavioral conversations vs code-showing conversations

**Quality:**
- Test coverage achieved through behavioral descriptions
- Number of bugs caught before coding via behavioral mapping
- Stakeholder confidence in understanding system behavior

**Efficiency:**
- Time saved in behavioral specification vs traditional BDD
- Reduction in "wait, what's supposed to happen here?" questions
- Faster alignment between product and engineering

---

*Architecture evolves as we build. This is the starting point, not the final form.*
