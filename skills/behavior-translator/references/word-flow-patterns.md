# Behavioral Visualization Patterns

Reference patterns for expressing software behavior visually in the CLI. The agent picks the right format based on what it's describing. Only use visuals when the behavior is complex enough to warrant one — simple behaviors are better as plain text.

## Choosing the Right Format

| What you're describing | Use this format |
|----------------------|----------------|
| Multi-step journey (signup, checkout) | **Flow** |
| Yes/no branching on a condition | **Decision Flow** |
| Rules with many branches (pricing, permissions) | **Tree** |
| Lifecycle with named states (order, subscription) | **State Diagram** |
| Before/after or plan comparison | **Table** |
| Conversion drop-off (visitors → signups → paid) | **Funnel** |
| Scheduled events over time (email sequences) | **Timeline** |
| Steps in strict order | **Sequential Flow** |
| Things happening at the same time | **Parallel Flow** |
| Repeated action until condition met | **Loop Flow** |
| Unexpected conditions | **Edge Case Flow** |
| Delayed outcomes | **Timed Flow** |
| Nested multi-factor decisions | **Conditional Chain** |

You can combine formats in a single response. "Here's the pricing tree, and here's the upgrade flow between tiers."

## Basic Flow

```
[Trigger]
  → [Outcome]
```

A single action produces a single result.

**Example:**
```
[Customer clicks "Sign Up"]
  → [Registration form appears]
```

## Decision Flow

```
[Trigger]
  → [Decision Point]?
    → yes → [Outcome A]
    → no → [Outcome B]
```

An action leads to a fork based on a condition.

**Example:**
```
[Customer enters email]
  → [Email already registered?]
    → yes → [Show "This email is already registered. Try logging in?"]
    → no → [Continue to password step]
```

## Sequential Flow

```
[Step 1]
  → [Step 2]
  → [Step 3]
  → [Final Outcome]
```

Multiple steps happen in order.

**Example:**
```
[Customer clicks "Place Order"]
  → [System checks payment method is valid]
  → [System reserves inventory]
  → [System charges payment]
  → [Customer sees "Order confirmed! Check your email for details."]
```

## Parallel Flow

```
[Trigger]
  → simultaneously:
    → [Outcome A]
    → [Outcome B]
    → [Outcome C]
```

Multiple things happen at the same time.

**Example:**
```
[Customer completes signup]
  → simultaneously:
    → [Welcome email is sent]
    → [Account dashboard appears]
    → [Free trial period begins]
```

## Loop Flow

```
[Trigger]
  → [Action]
  → [Check: done?]
    → no → [Back to Action]
    → yes → [Final Outcome]
```

An action repeats until a condition is met.

**Example:**
```
[Customer enters password]
  → [System checks password strength]
  → [Strong enough?]
    → no → [Show hint: "Add a number or symbol"]
    → no → [Back to password entry]
    → yes → [Accept password, continue to next step]
```

## Edge Case Flow

```
[Main Flow]
  ...

Edge: What if [unexpected condition]?
  → [Fallback Behavior]
  → [Recovery Path]
```

Handles situations outside the normal path.

**Example:**
```
[Customer clicks "Pay Now"]
  → [Process payment]
  → [Show confirmation]

Edge: What if the payment fails?
  → [Show "Payment didn't go through. Please check your card details."]
  → [Return to payment form with details preserved]

Edge: What if the system is down?
  → [Show "We're having trouble processing payments right now. Please try again in a few minutes."]
```

## Timed Flow

```
[Trigger]
  → [Immediate outcome]
  → after [time period]:
    → [Delayed outcome]
```

Some outcomes happen after a delay.

**Example:**
```
[Customer cancels subscription]
  → [Show "Your subscription will end on March 31"]
  → [Customer keeps full access]
  → after billing period ends:
    → [Access is removed]
    → [Send "Your subscription has ended" email]
```

## Conditional Chain

```
[Trigger]
  → [Condition A]?
    → yes → [Condition B]?
      → yes → [Outcome for A+B]
      → no → [Outcome for A only]
    → no → [Default outcome]
```

Nested decisions that depend on multiple factors.

**Example:**
```
[Customer requests refund]
  → [Within 30-day window?]
    → yes → [Order contains physical items?]
      → yes → [Show "Ship items back and we'll refund within 5 business days"]
      → no → [Refund processed immediately, show "Refund on its way!"]
    → no → [Show "This order is past the refund window. Contact support for help."]
```

## State Transition

```
[Entity] starts in [State A]
  → [Event happens] → moves to [State B]
  → [Event happens] → moves to [State C]
  → [Event happens] → returns to [State A]
```

Tracks how something changes over time.

**Example:**
```
[Order] starts in [Placed]
  → [Payment confirmed] → moves to [Processing]
  → [Shipped] → moves to [In Transit]
  → [Delivered] → moves to [Complete]
  → [Customer requests return] → moves to [Return Pending]
  → [Return received] → moves to [Refunded]
```

## Tree

```
[Root]
├── [Branch A]
│   ├── [Detail]
│   └── [Detail]
├── [Branch B]
│   ├── [Detail]
│   └── [Detail]
└── [Branch C] — MISSING
    └── (needs definition)
```

Shows hierarchical rules, categories, or feature breakdowns. Use when there are multiple branches at the same level, each with their own sub-items.

**Example:**
```
Pricing
├── Free
│   ├── 1 project
│   └── Basic features
├── Pro ($29/mo)
│   ├── Unlimited projects
│   ├── Priority support
│   └── Advanced analytics
├── Team ($99/mo)
│   ├── Everything in Pro
│   ├── 10 seats included
│   └── Admin controls
└── Enterprise — MISSING
    └── No pricing or features defined
```

## Table

```
┌──────────────┬──────────────┐
│ [Column A]   │ [Column B]   │
├──────────────┼──────────────┤
│ [value]      │ [value]      │
│ [value]      │ [value]      │
└──────────────┴──────────────┘
```

Shows side-by-side comparisons. Use for before/after, expected vs actual, plan comparisons, or feature matrices.

**Example:**
```
┌──────────────────────┬──────────────────────┐
│ Before               │ After                │
├──────────────────────┼──────────────────────┤
│ Cancel removes       │ Cancel preserves     │
│ access immediately   │ access until period  │
│                      │ ends                 │
├──────────────────────┼──────────────────────┤
│ No confirmation      │ "Are you sure?"      │
│ prompt               │ prompt shown         │
├──────────────────────┼──────────────────────┤
│ No email sent        │ Confirmation email   │
│                      │ sent on cancellation │
└──────────────────────┴──────────────────────┘
```

## Funnel

```
[Stage 1]           ████████████████████  100%
  ↓
[Stage 2]           ████████████          60%
  ↓
[Stage 3]           ██████                30%
  ↓
[Stage 4]           ███                   15%
```

Shows conversion or drop-off across stages. Use when describing user journeys where volume decreases at each step.

**Example:**
```
Visit homepage      ████████████████████  100% of visitors
  ↓
Click "Sign Up"     ████████████          58%
  ↓
Complete form       ██████                31%
  ↓
Verify email        ████                  22%
  ↓
First project       ██                    12%
```

## Timeline

```
[Time/Date]  ── [Event]
     │
[Time/Date]  ── [Event]
     │
[Time/Date]  ── [Event]
```

Shows events in chronological order. Use for email sequences, billing cycles, scheduled actions, or any time-ordered behavior.

**Example:**
```
Day 0   ── Customer signs up
  │        Welcome email sent immediately
  │
Day 1   ── "Getting started" email
  │
Day 3   ── "Did you try feature X?" email
  │
Day 7   ── Trial halfway reminder
  │        "You have 7 days left"
  │
Day 13  ── Trial ending warning
  │        "Your trial ends tomorrow"
  │
Day 14  ── Trial expires
           Access restricted to free tier
```

## State Diagram (Compact)

```
(State A) ──event──→ (State B) ──event──→ (State C)
                        │                      │
                      event                  event
                        ↓                      ↓
                   (State D) ──event──→ (State E)
```

A more compact version of state transitions. Use when states have multiple possible transitions and you want to show the full map at a glance.

**Example:**
```
(Trial) ──expires──→ (Active) ──cancels──→ (Cancelling)
                        │                      │
                  payment fails          period ends
                        ↓                      ↓
                   (Past Due) ──3 retries──→ (Churned)
```
