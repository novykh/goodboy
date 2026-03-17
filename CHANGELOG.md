# Changelog

All notable changes to goodboy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-03-17

### Added
- 7 hook types: PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, Stop, SubagentStop, PreCompact
- Behavior-first mode gate on all hooks (only active when `.behavior-first-mode` exists)
- Markdown auto-translate: `.md` files with code are allowed but trigger behavioral translation
- Feature file quality gate: validates Gherkin structure before saving `.feature` files
- Bash output translator: reminds agent to translate technical output
- Behavioral question reframer: detects technical language in user prompts
- Session stop summary: reports saved behaviors at session end
- Subagent output translator: ensures subagent results are behavioral
- PreCompact context preserver: saves confirmed behaviors before compression
- Multi-platform support: Cursor, Codex, OpenCode, Gemini CLI
- Agents: behavioral-reviewer, feature-reviewer
- CLI visualization toolkit: flows, trees, tables, funnels, timelines, state diagrams
- 3-phase gated workflow with TaskCreate tracking (Map → Confirm → Save)
- 135 tests across 9 suites

### Changed
- Behavior-translator workflow: 11-step checklist → 3-phase gated workflow
- Feature files now save to `docs/goodboy/behaviors/`
- Dashboard now saves to `docs/goodboy/dashboard.html`
- Commands renamed: `start`, `dashboard`, `status`
- README rewritten to match v0.2 reality (no test execution claims)

### Removed
- Unused settings (goodboy.mode, goodboy.autoActivate, etc.)
- False test execution claims from README and docs

## [0.1.0] - 2026-03-14

### Added
- Core `behavior-translator` skill with HARD-GATE verification
- `being-a-goodboy` meta-skill for activation and session management
- PreToolUse hook enforcement (`enforce-behavioral.py`)
- SessionStart hook for auto-activation via `.behavior-first-mode` file
- Cross-platform hook wrapper (`run-hook.cmd`)
- Feature file accumulator (`accumulator.py`)
- Silent test runner with behavioral result translation (`test_runner.py`)
- HTML visualizer with Mermaid diagrams (`visualizer.py`)
- Shared utilities module (`utils.py`)
- Comprehensive test suite
- Full documentation: README, ARCHITECTURE, VISION, QUICKREF, COMPARISON, REFERENCES, INDEX
- Plugin marketplace configuration for distribution
- Slash commands: `/goodboy-status`, `/goodboy-activate`, `/goodboy-dashboard`
