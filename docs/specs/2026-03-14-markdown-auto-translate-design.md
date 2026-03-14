# Markdown Auto-Translate Hook

## Problem

When another plugin creates a document (e.g., a design spec) that contains code, non-technical users in behavior-first mode can't understand it. Currently the hook blocks the write entirely. Instead, we should allow the document through and automatically provide a BDD translation.

## Design

### Modified Hook Behavior (`enforce-behavioral.py`)

The hook gains two new capabilities:

1. **Behavior-first mode gate** — The hook checks for a `.behavior-first-mode` file in the project root. If the file doesn't exist, the hook allows everything (exit 0, no action). All enforcement only applies when the user has explicitly activated behavior-first mode.

2. **Markdown exception path** — When a Write/Edit targets a `.md` file and the content contains code:
   - Allow the write (exit 0)
   - Inject a `systemMessage` instructing the AI to immediately provide a behavioral translation of the document

### Decision Flow

```
Hook receives Write/Edit/MultiEdit
  → .behavior-first-mode file exists?
    → no → allow (exit 0, no message)
    → yes → file is .md?
      → yes → contains code?
        → no → allow (exit 0, no message)
        → yes → allow (exit 0) + inject translation message
      → no → contains code and not behavioral?
        → yes → deny (exit 2, existing behavior)
        → no → allow (exit 0)
```

### File Path Detection

The hook reads `file_path` from `tool_input` to determine if the target is a markdown file. Check for `.md` extension (case-insensitive).

### Injected System Message

When a markdown file with code is allowed through:

```
This document contains technical content (code, file paths, or implementation details).
You MUST now provide a behavioral translation of this document for the user.
Restate everything in behavioral language: what does the user SEE or EXPERIENCE?
Use the behavior-translator skill format — word-flow diagrams, no code, no jargon.
```

### Behavior-First Mode Detection

Check for `.behavior-first-mode` file relative to the working directory:
- `os.path.exists('.behavior-first-mode')` from the project root
- The file is only created when the user explicitly activates goodboy (via natural language triggers or `/goodboy-activate`)
- No auto-creation, no developer-placed flags

### What Changes

| File | Change |
|------|--------|
| `hooks/scripts/enforce-behavioral.py` | Add behavior-first mode gate, add `.md` exception path |
| `tests/test_enforce_behavioral.py` | Add tests for new paths |

### What Stays the Same

- Non-markdown code blocking (deny) when behavior-first mode is active
- Behavioral content detection logic
- Hook configuration in `hooks.json`
- All other hooks and skills
