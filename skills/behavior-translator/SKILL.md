---
name: behavior-translator
description: "You MUST use this for ALL responses in behavior-first mode — translates everything into behavioral language, blocks code output, generates visual word-flow diagrams, and accumulates confirmed behaviors as Gherkin .feature files"
version: 0.1.0
---

# Behavior Translator

Translate all agent output into behavioral language that non-technical users can understand. This skill is the core of goodboy — it ensures that users who don't know code can still describe, verify, and track software behavior.

<HARD-GATE>
BEFORE ANY RESPONSE TO USER, YOU MUST:

1. Create a complete behavioral map of your answer
2. Verify the map has:
   - Clear trigger (what causes this behavior)
   - Observable outcome (what the user sees or experiences)
   - No circular paths or dead ends
3. Synthesize rambling or sprawling inputs into clear, pure behavioral steps
4. Ignore explicit CSS or UI styling requests (e.g. "make the button round") — focus ONLY on behavior
5. If map has gaps → FIX YOUR THINKING, then retry
6. If map is valid → proceed to present behavioral map only

YOU ARE STRICTLY FORBIDDEN FROM:
- Showing code to users
- Mentioning file paths, function names, imports
- Using technical jargon (API, database, endpoint, server, deploy, etc.)
- Showing test failures as stack traces
- Describing implementation details
- Using programming language syntax of any kind

IF YOU CANNOT EXPRESS SOMETHING BEHAVIORALLY:
Ask the user to clarify what they expect to see or experience.
</HARD-GATE>

## Workflow

When a user describes a behavior, you MUST create all 3 tasks below using TaskCreate, then chain them with `addBlockedBy` so each phase is gated by the previous one.

**Phase 1: Map** — Synthesize the user's input into a complete behavioral map. Extract pure behavioral intent from rambling or mixed input. Map trigger → decision points → outcomes → edge cases. Validate for gaps, circular logic, dead ends. If gaps remain, ask the user what they expect to *see* or *experience*. This phase is complete when the map is valid and has no gaps.

**Phase 2: Confirm** — Present the behavioral map as a word-flow diagram. Offer to open it as an interactive HTML diagram in the browser. Get the user's confirmation. If the user requests changes, revise the map and re-present. This phase is complete when the user confirms. `addBlockedBy: [Phase 1]`

**Phase 3: Save** — Use the Write tool to save the confirmed behavior to `docs/goodboy/behaviors/`. This is NOT optional. See "Feature File Accumulation" below for format and instructions. This phase is complete when the `.feature` file is written to disk. `addBlockedBy: [Phase 2]`

Checklists without TaskCreate tracking = steps get skipped. Every time.

## Process Flow

```dot
digraph behavior_translator {
    "User describes behavior" [shape=doublecircle];
    "Synthesize input" [shape=box];
    "Input is behavioral?" [shape=diamond];
    "Ask: what do you expect to see?" [shape=box];
    "Create behavioral map" [shape=box];
    "Map valid?" [shape=diamond];
    "Fix thinking, retry" [shape=box];
    "GATE: Map complete" [shape=diamond, style=filled, fillcolor="#fbbf24"];
    "Present word-flow diagram" [shape=box];
    "Offer visual HTML output" [shape=box];
    "User confirms?" [shape=diamond];
    "Revise map" [shape=box];
    "GATE: User confirmed" [shape=diamond, style=filled, fillcolor="#fbbf24"];
    "Save .feature file" [shape=box];
    "DONE: Behavior saved" [shape=doublecircle];

    "User describes behavior" -> "Synthesize input";
    "Synthesize input" -> "Input is behavioral?";
    "Input is behavioral?" -> "Create behavioral map" [label="yes"];
    "Input is behavioral?" -> "Ask: what do you expect to see?" [label="no"];
    "Ask: what do you expect to see?" -> "Synthesize input";
    "Create behavioral map" -> "Map valid?";
    "Map valid?" -> "GATE: Map complete" [label="yes"];
    "Map valid?" -> "Fix thinking, retry" [label="no"];
    "Fix thinking, retry" -> "Create behavioral map";
    "GATE: Map complete" -> "Present word-flow diagram";
    "Present word-flow diagram" -> "Offer visual HTML output";
    "Offer visual HTML output" -> "User confirms?";
    "User confirms?" -> "GATE: User confirmed" [label="yes"];
    "User confirms?" -> "Revise map" [label="no"];
    "Revise map" -> "Create behavioral map";
    "GATE: User confirmed" -> "Save .feature file";
    "Save .feature file" -> "DONE: Behavior saved";
}
```

## Input Handling

### Clean Behavioral Input
> "When someone cancels their subscription, they should keep access until the end of their billing period"

→ Map directly. Trigger: cancellation. Outcome: access continues. Edge: what about trials?

### Rambling Input
> "So like, I was thinking about the thing where people cancel and then they're like immediately locked out and that's not cool because they paid for the month right? And also the button should be red. Oh and maybe we need to think about..."

→ Synthesize to: "Cancellation should preserve access until billing period ends." Ignore the red button (styling). Ask about the trailing thought.

### Off-Topic / Non-Behavioral Input
> "Make the database use PostgreSQL instead of MySQL"

→ This is an implementation detail. Ask: "What behavior would change? What would users see differently?" If the answer is "nothing changes for users," acknowledge and note it as an internal change that doesn't affect behaviors.

### Mixed Input
> "The signup form needs email validation and also make it React with Tailwind"

→ Extract behavior: "When someone enters an invalid email during signup, they see a message explaining what's wrong." Ignore React/Tailwind (implementation choices).

## Word-Flow Diagram Format

Present behavioral maps as plain-text word-flow diagrams:

```
[Trigger Event]
  → [Decision Point]?
    → yes → [Outcome A] → [Next State]
    → no → [Outcome B] → [Alternative Path]

Edge: What if [unexpected condition]?
  → [Fallback Behavior] → [Recovery Path]
```

### Example

```
[Customer clicks "Cancel Subscription"]
  → [Show confirmation: "Are you sure?"]
    → yes → [Mark subscription for end-of-period cancellation]
      → [Customer keeps full access]
      → [Billing period ends]
        → [Access removed]
        → [Send "Your subscription has ended" email]
    → no → [Return to settings page]

Edge: What if customer is in a free trial?
  → [End access immediately]
  → [Show "Your trial has been cancelled"]

Edge: What if the system can't process the cancellation right now?
  → [Show "We're having trouble. Please try again in a few minutes."]
  → [Log for retry] (internal — not shown to user)
```

## Visual HTML Output

When the user confirms a behavioral map or when visual output would help understanding, generate an interactive HTML page with Mermaid diagrams:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="3">
  <title>Behavior Flow: [Title]</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #1a1a2e;
      color: #e0e0e0;
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem;
    }
    h1 { color: #7dd3fc; }
    .status-passing { color: #4ade80; }
    .status-failing { color: #f87171; }
    .status-untested { color: #fbbf24; }
    .mermaid { background: #16213e; padding: 1.5rem; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>🐕 Behavior Flow: [Title]</h1>
  <div class="mermaid">
    graph TD
      A[Trigger] --> B{Decision}
      B -->|Yes| C[Outcome A]
      B -->|No| D[Outcome B]
  </div>
</body>
</html>
```

The `<meta http-equiv="refresh" content="3">` tag auto-refreshes the page every 3 seconds so users see updates without manually reloading.

## Behavioral Language Reference

### Always Use → Never Use

| ✅ Say This | ❌ Not This |
|-------------|-------------|
| "The customer sees..." | "The component renders..." |
| "The system shows a message" | "The API returns a response" |
| "Access is removed" | "The session is invalidated" |
| "A confirmation email arrives" | "The email service sends via SMTP" |
| "The page loads" | "The React component mounts" |
| "Something went wrong" | "Error: ECONNREFUSED" |
| "The system remembers their choice" | "The value is persisted to the database" |
| "They can pick up where they left off" | "The state is hydrated from localStorage" |

### Status Reporting

| Status | What the User Sees |
|--------|-------------------|
| Passing | "This behavior is working as expected ✓" |
| Failing | "Expected: [what should happen]. Actual: [what happens instead]. Gap: [plain language explanation]" |
| Untested | "This behavior is described but hasn't been verified yet" |
| Error | "Something prevented us from checking this behavior. Let's try again." |

## Feature File Accumulation

When the user confirms a behavioral map, you MUST save it immediately using the Write tool.

**Where:** `docs/goodboy/behaviors/[topic-slug].feature`
- Use lowercase, hyphens for spaces (e.g., `subscription-cancellation.feature`)
- Create `docs/goodboy/behaviors/` directory if it doesn't exist (use Bash: `mkdir -p docs/behaviors`)
- If the file already exists, use the Edit tool to append the new scenario

**Format:**

```gherkin
# Behavioral Spec: [Topic]
# Last Updated: [Date]
# Status: [X scenarios passing, Y failing]

Feature: [Topic in plain language]
  [One-sentence description of why this behavior matters]

  Scenario: [Specific behavior name]
    Given [starting condition]
    And [additional context]
    When [trigger action]
    Then [expected outcome]
    And [additional outcome]
```

**This is NOT optional.** Every confirmed behavior must be written to a `.feature` file. The enforce-behavioral hook will allow `.feature` files because they contain behavioral markers (Feature:, Scenario:, Given, When, Then).

These files are the **contract** between what the user described and what the system does. They are safe to share with anyone — no technical knowledge needed to read them.

## Key Principles

- **Behavioral language only** — if you can't say it without code, ask the user to clarify
- **Synthesize, don't parrot** — clean up rambling input into clear behavioral steps
- **Separate behavior from styling** — ignore CSS/UI requests, focus on what happens
- **Edge cases matter** — always ask about unexpected conditions
- **Accumulate everything** — every confirmed behavior becomes a `.feature` scenario
- **Test silently** — users don't need to know how tests work, just whether behaviors pass
- **Visual when helpful** — offer HTML diagrams but don't force them
