# CLAUDE.md

This is goodboy, a behavior-first Claude Code plugin.

## Project Structure
- `skills/` — Claude Code skill definitions (SKILL.md files)
- `hooks/` — PreToolUse, UserPromptSubmit, SessionStart hooks
- `tests/` — Bash and Python test suites
- `.claude-plugin/plugin.json` — Plugin manifest (source of truth for version)

## Testing
Run all tests: `bash tests/run-all.sh`
Python tests: `python3 tests/test_enforce_behavioral.py`

## Key Conventions
- All hook scripts use Python 3.8+
- Hook scripts communicate via JSON on stdin/stdout
- Exit code 0 = allow, exit code 2 = deny (for PreToolUse hooks)
- `.claude-plugin/plugin.json` is the plugin manifest (source of truth)
- Behavioral language only in user-facing output
- Gherkin .feature files go in `docs/behaviors/`

## Development
- Test locally with: `claude --plugin-dir .`
- Reload after changes: `/reload-plugins`
- Validate structure: `/plugin validate .`
