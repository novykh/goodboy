# Word-Flow Patterns

Reference patterns for expressing software behavior as plain-language flow diagrams.

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
