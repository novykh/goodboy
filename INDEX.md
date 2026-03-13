# goodboy 🐕

**Talk to AI agents about behavior, not code.**

---

## 📚 Documentation Index

**Start here:**
- **[README.md](README.md)** — What is this? Why should I care? (5 min read)
- **[QUICKREF.md](QUICKREF.md)** — Quick reference for daily use (bookmark this!)

**Deep dives:**
- **[VISION.md](VISION.md)** — Complete project vision, philosophy, roadmap (20 min read)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Technical architecture and implementation (15 min read)
- **[COMPARISON.md](COMPARISON.md)** — How we compare to other tools (10 min read)
- **[REFERENCES.md](REFERENCES.md)** — All key references and strong points (10 min read)

---

## 🎯 Quick Links by Audience

### I'm a Product Manager / Non-Technical Stakeholder
1. Read: [README.md](README.md) — See what this does for you
2. Read: [QUICKREF.md](QUICKREF.md) — Learn the patterns
3. Try: Start describing features using the activation phrase
4. Bookmark: [COMPARISON.md](COMPARISON.md) — See how this differs from Jira/Confluence

### I'm a Developer
1. Read: [README.md](README.md) — Understand the value prop
2. Read: [ARCHITECTURE.md](ARCHITECTURE.md) — See how it works technically
3. Read: [COMPARISON.md](COMPARISON.md) — How this compares to other tools
4. Contribute: Check the roadmap in [VISION.md](VISION.md)

### I'm a BDD Expert / QA Lead
1. Read: [COMPARISON.md](COMPARISON.md) — See our take on BDD's promises
2. Read: [ARCHITECTURE.md](ARCHITECTURE.md) — Review our Gherkin generation approach
3. Feedback: Are we generating good .feature files?
4. Contribute: Help us improve behavioral patterns

### I'm an AI Agent Framework Maintainer
1. Read: [VISION.md](VISION.md) — The behavioral verification pattern
2. Read: [ARCHITECTURE.md](ARCHITECTURE.md) — Hook-based enforcement
3. Read: [COMPARISON.md](COMPARISON.md) — How this could integrate with your framework
4. Collaborate: Could this work with AutoGen/CrewAI/LangChain?

### I'm Curious About the Space
1. Read: [README.md](README.md) — Get oriented
2. Read: [REFERENCES.md](REFERENCES.md) — See the landscape and our positioning
3. Read: [VISION.md](VISION.md) — Understand why this matters now

---

## ⚡ The 60-Second Version

**Problem:** AI agents show code to non-technical users. BDD tools promised to fix this but still require learning Gherkin syntax.

**Solution:** goodboy uses AI as the translator. You describe behavior naturally, the agent maps it visually, and your conversation becomes executable tests.

**How:** 
1. **Enforcement layer** (hooks block code output mechanically)
2. **Verification layer** (agent must map behaviorally before responding)
3. **Accumulation layer** (.feature files grow with every confirmed behavior)

**Built with:** Claude Code's hook and plugin system

**Status:** Planning → MVP Development

**Try it:** Open your terminal, run `claude`, and say `> You are a goodboy and I don't know code.`

---

## 📂 File Structure

```
goodboy/
├── README.md              ← Start here
├── QUICKREF.md            ← Daily reference
├── VISION.md              ← Complete vision
├── ARCHITECTURE.md        ← Technical details
├── COMPARISON.md          ← vs. other tools
├── REFERENCES.md          ← Key references & strong points
├── CONTRIBUTING.md        ← How to contribute
├── CHANGELOG.md           ← Version history
├── INDEX.md               ← You are here
├── CLAUDE.md              ← Claude Code project context
├── LICENSE                ← MIT license
├── marketplace.json       ← Plugin marketplace manifest
├── settings.json          ← Plugin default settings
│
├── .claude-plugin/
│   └── plugin.json        # Plugin manifest (source of truth)
│
├── hooks/                 # Claude Code plugin hooks
│   ├── hooks.json         # Hook registration (PreToolUse, SessionStart, UserPromptSubmit)
│   ├── run-hook.cmd       # Cross-platform polyglot wrapper
│   ├── session-start      # SessionStart: load context, detect .behavior-first-mode
│   └── scripts/
│       └── enforce-behavioral.py  # PreToolUse: block code output
│
├── skills/
│   ├── being-a-goodboy/
│   │   └── SKILL.md       # Meta-skill: activation, session rules, skill priority
│   └── behavior-translator/
│       ├── SKILL.md        # Main skill definition (HARD-GATE)
│       ├── accumulator.py  # Feature file accumulator
│       ├── test_runner.py  # Silent test runner & result translation
│       ├── visualizer.py   # HTML visualizer (diagrams, dashboard)
│       ├── utils.py        # Shared utilities (slugify, escape_html)
│       └── references/     # Word-flow patterns, templates, styles
│
├── commands/              # Slash commands
│   ├── goodboy-status.md
│   ├── goodboy-activate.md
│   └── goodboy-dashboard.md
│
├── tests/
│   ├── run-all.sh              # Top-level test runner
│   ├── test_plugin_json.sh     # Plugin manifest tests
│   ├── test_hooks_json.sh      # Hook registration tests
│   ├── test_session_start.sh   # Session-start hook tests
│   ├── test_enforce_behavioral.py  # Enforcement script tests
│   ├── test_skills.sh          # Skill file validation
│   ├── test_accumulator.py     # Accumulator tests
│   ├── test_test_runner.py     # Test runner tests
│   └── test_visualizer.py      # Visualizer tests
│
└── docs/
    └── behaviors/          (Your .feature files will go here)
```

---

## 🚀 Get Started

### If you're ready to try it:
```bash
# Inside Claude Code:
/plugin marketplace add novykh/goodboy
/plugin install goodboy@novykh

# Activate:
> You are a goodboy and I don't know code.
```

### If you want to understand it first:
1. [README.md](README.md) — See real examples
2. [QUICKREF.md](QUICKREF.md) — Learn the patterns
3. [VISION.md](VISION.md) — Understand the philosophy

---

## 🎬 Project Status

| Phase | Status | Timeline |
|-------|--------|----------|
| **Planning & Documentation** | ✅ Complete | Week 0 |
| **Core Skill Development** | ✅ Complete | Week 1-2 |
| **Hook Enforcement** | ✅ Complete | Week 1-2 |
| **Test Integration** | ✅ Complete | Week 2-3 |
| **Visual Output** | ✅ Complete | Week 3-4 |
| **Plugin Marketplace Release** | 📋 Planned | Week 4 |
| **User Testing** | 📋 Planned | Week 5 |
| **Open Source Release** | 📋 Planned | Week 6 |

---

## 💡 Key Insights

### The Problem is Real
- Every AI agent framework assumes technical users
- Product managers can't effectively use AI agents
- BDD tools failed to deliver on their promise

### The Solution is Unique
- First tool with mechanical enforcement (not just prompts)
- First to use AI as the BDD translator
- First to combine behavioral verification + visual output + living specs

### The Timing is Perfect
- Agent frameworks maturing (2024-2025)
- MCP standardizing tool integration
- Nobody solving the non-technical user problem

### The Integration is Clean
- Built on proven infrastructure (Claude Code hooks + plugin system)
- Extends, doesn't replace existing tools
- Two tracks (behavioral + technical) sharing one codebase

---

## 🔗 External Resources

### Claude Code Infrastructure
- [Claude Code Hooks](https://code.claude.com/docs/en/hooks) — Official documentation

### Inspiration
- [obra/superpowers](https://github.com/obra/superpowers) — Skill-based agent framework (inspiration for skill architecture)
- [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — Visual output patterns
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) — Hook examples

### Context
- Cucumber, SpecFlow, Behave — Traditional BDD tools
- AutoGen, CrewAI, LangChain — Multi-agent frameworks
- LangSmith, Langfuse — Agent observability tools

---

## 🤝 Contributing

We need help from:
- **Non-technical testers** — Can you actually use this without frustration?
- **BDD experts** — Is our Gherkin generation sound?
- **Visual designers** — Make the HTML output stunning
- **Framework maintainers** — Want to integrate with other agent frameworks?

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📬 Stay Updated

- **GitHub:** Watch this repo for updates
- **Issues:** Report bugs, request features
- **Discussions:** Share usage patterns, integration ideas

---

## 📄 License

MIT — Use this however you want. We're trying to make AI accessible to more people.

---

## 🎯 Remember

**You're not learning to code. You're learning to describe behavior clearly.**

The agent handles everything else:
- Translation to code ✓
- Test generation ✓
- Execution ✓
- Verification ✓

You just describe what should happen.

---

*Built with ❤️ for everyone who's ever said "I don't know code" and felt locked out of the AI agent revolution.*

**Let's bridge that gap together. 🐕**
