# Changelog

All notable changes to goodboy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-03-14

### Added
- Core `behavior-translator` skill with HARD-GATE verification
- `being-a-goodboy` meta-skill for activation and session management
- PreToolUse hook enforcement (`enforce-behavioral.py`)
- UserPromptSubmit hook for natural language activation
- SessionStart hook for auto-activation via `.behavior-first-mode` file
- Cross-platform hook wrapper (`run-hook.cmd`)
- Feature file accumulator (`accumulator.py`)
- Silent test runner with behavioral result translation (`test_runner.py`)
- HTML visualizer with Mermaid diagrams (`visualizer.py`)
- Shared utilities module (`utils.py`)
- Comprehensive test suite (99 tests across 8 suites)
- Full documentation: README, ARCHITECTURE, VISION, QUICKREF, COMPARISON, REFERENCES, INDEX
- Plugin marketplace configuration for distribution
- Slash commands: `/goodboy-status`, `/goodboy-activate`, `/goodboy-dashboard`
