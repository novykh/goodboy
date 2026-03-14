# goodboy 🐕

**Talk to AI agents about behavior, not code.**

goodboy makes AI assistants accessible to non-technical users by enforcing behavioral verification. You describe what should happen, the agent handles everything underneath, and every conversation becomes executable tests.

---

## The Problem

You want to work with AI agents, but:
- They show you code you don't understand
- They talk in technical jargon (APIs, endpoints, functions)
- You can't tell if they actually understood what you meant
- There's no record of what you agreed the system should do

**Current AI agent frameworks assume you speak code.** Even as a developer, this gets exhausting. For non-technical stakeholders, it's completely unusable.

---

## The Solution

goodboy adds a mandatory verification layer: **the agent can only talk to you in behavioral terms.**

```
You: "When someone cancels their subscription, they should keep 
     access until the end of their billing period."

Agent: [Shows you a visual flow diagram]
       
       Customer clicks cancel 
         → confirmation prompt 
         → confirms 
         → subscription marked for end-of-period 
         → access continues 
         → billing period ends 
         → access removed 
         → confirmation email sent

       "I checked this against your system. Currently, access 
       is removed immediately on cancellation. This doesn't 
       match expected behavior. Want me to fix it?"
```

**What just happened (behind the scenes):**
1. Agent mapped your description to behavioral flows
2. Generated executable tests  
3. Ran them against your actual codebase
4. Translated technical failures to behavioral gaps
5. Opened a beautiful HTML page in your browser (no code visible)

**You're writing tests without knowing it.** Every behavior you describe becomes automated verification.

---

## Key Features

### 🚫 No Code Zone
The agent is **mechanically prevented** from showing you code. Not "please don't" — literally can't. A PreToolUse hook blocks any output containing code syntax, file paths, or technical jargon.

If the agent can't express something behaviorally, that's a signal the behavior itself isn't well-defined yet.

### ✅ Forced Behavioral Verification  
Before the agent can respond, it must:
1. Map its thinking to complete behavioral flows
2. Check for gaps, contradictions, circular paths
3. Fix the thinking if the map doesn't hold up
4. Only then present the behavioral map to you

**The behavioral map isn't presentation — it's the test of the agent's reasoning.**

**Handling Rambling & Off-Topic Requests:**
The agent is trained to synthesize sprawling or off-topic responses, discard UI and CSS styling requests (which shouldn't be handled by the behavioral layer), and extract purely actionable behavioral logic.

### 📝 Living Behavioral Specs
Every behavior you confirm gets appended to a `.feature` file. Over time you build a complete specification through conversation, without ever editing files directly.

These aren't just docs — they're executable tests running against your code.

### 🎨 Beautiful Visual Output
No more wall of text in a terminal. Behaviors are shown as:
- **Word-flow diagrams** (Mermaid flowcharts)
- **Expected vs Actual** comparison views  
- **Feature dashboards** showing what's passing/failing

Opens automatically in your browser. Dark mode included.

### 🔗 Two Tracks, One Codebase
- When behaviors fail, the agent automatically plans and executes fixes
- Developers still have full access to code-level tools
- **Stakeholders speak behavior, developers write code, everyone's in sync**

---

## Quick Start

### Prerequisites

- Python 3.8+ (for behavioral enforcement hooks)
- Optional: [Behave](https://behave.readthedocs.io/) or [Cucumber](https://cucumber.io/) for automated test execution

### Installation

**Note:** Installation differs by platform. Claude Code and Cursor have built-in plugin marketplaces. Codex, OpenCode, and Gemini CLI require manual setup.

#### Claude Code (Marketplace)

```bash
/plugin marketplace add novykh/goodboy
/plugin install goodboy@novykh
```

Or via CLI:

```bash
claude plugin marketplace add novykh/goodboy
claude plugin install goodboy@novykh
```

#### Cursor

In Cursor Agent chat:

```text
/add-plugin goodboy
```

Or search for "goodboy" in the plugin marketplace.

#### Codex

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/novykh/goodboy/refs/heads/main/.codex/INSTALL.md
```

#### OpenCode

Tell OpenCode:

```
Fetch and follow instructions from https://raw.githubusercontent.com/novykh/goodboy/refs/heads/main/.opencode/INSTALL.md
```

#### Gemini CLI

```bash
gemini extensions install https://github.com/novykh/goodboy
```

To update:

```bash
gemini extensions update goodboy
```

### Activate

Start any conversation and say "I don't know code" to activate behavior-first mode.

Or auto-activate for a project:

```bash
touch .behavior-first-mode   # in your project root
```

### Team Installation

Share goodboy with your whole team by installing with project scope (Claude Code):

```bash
claude plugin install goodboy@novykh --scope project
```

This writes to `.claude/settings.json`, which you commit to version control.

### Local Development

```bash
git clone https://github.com/novykh/goodboy.git
claude --plugin-dir ./goodboy
```

### Your First Behavioral Conversation

```bash
# Launch Claude Code
claude

# Activate goodboy
> You are a goodboy and I don't know code.

# Describe a behavior
> When a user tries to log in with the wrong password three 
  times, they should see a "forgot password?" link.

# The agent will:
# 1. Map the behavior visually
# 2. Ask clarifying questions if needed  
# 3. Save to .feature file
# 4. Test against your code
# 5. Tell you if it passes or fails (in behavioral terms)
```

### Check Your Behavioral Specs

```bash
# View all behaviors
ls docs/behaviors/

# Open the dashboard
open docs/behaviors/dashboard.html
```

### Update

```bash
/plugin update goodboy@novykh
```

### Troubleshooting

Plugin not loading? Run `/plugin validate goodboy` or `claude --debug`.
Hooks not firing? Check `python3 --version` and script permissions.
Agent still showing code? Say "I don't know code" or run `/reload-plugins`.

---

## How It Works

### The Flow

```
User describes behavior
    ↓
Agent creates behavioral map
    ↓
[VERIFICATION CHECKPOINT]
Does the map have gaps? Contradictions? 
    ↓ YES → Fix thinking, retry
    ↓ NO  → Continue
    ↓
Show visual map to user
    ↓
User confirms or corrects  
    ↓
Append to .feature file
    ↓
Generate Gherkin tests (hidden)
    ↓
Run tests silently
    ↓
Translate results to behavioral language
    ↓
Show user: "passing" or "failing, here's the gap"
```

### The Architecture

**Three Layers:**
1. **Enforcement** — PreToolUse hooks block code from reaching you
2. **Verification** — Agent must prove its thinking via behavioral maps
3. **Accumulation** — .feature files grow with every confirmed behavior

**Behind the Scenes:**
- Your conversations happen in behavioral language
- When behaviors fail, the agent automatically plans and executes fixes
- You just see: "this behavior is now passing ✓"

---

## Use Cases

### For Product Managers
"I need to specify how the onboarding flow should work, but I don't want to write Jira tickets that get misinterpreted."

→ Describe the flow conversationally. The agent maps it, you confirm it, now engineering has an executable spec.

### For QA Leads  
"I want comprehensive test coverage but I don't want to write test code."

→ Describe scenarios as you think of them. The agent accumulates them into a test suite that runs automatically.

### For Founders
"I know what I want my product to do, but I can't communicate it to developers without them asking 100 clarifying questions."

→ Talk to the agent. It will ask the clarifying questions, capture your answers as behavioral specs, and verify the implementation matches.

### For Developers
"I'm tired of stakeholders asking to see the code, then getting confused, then saying 'that's not what I meant.'"

→ Show them the .feature file or the HTML visualizations. They can actually understand it. When they describe new behaviors, the agent writes the tests for you.

---

## Examples

### Example 1: Subscription Cancellation

**You say:**
> When customers cancel, they should keep access until their billing period ends.

**Agent shows:**
```
Customer clicks cancel 
  → confirmation: "Keep access until March 15?"
  → confirms
  → subscription marked for end-of-period
  → access continues (all features work)
  → March 15 arrives
  → access removed
  → email: "Your subscription has ended"

Currently: ✗ Failing
Access is removed immediately on cancellation.

Gap: System not checking billing_period_end before revoking access.
```

**You say:**
> Fix it.

**Agent:**
> [Does the implementation work behind the scenes]
> This behavior is now passing ✓

---

### Example 2: Password Reset Flow

**You say:**
> Show me the password reset behavior.

**Agent shows:**
```
User clicks "Forgot password"
  → enters email
  → valid email format?
    → no → "Please enter a valid email"
    → yes → "Check your email for reset link"
  → receives email within 2 minutes
  → clicks link (valid for 1 hour)
  → enters new password
  → "Password updated, you can now log in"

Currently: ✓ Passing (all steps verified)
```

---

### Example 3: Edge Case Discovery

**You say:**
> When users upload a profile photo, it should appear immediately.

**Agent:**
> Let me map that:
>
> User selects photo → uploads → processing → photo appears
>
> What should happen if:
> - The photo is too large (> 5MB)?
> - The photo isn't a valid image format?
> - The upload fails due to network issues?

**You clarify edge cases, agent adds them all to the behavioral spec.**

---

## Configuration

### Strict Mode (default)
No code, no technical terms, behavioral language only.

### Hybrid Mode  
Allow technical details if explicitly requested.  
Enable with: `> Switch to hybrid mode` during your session.

### Developer Mode
Show both behavioral AND technical views.  
Enable with: `> Switch to developer mode` during your session.

---

## Roadmap

### v0.1 (Current)
- [x] Behavioral mapping verification
- [x] PreToolUse hook enforcement
- [x] .feature file accumulation
- [x] Basic visual output
- [x] HTML dashboard with Mermaid diagrams
- [x] Plugin marketplace distribution
- [x] Slash commands (/goodboy-status, /goodboy-dashboard, /goodboy-activate)
- [x] Multi-platform support (Claude Code, Cursor, Codex, OpenCode, Gemini CLI)
- [x] Markdown auto-translate (behavioral translation of docs with code)

### v0.2 (Next)
- [ ] Multi-feature reconciliation
- [ ] Behavioral conflict detection

### v0.3
- [ ] Team collaboration (multiple stakeholders describing behaviors)
- [ ] Behavior evolution tracking (git history visualization)
- [ ] Natural language queries ("show all payment-related behaviors")

### v1.0
- [ ] Support for AutoGen, CrewAI, LangChain
- [ ] Behavioral regression alerts
- [ ] Public plugin marketplace release

---

## Philosophy

### Why "Behavior-First"?

Traditional development: code first, tests second, behavior is implicit.

BDD tried to fix this: behavior first, but you still need to learn Gherkin, write step definitions, run test frameworks.

**Behavior-First with AI:** behavior first, AI handles everything else, non-technical people participate fully.

### The No-Code Constraint is the Feature

The moment you show code, you've lost the non-technical person. This isn't about "dumbing things down" — it's about keeping everyone focused on **what the system should do**, not **how it does it**.

If the agent can't express something behaviorally, either:
1. The behavior isn't well-defined yet (ask clarifying questions)
2. The agent is thinking in implementation terms (make it rethink)

Either way, forcing behavioral language catches problems earlier.

### You're Writing Tests Without Knowing It

Every time you say "when X happens, the user should see Y" — that's a test.

The agent:
- Understands what you mean
- Generates the test code
- Runs it against your system  
- Tells you if it passes

**You get test coverage without writing tests.** That's the dream.

---

## Contributing

We need:
- **Non-technical testers** — Can you actually use this? What's confusing?
- **BDD experts** — Are we generating good Gherkin? What are we missing?
- **Visual designers** — Make the HTML output even more beautiful

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Inspiration & References

- **[obra/superpowers](https://github.com/obra/superpowers)** — Skill-based agent framework that inspired our approach
- **Cucumber/SpecFlow/Behave** — The BDD tools we're building on (with respect)
- **Reflexion paper** — Agents verifying their own reasoning
- **Claude Code hooks** — The technical infrastructure that makes this possible

---

## License

MIT — use this however you want.

---

## FAQ

**Q: Do I need to know how to code to use this?**  
A: Nope. That's the entire point.

**Q: What if I want to see the code sometimes?**  
A: Enable hybrid mode. Or just ask "show me the technical details" and the agent will explain (still in plain language).

**Q: Does this work with my existing test suite?**  
A: Yes. The .feature files can run alongside your existing tests. We generate Gherkin-compatible step definitions.

**Q: What about complex technical behaviors like "optimize database queries"?**  
A: The agent will find the user-visible behavior: "search results should return in under 1 second" and work backwards. If there's no user-visible outcome, it's probably not a behavior — it's an implementation detail.

**Q: Won't this make the agent slower?**  
A: Yes, by 10-30%. Behavioral verification takes extra time. But reliability matters more than speed for specs.

**Q: Can multiple people describe behaviors for the same project?**  
A: Yes! The agent will detect contradictions and ask for clarification. The .feature file becomes the shared source of truth.

---

**Stop explaining your product in code. Start describing it in behavior.**

🐕 **goodboy** — because everyone deserves to understand what the system actually does.
