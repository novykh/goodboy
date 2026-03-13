# Contributing to goodboy 🐕

Thanks for your interest in making AI agents accessible to non-technical users!

---

## How You Can Help

### Non-Technical Testers

The most valuable contribution right now is **real usage feedback**. Can you actually describe system behavior and get useful results without seeing code?

1. Install goodboy (see [README.md](README.md))
2. Try describing behaviors for a real project
3. Open an issue with what worked, what was confusing, and what broke

### BDD Experts

We generate Gherkin `.feature` files from natural conversation. We need feedback on:

- Are the generated scenarios well-structured?
- Do the step definitions follow best practices?
- What patterns are we missing?

### Developers

Pick up any item from the [roadmap](VISION.md) or check open issues.

**Areas that need work:**

- Hook scripts (`hooks/scripts/`) — enforcement and detection logic
- Skill definitions (`skills/behavior-translator/`) — HARD-GATE patterns
- HTML generation — Mermaid diagram templates, auto-refresh
- Test runner integration — Cucumber/Behave step definition generation

### Visual Designers

The HTML output (behavioral maps, dashboards, expected-vs-actual views) should be **beautiful and immediately understandable**. Help us make it better.

---

## Development Setup

```bash
git clone https://github.com/novykh/goodboy.git
cd goodboy

# Test locally without installing
claude --plugin-dir .

# Run the test suite
bash tests/run-all.sh

# Or run individual Python test suites
python3 tests/test_enforce_behavioral.py
python3 tests/test_accumulator.py
python3 tests/test_test_runner.py
python3 tests/test_visualizer.py

# After making changes, reload inside Claude Code
/reload-plugins

# Validate your changes
/plugin validate .

# Test hook enforcement manually
echo '{"tool_name": "Write", "tool_input": {"content": "import os"}}' | python3 hooks/scripts/enforce-behavioral.py
```

---

## Submitting Changes

1. Fork the repo
2. Create a feature branch (`git checkout -b my-feature`)
3. Make your changes
4. Run tests to make sure nothing broke
5. Open a pull request with a clear description of what you changed and why

---

## Code of Conduct

Be respectful. We're trying to make AI accessible to more people. Keep that mission in mind.

---

## Questions?

Open a GitHub issue or start a Discussion. We're happy to help you get oriented.
