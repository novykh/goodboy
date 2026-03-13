# goodboy Quick Reference

## Essential Commands

```bash
# Start conversation
claude
> You are a goodboy and I don't know code.

# View all behaviors
ls docs/behaviors/

# Open dashboard
open docs/behaviors/dashboard.html
```

---

## Behavioral Language Patterns

> **💡 Don't worry about being perfectly organized.** The agent will synthesize rambling, off-topic, or messy inputs and extract the pure behavioral logic. Just describe what you want — the agent does the structuring. It will also ignore UI styling requests (colors, fonts, etc.) and focus only on behavior.

### ✅ Good (Behavioral)
```
"When a user clicks the submit button, they should see a success message"
"If the payment fails, show them an error with a retry option"
"After signup, send a welcome email within 5 minutes"
```

### ❌ Bad (Technical)
```
"The POST handler should return 200 with JSON"
"Add error handling to the payment service"
"The email job should be enqueued"
```

---

## Word-Flow Diagram Format

```
[Trigger Event]
  → [Decision Point]?
    → yes → [Outcome A] → [Next State]
    → no → [Outcome B] → [Alternative Path]
  
Edge: What if [condition]?
  → [Fallback] → [Recovery]
```

**Example:**
```
User clicks "Buy Now"
  → Item in stock?
    → yes → Add to cart → Show cart
    → no → Show "Out of stock" → Offer waitlist

Edge: What if payment fails?
  → Show error → Keep items in cart → Offer retry
```

---

## Common Patterns

### User Action → System Response
```
User does X → System shows Y
```

### Conditional Behavior
```
User does X → Condition met?
  → yes → Outcome A
  → no → Outcome B
```

### Time-Based Behavior
```
User does X → System does Y within [timeframe]
```

### Error Handling
```
User does X → Error occurs? 
  → yes → Show error → Offer recovery path
  → no → Continue normal flow
```

---

## Asking the Right Questions

### To Define New Behavior
- "When [event], what should the user see?"
- "What happens if [edge case]?"
- "How long should [action] take?"

### To Check Existing Behavior
- "Show me the [feature name] behavior"
- "What happens when [scenario]?"
- "Is the [behavior] working correctly?"

### To Fix Broken Behavior
- "The [behavior] isn't working right"
- "Users are seeing [unexpected outcome] instead of [expected]"
- "Fix the [behavior name]"

---

## Understanding Agent Responses

### Behavioral Map
The agent showing you a flow diagram. Confirm it's correct.

### Verification Result
```
Expected: [what should happen]
Actual: [what's happening now]
Gap: [what's wrong]
```

### Status Updates
- ✓ Passing — behavior works as expected
- ✗ Failing — behavior not matching spec
- ⚠️ Untested — behavior described but not verified yet

---

## Common Workflows

### 1. Defining a Feature
```
You: "When users sign up, they should..."
Agent: [maps behavior, asks clarifying questions]
You: [clarifies edge cases]
Agent: [updates map, asks for confirmation]
You: "Yes, that's right"
Agent: [saves to .feature file, runs tests]
Agent: "This behavior is currently failing. Want me to fix it?"
```

### 2. Debugging an Issue  
```
You: "Users aren't getting confirmation emails"
Agent: [checks behavioral spec]
Agent: "Expected: email within 5 min. Actual: no email sent."
Agent: "Gap: messages stuck in queue. Want me to fix it?"
You: "Yes"
Agent: [fixes, retests]
Agent: "This behavior is now passing ✓"
```

### 3. Exploring System  
```
You: "Show me all payment-related behaviors"
Agent: [lists behaviors from .feature files]
Agent: "3 payment behaviors: processing, refunds, failed payment recovery"
You: "Show me the refund behavior"
Agent: [displays behavioral map]
```

---

## Troubleshooting

### "I'm not seeing visual output"
Check that HTML files are being generated in `docs/behaviors/`  
Try: `open docs/behaviors/dashboard.html`

### "Auto-refresh isn't working"
Make sure the browser hasn't blocked the page. The HTML files use a meta refresh tag or Live.js to automatically update.

### "Agent is showing me code"
The PreToolUse hook might not be active.  
Check: the goodboy plugin is installed at `~/.claude/plugins/goodboy/` and `hooks/hooks.json` is properly configured.

### "Agent resets to normal mode"
Make sure to re-start the conversation with `> You are a goodboy and I don't know code.` if the session resets.

### "Behavioral maps seem incomplete"
The agent should ask clarifying questions. If it doesn't:  
Say: "What about edge cases?" or "What if [condition]?"

### "Tests aren't running"
Check that test framework is installed:
```bash
# For Python projects
pip install behave

# For JavaScript projects  
npm install --save-dev @cucumber/cucumber
```

---

## Tips for Better Behaviors

### Be Specific About Outcomes
❌ "The user should be notified"  
✅ "The user should see a banner at the top saying 'Success'"

### Include Timeframes
❌ "Send an email"  
✅ "Send an email within 5 minutes"

### Think in User Terms
❌ "The API should return valid data"  
✅ "The user should see their order history"

### Map the Edges
Don't just describe the happy path. Ask:
- "What if the user's connection is slow?"
- "What if they click twice?"
- "What if the data isn't available?"

---

## Behavioral Spec Best Practices

### Start Broad, Then Detailed
1. Map the main flow first
2. Confirm the happy path
3. Then add edge cases
4. Then add error scenarios

### One Behavior at a Time
Don't describe 5 features in one message. The agent will map each separately and confirm individually.

### Review the Spec Regularly
```bash
open docs/behaviors/dashboard.html
```
See what's passing, failing, or untested.

### Collaborate
Multiple people can describe behaviors. The agent will:
- Add them all to the .feature files
- Detect contradictions
- Ask which version is correct

---

## Integration Points

### With Development
When behaviors fail, agent can automatically:
- Use brainstorming skill to plan fix
- Use execution skill to implement
- Retest and report back

### With Design
Behaviors can reference designs:
"When user clicks upgrade, show the modal from [Figma link]"

### With QA
.feature files ARE the test plan.  
QA can read them directly (no code knowledge needed).

---

## File Structure Reference

```
your-project/
├── .behavior-first-mode          # (Optional) Auto-activate for every session
├── docs/
│   └── behaviors/                # Your behavioral specs
│       ├── 2026-03-06-signup.feature
│       ├── 2026-03-06-payment.feature
│       └── dashboard.html        # Overview page
└── tests/
    └── step_definitions/         # Generated (hidden from you)
```

> The goodboy plugin itself lives in `~/.claude/plugins/goodboy/` with its hooks, skills, and scripts. The above is what appears in *your* project.

---

## What Each File Contains

### Activation
No flag files needed. Just say `> You are a goodboy and I don't know code.` to activate the behavioral layer.

### `.feature` files
Human-readable behavioral specs in Gherkin format.  
You edit these through conversation, not directly.

### `dashboard.html`  
Visual overview of all behaviors with status indicators.  
Auto-generated, opens in browser.

### `step_definitions/`
The actual test code. Generated by agent.  
You don't need to look at this unless you want to.

---

## Getting Help

### In-Session
```
> I don't understand this behavioral map
> Can you explain [behavior] differently?
> Show me a simpler version
```

### Documentation
- Full vision: `VISION.md`
- Architecture: `ARCHITECTURE.md`  
- This guide: `QUICKREF.md`

### Community
- GitHub issues for bugs/features
- Discussions for patterns and use cases

---

## Remember

**You're not learning to code. You're learning to describe behavior clearly.**

The agent handles:
- Translation to code
- Test generation
- Execution
- Verification

You handle:
- Describing what should happen
- Confirming the agent understood correctly
- Deciding if behaviors are acceptable

That's it. That's the whole interface.

---

*Keep this file open while you work. Reference it when you're unsure how to phrase something.*
