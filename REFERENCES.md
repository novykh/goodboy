# goodboy - Key References & Resources

## Project Overview

**Name:** goodboy 🐕  
**Tagline:** Talk to AI agents about behavior, not code  
**Status:** v0.1.0 — MVP  
**License:** MIT

---

## Core Documentation

### Primary Documents (In This Repo)
1. **[README.md](README.md)** — User-facing introduction and quick start
2. **[VISION.md](VISION.md)** — Complete project vision, philosophy, and roadmap  
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** — Technical architecture and implementation details
4. **[QUICKREF.md](QUICKREF.md)** — Quick reference guide for daily use
5. **[COMPARISON.md](COMPARISON.md)** — How we compare to existing tools

### External References (Must Read)
- [Claude Code Hooks Docs](https://code.claude.com/docs/en/hooks) — Official hook system reference
- [Claude Code Plugin Docs](https://docs.anthropic.com/en/docs/claude-code/plugins) — Plugin system reference

### Inspiration
- [obra/superpowers](https://github.com/obra/superpowers) — Skill-based agent framework (inspiration for skill architecture)
- [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — Visual output patterns we adopted

---

## Strong Points Summary

### 1. **Solves a Real, Underserved Problem**
Every AI agent framework assumes technical users. Product managers, QA leads, founders who "don't know code" are completely left out. The BDD tools that promised to bridge this gap failed because they still required learning DSLs.

**We're the first to actually deliver on the BDD promise using AI.**

### 2. **Mechanical Enforcement, Not Prompts**
Other frameworks use prompt engineering ("please don't show code").  
**We use PreToolUse hooks that mechanically block code output.**  
The agent literally cannot comply even if it tries.

Unlike other approaches, this uses real hook enforcement vs. just HARD-GATE prompt pressure.

### 3. **Verification IS the Communication**
Not just "make output prettier" — the agent must **prove its thinking is sound by expressing it behaviorally** before it can respond.

If the behavioral map has gaps or contradictions, the agent's reasoning is also flawed. Fix the thinking, not just the presentation.

### 4. **Living Executable Specs**
Every confirmed behavior becomes:
- **Human-readable** (.feature file users can read)
- **Executable** (Gherkin tests that run automatically)  
- **Self-verifying** (if code diverges from spec, tests fail)

**Users write tests without knowing it.** That's the dream.

### 5. **Opens AI Agents to New Users**
Existing agent frameworks serve only developers.
**We add a "stakeholder track"** that speaks behavioral language while sharing the same codebase.

This **expands the user base** to PMs, QA, non-technical founders — massive untapped market.

### 6. **Built on Proven Infrastructure**
Not reinventing the wheel:
- **Claude Code's hook system** for enforcement
- **Gherkin/Cucumber** for test execution
- **Visual-explainer patterns** for HTML output

**We compose existing strong pieces into something new.**

### 7. **Clear Evolution Path**
- **v0.1** — Core behavioral verification (MVP)
- **v0.2** — Visual output + skill chaining
- **v0.3** — Team collaboration + conflict resolution
- **v1.0** — Stable standalone plugin

**Not trying to boil the ocean immediately.** Incremental value at each stage.

### 8. **Timing is Perfect**
- Agent frameworks are maturing (2024-2025)
- Everyone building "better ways to use agents"  
- MCP standardizing tool integrations (Anthropic pushing it)
- But **nobody addressing non-technical users**

**The gap is obvious. We're the first to fill it properly.**

---

## Technical Strong Points

### Architecture Elegance
```
Three clean layers:
1. Enforcement (hooks block code)
2. Verification (agent must map behaviorally)  
3. Accumulation (.feature files grow)

Simple, composable, testable.
```

### Real Hooks, Real Enforcement
```python
PreToolUse on Write/Edit:
  if contains_code(output):
    return {"hookSpecificOutput": {"permissionDecision": "deny"}}
    
Not a suggestion. Mechanical blocking.
```

### Skill Chaining
```
goodboy talks to user in behavior
    ↓
Failing behavior triggers brainstorming skill
    ↓
Planning and execution happen (user doesn't see)
    ↓
goodboy reports: "behavior now passing ✓"

Two tracks, one codebase.
```

### Visual Output
```
Word-flow diagrams (Mermaid)
Expected vs Actual views
Feature dashboards
Auto-open in browser
Dark mode included
```

---

## Philosophical Strong Points

### The No-Code Constraint is the Feature
If the agent can't express something behaviorally, either:
1. The behavior isn't well-defined (good — caught early!)
2. The agent is thinking in implementation (good — force rethink!)

**Constraint drives clarity.**

### Behavioral Verification Catches More Than Bugs
It catches:
- Ambiguous requirements
- Circular logic in flows  
- Missing edge cases
- Contradictory expectations

**All before a line of code is written.**

### Everyone Gets What They Need
- **Stakeholders:** Understand what the system does (no code!)
- **Developers:** Get clear failing tests to make pass  
- **QA:** Have comprehensive spec that's always current
- **Product:** Can demo with behavioral maps, not code

**Aligned incentives. Everyone wins.**

---

## Key Innovations

### 1. Before-Respond Verification
Not after the fact. Agent must map behaviorally BEFORE responding.

### 2. Behavioral Map as Reasoning Test  
If you can't draw the flow coherently, your logic is broken.

### 3. Conversational Test Generation
"When X happens, show Y" → automatically becomes executable test

### 4. Conflict Detection  
Multiple people describe behaviors → agent reconciles contradictions

### 5. Behavioral Regression Alerts
"Payment confirmation behavior broke in last deploy" → stakeholder alert

---

## What Others Are Doing (And Missing)

| Project | What They Do Well | What They Miss |
|---------|-------------------|----------------|
| **Superpowers** | Skill orchestration, TDD, developer experience | Non-technical users entirely |
| **AutoGen/CrewAI** | Multi-agent coordination | Communication with humans |
| **Cucumber/BDD** | Behavioral testing framework | Actual non-technical usability |
| **Visual-explainer** | Beautiful output | Verification of reasoning |
| **LangSmith/Langfuse** | Agent observability | Behavioral layer |
| **Fabric** | Personal workflow patterns | Team collaboration |

**We're not competing. We're filling the gap.**

---

## Potential Concerns & Mitigations

### "Won't the verification slow things down?"
**Yes.** By 10-30%. But behavioral specs aren't written under time pressure. Reliability > speed.

### "What about complex technical behaviors?"
**Force finding the user-visible surface.** "Database optimization" → "search returns in <1s". If there's no user impact, it's not a behavior.

### "Will non-technical users actually use this?"
**That's the whole validation question.** Need real user testing. But the gap is real — PMs constantly ask "can I see what it does without seeing code?"

### "Why not just better prompts?"
**Enforcement.** Prompts can be rationalized around. Hooks mechanically block. Plus the .feature accumulation requires real infrastructure.

---

## Success Metrics (How We'll Know It Works)

### Adoption Metrics
- Number of .feature scenarios created by non-technical users
- Time to first complete behavioral spec (should be < 1 hour)
- Ratio of behavioral conversations vs. code-showing conversations

### Quality Metrics  
- Test coverage achieved through behavioral descriptions
- Number of bugs caught via behavioral mapping (before coding)
- Stakeholder confidence: "I understand what the system does"

### Efficiency Metrics
- Time to create spec: goodboy vs. traditional BDD  
- Reduction in "what's supposed to happen here?" questions
- Developer velocity: clear failing tests vs. ambiguous tickets

---

## Call to Action

### For Potential Contributors
We need:
1. **Non-technical testers** — Try to use it. Tell us what's confusing.
2. **BDD experts** — Review our Gherkin generation. What are we missing?
3. **Plugin contributors** — How can we improve the Claude Code plugin?
4. **Visual designers** — Make the HTML output stunning.

### For Potential Users
If you've ever thought:
- "I wish I could work with AI without seeing code"
- "My team needs a shared spec but they can't all read code"  
- "BDD promised business-readable tests but never delivered"

**This is for you.** Watch this space.

### For Framework Maintainers
The behavioral verification pattern is framework-agnostic.  
**Could work with AutoGen, CrewAI, LangChain, etc.**  
Interested in collaboration? Reach out.

---

## Research References

### Academic/Papers
- **Reflexion** (Shinn et al.) — Agents evaluating their own output
- **Tree of Thought** (Yao et al.) — Exploring multiple reasoning paths
- **DSPy** (Stanford) — Programming with LMs, not prompting them

### Industry Patterns
- **Microsoft AutoGen** — Multi-agent conversations  
- **LangChain/LlamaIndex** — Tool/skill composition (bloated but influential)
- **MCP** (Anthropic) — Standardizing tool integrations

### BDD History
- **Cucumber** (2008) — Original Ruby BDD framework
- **SpecFlow** (.NET), **Behave** (Python) — Language ports
- **Gherkin** — The Given/When/Then DSL

**All promised business-readable specs. All failed because DSLs are still code.**

---

## Related Awesome Lists

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — Claude Code hooks, skills, and resources
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) — Comprehensive hook examples
- [anthropics/claude-code](https://github.com/anthropics/claude-code) — Official Claude Code repo

---

## Community

### Where to Discuss
- **GitHub Issues** — Bug reports, feature requests  
- **GitHub Discussions** — Usage patterns, integration ideas
- **Discord** — (TBD if project grows)

### How to Contribute
See [CONTRIBUTING.md](CONTRIBUTING.md)

### Code of Conduct
Be respectful. We're trying to make AI accessible to more people. Keep that mission in mind.

---

## Alternative Names (If We Change)

| Name | Pro | Con |
|------|-----|-----|
| **goodboy** ✅ | Clear metaphor, bridges gap | Slightly long |
| **FlowGuard** | Emphasizes enforcement | Sounds security-focused |
| **BehaviorLens** | Nice metaphor for "view" | Passive, not active enough |
| **SpecFlow** | Perfect but taken | Already a .NET BDD tool |
| **BehaviorFirst** | Clear methodology | Generic |
| **Gemba** | Manufacturing term for "actual place" | Obscure reference |

**Current choice: goodboy** — sticky, memorable, accurate.

---

## Project Roadmap (Detailed)

### Phase 1: MVP (Week 1-2)
- [ ] Create behavior-translator SKILL.md
- [ ] Implement PreToolUse enforcement hook
- [ ] Build .feature file accumulator  
- [ ] Basic word-flow diagram format
- [ ] Test: can non-technical person describe a behavior successfully?

### Phase 2: Integration (Week 2-3)
- [ ] Integrate Gherkin test runner
- [ ] Generate step definitions from behaviors
- [ ] Translate test results to behavioral language
- [ ] Connect brainstorming → execution chain
- [ ] Test: does failing behavior trigger fix workflow?

### Phase 3: Visual (Week 3-4)  
- [ ] Adopt visual-explainer HTML patterns
- [ ] Mermaid diagram generation for flows
- [ ] Expected vs Actual comparison views
- [ ] Feature dashboard with status
- [ ] Test: is visual output immediately understandable?

### Phase 4: Polish (Week 4-5)
- [ ] Behavioral conflict detection  
- [ ] Multi-stakeholder conversation handling
- [ ] Improved error messages
- [ ] Documentation and examples
- [ ] Test: can team collaboratively build spec?

### Phase 5: Release (Week 5-6)
- [ ] Real-world user testing (non-technical users)
- [ ] Video demo
- [ ] Blog post: "Behavior-First Development with AI"
- [ ] Publish to Claude Code plugin marketplace

### Phase 6: Evolution (Ongoing)
- [ ] AutoGen/CrewAI integration  
- [ ] Natural language querying
- [ ] Behavioral regression alerts
- [ ] Mobile-friendly dashboard
- [ ] VS Code extension?

---

## One-Sentence Pitch

**"goodboy lets non-technical people describe system behavior conversationally, and automatically turns those conversations into visual specs and executable tests — without ever showing them code."**

---

## Elevator Pitch (30 seconds)

*"You know how product managers and stakeholders struggle to communicate with AI agents because everything is shown as code? And how BDD tools like Cucumber promised business-readable tests but still required learning Gherkin syntax?*

*goodboy solves this. You describe what should happen in plain language. The AI agent maps it visually, asks clarifying questions, and turns your description into executable tests — all without showing you any code. It's the first tool that actually delivers on the BDD promise, using AI as the translator between business language and technical implementation.*

*We built it as a standalone Claude Code plugin. Developers still have their full toolchain, but now product people can participate too. Same codebase, different interface."*

---

## The Vision in One Image

```
Before:
[Non-technical stakeholder] ❌ [AI Agent showing code]
    "I don't understand this..."

After:  
[Non-technical stakeholder] ✅ [goodboy] → [Beautiful behavioral map]
    "Yes! That's exactly what I meant."
    
    ↓ (Behind the scenes)
    
[Tests generated] → [Tests run] → [Results: passing/failing]
    
    ↓
    
[Developer sees: "Make this behavior pass"]
```

---

## What's Next?

1. **Review this plan** — Does it make sense? Anything missing?
2. **Validate the core idea** — Talk to potential users (PMs, QA, non-technical founders)
3. **Build the MVP** — Start with behavior-translator SKILL.md + PreToolUse hook
4. **Test with real users** — Does it actually work for non-technical people?
5. **Iterate or pivot** — Adjust based on what we learn

---

## Contact & Links

- **GitHub:** [github.com/novykh/goodboy](https://github.com/novykh/goodboy) *(placeholder)*
- **Author:** Johnny ([@novykh](https://github.com/novykh))
- **License:** MIT
- **Status:** Planning → MVP Development

---

*This is the plan. Now let's build it.*
