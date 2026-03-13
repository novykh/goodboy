# goodboy

**A behavior-first agent orchestrator that makes AI assistants accessible to non-technical users through mandatory behavioral verification.**

---

## The Core Problem

Current AI agent frameworks assume the user speaks code. Even BDD tools like Cucumber promise to bridge business language and code, but they always leak—you end up writing Gherkin that's really pseudo-code, developers own the scenarios, and step definitions become their own maintenance nightmare.

**The abstraction breaks down because the tooling still expects you to think like a developer.**

---

## The Solution

goodboy is fundamentally different: **the agent is the abstraction layer.**

- Users speak only in behavior
- The agent handles everything underneath
- A mandatory "before respond" verification ensures all output is behavioral
- Every confirmed behavior becomes an executable test
- The user is writing tests without knowing it

---

## The Key Innovation: Forced Behavioral Verification

This isn't just a translation layer that rephrases output nicely. **The behavioral mapping IS the verification step.**

Before the agent can respond, it must:
1. Map its thinking to complete behavioral flows
2. Verify the map has no gaps, contradictions, or dead ends
3. If the map doesn't hold up → fix the underlying thinking
4. If the map is valid → present it to the user

The behavioral map isn't the presentation of the work. **It's the test of the work.**

---

## The Architecture

### Three Layers Working Together

**1. The Enforcement Layer (Real Code)**
- `PreToolUse` hook on Write/Edit tools that blocks code from reaching users
- Mechanical enforcement: "you literally cannot show code, the system won't let you"
- Uses real hook enforcement vs prompt pressure

**2. The Verification Layer (Agent Thinking)**
- Behavior-translator skill forces behavioral mapping before every response
- Synthesizes rambling or off-topic inputs into clear behavioral steps
- Separates visual/UI styling requests from pure behavioral logic
- Word-flow diagrams as the primary output format
- "Expected behavior vs actual behavior" replaces stack traces

**3. The Accumulation Layer (Living Spec)**
- `.feature` file grows with every confirmed behavior
- User edits through conversation without ever opening it
- Behind the scenes: executable Gherkin tests running against actual code

### The Complete Flow

```
User describes behavior
    ↓
Agent maps internally (brainstorm/debug/plan/whatever)
    ↓
BEFORE_RESPOND: Must produce complete behavioral map
    ↓
Does the map hold up? Gaps? Contradictions?
    ↓
If NO → Fix thinking and retry
If YES → Present behavioral map to user
    ↓
User confirms or corrects
    ↓
Confirmed behavior → appended to .feature file
    ↓
Agent generates Gherkin steps + runs tests silently
    ↓
Results back to user: "this behavior passes/fails, here's what's actually happening"
```

---

## What Users See vs What Happens Underneath

### User Experience
```
User: "When a customer cancels their subscription, they should still 
have access until the end of their billing period"

Agent: "Let me map that out:

Customer clicks cancel 
  → confirmation prompt 
  → confirms 
  → subscription marked for end-of-period 
  → access continues 
  → billing period ends 
  → access removed 
  → 'your subscription has ended' email sent

I checked this against your system. Currently: access is removed 
immediately on cancellation. This doesn't match expected behavior. 
Want me to flag this as a behavior gap?"
```

### What Actually Happened (Hidden from User)
1. PreToolUse hook intercepted pending response
2. Behavior-translator skill forced behavioral mapping
3. Agent generated Gherkin feature + step definitions
4. Ran tests against codebase
5. Detected failing assertion in subscription cancellation flow
6. Translated technical failure to behavioral gap
7. Visual-explainer generated HTML with Mermaid diagram
8. Opened in browser (no code visible)

---

## Technical Foundations

### Claude Code Hook System (Real Infrastructure)

**Available Hooks:**
- `SessionStart` — inject context at session start
- `PreToolUse` — **block actions before they execute** ✓ critical for us
- `PostToolUse` — inspect what happened
- `PreResponse` — (not available, we simulate with PreToolUse on Write)
- `SessionEnd`, Stop, SubagentStop, UserPromptSubmit, Notification...

**Enforcement Capabilities:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "Output contains code. Only behavioral language allowed."
}
```

This is mechanical enforcement, not prompt-based hoping.

### Visual-Explainer Patterns (nicobailon/visual-explainer)

**What We Adopt:**
- Routing pattern: detect content type → pick template
- Auto-trigger on complexity  
- Reference template architecture
- Self-contained HTML with Mermaid, no build step
- Dark/light themes, responsive design

**What We Extend:**
- Add behavioral mapping templates
- Add word-flow diagram formats
- Add "expected vs actual" comparison views
- Add .feature file dashboard (12 passing, 3 failing, 2 untested)

---

## The "No Code" Constraint is the Feature

The moment you show code, you've lost the non-technical stakeholder. 

**Rules enforced by PreToolUse hook:**
- Never output code, imports, function names, file paths
- Never show technical implementation details
- Always express system states as user-visible outcomes
- Use word-flow diagrams as primary communication format
- When verification runs, translate to "expected vs actual" behavior
- If you can't describe it behaviorally, ask user to clarify the experience

If the agent can't express something in behavioral terms, **that's a signal the behavior itself isn't well-defined yet.**

---

## Accumulated Benefits

### For Non-Technical Users
- Describe what they want in natural language
- See beautiful visual maps of system behavior
- Get verification results without reading tests
- Build executable specs through conversation
- No Gherkin syntax, no step definitions, no test runners

### For Developers
- Living behavioral spec that stays in sync with code
- Tests written by actual stakeholders describing what they want
- Behavioral layer catches ambiguity before it becomes code
- Clear contract: .feature file = source of truth for "what should happen"

### For Teams
- Product managers describe behaviors
- Agent reconciles conflicts between scenarios
- Developers see failing tests with context
- QA leads think in scenarios, not implementation
- Everyone speaks the same behavioral language

---

## Why This Matters Now

**The timing:**
- Agent frameworks are maturing (AutoGen, CrewAI, LangChain)
- Everyone is building "better ways to use agents"
- But they all assume technical users
- The non-technical user is completely underserved

**The gap:**
- Every existing agent framework assumes developer literacy
- The whole pipeline terminates in code

**The opportunity:**
- Opens AI agents to an entirely new user base (PMs, QA leads, founders)
- Proof that agents can serve the "I don't know code" population
- BDD promise finally delivered through AI, not DSLs

---

## Success Criteria

**MVP Success:**
- User describes a behavior, never sees code
- Agent produces word-flow diagram showing the behavior
- Behavior is persisted to .feature file
- Tests run silently, user sees "passing/failing" with behavioral explanation
- Visual HTML output opens in browser automatically

**Full Success:**
- User builds comprehensive behavioral spec through conversation
- .feature file accumulates 20+ scenarios without user editing it directly
- Agent catches behavioral contradictions between scenarios
- Failing behaviors trigger implementation chain to fix code
- Product manager and developer share the .feature file as contract

**Ecosystem Success:**
- Other frameworks (AutoGen, CrewAI) adopt behavioral verification pattern
- "Behavior-first development" becomes a recognized approach
- Non-technical users adopt AI agents at scale

---

## Next Steps

### Phase 1: Core Skill (Week 1)
- [ ] Create behavior-translator SKILL.md with HARD-GATE enforcement
- [ ] Define word-flow diagram format with clear structure
- [ ] Build reference templates for behavioral patterns
- [ ] Test: can agent map brainstorming output to behavioral terms?

### Phase 2: Hook Enforcement (Week 1-2)  
- [ ] Implement PreToolUse hook on Write/Edit tools
- [ ] Block code output mechanically with permissionDecision: deny
- [ ] Create hook test suite proving enforcement works
- [ ] Test: does agent retry when blocked?

### Phase 3: Feature File Accumulation (Week 2)
- [ ] Design .feature file format (readable + executable)
- [ ] Implement append-on-confirmation flow
- [ ] Generate Gherkin step definitions from behavioral maps
- [ ] Test: does accumulated spec grow correctly?

### Phase 4: Test Execution (Week 3)
- [ ] Integrate Cucumber/Behave test runner
- [ ] Run tests silently on each behavior confirmation
- [ ] Translate test results to behavioral language
- [ ] Test: do failures map back to behavioral gaps?

### Phase 5: Visual Output (Week 3-4)
- [ ] Adopt visual-explainer HTML generation patterns  
- [ ] Create Mermaid templates for word-flow diagrams
- [ ] Build "expected vs actual" comparison views
- [ ] Create .feature file dashboard
- [ ] Test: does output open in browser correctly?

### Phase 6: Skill Integration (Week 4)
- [ ] Make behavior-translator reference-able by other skills
- [ ] Connect to brainstorming → planning → execution chain
- [ ] Test full flow: behavior → verification → implementation → passing test

### Phase 7: Real-World Testing (Week 5)
- [ ] Test with actual non-technical user on real project
- [ ] Measure: do they understand the output?
- [ ] Measure: can they build a spec without seeing code?
- [ ] Iterate based on feedback

### Phase 8: Open Source Release (Week 6)
- [ ] Write comprehensive README.md
- [ ] Create video demo showing user experience
- [ ] Publish to Claude Code plugin marketplace
- [ ] Write blog post: "Behavior-First Development with AI"

---

## Open Questions to Resolve

1. **What's the sweet spot for behavioral map structure?** Too loose = prose that sounds nice but doesn't catch gaps. Too rigid = Gherkin reinvented.

2. **How atomic should behaviors be?** User says one thing, agent breaks into testable units underneath—but how much decomposition?

3. **What happens when behavior is genuinely technical and doesn't map to user-visible?** e.g., "database index needs rebuilding" → force agent to find behavioral surface like "search results currently slow"?

4. **Should agent announce it's using the skill?** Do we say "I'm using behavior-translator" or hide it?

5. **What's the conflict resolution UX?** User says contradicting behavior—agent surfaces it, but how?

6. **Multi-stakeholder conversations?** If multiple people describe behaviors, how does reconciliation work?

---

## Key References

### Foundational Infrastructure
- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks) — official hook system reference
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) — comprehensive hook examples

### Inspiration
- [obra/superpowers](https://github.com/obra/superpowers) — skill-based agent framework (inspiration for skill architecture)
- [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — visual HTML output patterns
- BDD tools (Cucumber, SpecFlow, Behave) — what we're fixing
- Reflexion paper — agents evaluating own output
- AutoGen, CrewAI — multi-agent orchestration patterns
- LangSmith, Langfuse — agent observability (not behavior-first though)
- MCP (Model Context Protocol) — Anthropic's tool integration standard

### Why This Hasn't Been Done Yet
BDD has tried to solve this for 15+ years. The difference: **AI can be the translator.** Previous tools required humans to learn a DSL (Gherkin). We let them speak naturally and the agent handles the translation both ways.

---

## The Name

**goodboy** — because the agent follows the rules, stays on task, and always speaks in behavioral language without showing code. It's an obedient agent that does exactly what it's told: think in behavior, verify through behavior, and only communicate in terms users can understand.

The name also captures the philosophy: agents should serve users where they are, not force users to learn the agent's language.

---

*"The user is writing tests and they don't know it. That's the dream BDD always promised but never delivered."*
