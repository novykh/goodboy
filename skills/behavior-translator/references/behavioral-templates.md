# Behavioral Templates

Ready-to-use templates for common behavioral scenarios. Copy and adapt these when creating `.feature` files and word-flow diagrams.

## User Authentication

### Signup

```gherkin
Feature: User Signup
  New visitors can create an account to access the system.

  Scenario: Successful signup with new email
    Given a visitor on the signup page
    When they enter a valid email and password
    And click "Create Account"
    Then they see "Welcome! Check your email to verify your account."
    And a verification email arrives within 5 minutes

  Scenario: Signup with existing email
    Given a visitor on the signup page
    When they enter an email that already has an account
    Then they see "This email is already registered. Try logging in?"
    And a "Log in" link is shown

  Scenario: Signup with weak password
    Given a visitor on the signup page
    When they enter a password that's too short
    Then they see "Password needs at least 8 characters"
    And the "Create Account" button stays disabled
```

### Login

```gherkin
Feature: User Login
  Registered users can log in to access their account.

  Scenario: Successful login
    Given a registered user on the login page
    When they enter correct email and password
    And click "Log In"
    Then they see their dashboard

  Scenario: Wrong password
    Given a registered user on the login page
    When they enter the wrong password
    Then they see "Incorrect email or password"
    And they can try again

  Scenario: Forgotten password
    Given a user who forgot their password
    When they click "Forgot password?"
    And enter their email
    Then they see "Check your email for a reset link"
    And a reset email arrives within 5 minutes
```

## E-Commerce

### Cart Management

```gherkin
Feature: Shopping Cart
  Customers can add, remove, and manage items before checkout.

  Scenario: Add item to cart
    Given a customer viewing a product
    When they click "Add to Cart"
    Then the cart icon shows 1 item
    And a confirmation appears: "[Product name] added to cart"

  Scenario: Remove item from cart
    Given a customer with items in their cart
    When they click "Remove" next to an item
    Then the item disappears from the cart
    And the total updates immediately

  Scenario: Empty cart
    Given a customer with no items in their cart
    When they view the cart
    Then they see "Your cart is empty"
    And a "Continue Shopping" link is shown
```

### Checkout

```gherkin
Feature: Checkout
  Customers can complete their purchase.

  Scenario: Successful purchase
    Given a customer with items in their cart
    When they enter shipping and payment details
    And click "Place Order"
    Then they see "Order confirmed! Check your email for details."
    And a confirmation email arrives
    And the cart is now empty

  Scenario: Payment failure
    Given a customer at the payment step
    When their payment is declined
    Then they see "Payment didn't go through. Please check your card details."
    And their cart items are preserved
    And they can try a different payment method
```

## Subscription Management

### Cancellation

```gherkin
Feature: Subscription Cancellation
  Customers who cancel should maintain access until their billing period ends.

  Scenario: Standard cancellation
    Given a customer with an active subscription
    And 15 days remaining in their billing period
    When they click "Cancel Subscription"
    And confirm the cancellation
    Then they see "Your subscription will end on [date]"
    And they maintain full access until that date

  Scenario: Immediate cancellation during trial
    Given a customer in a free trial
    When they cancel their subscription
    Then their access ends immediately
    And they see "Your trial has been cancelled"
```

## Notifications

### Email Notifications

```gherkin
Feature: Email Notifications
  Users receive emails about important account events.

  Scenario: Welcome email after signup
    Given a new user completes signup
    Then they receive a welcome email within 5 minutes
    And the email contains a verification link

  Scenario: Order confirmation
    Given a customer places an order
    Then they receive a confirmation email
    And the email includes order number and estimated delivery

  Scenario: Password reset
    Given a user requests a password reset
    Then they receive a reset email within 2 minutes
    And the reset link expires after 1 hour
```

## Error Handling

### Graceful Failures

```gherkin
Feature: Graceful Error Handling
  When things go wrong, users see helpful messages instead of technical errors.

  Scenario: Page not found
    Given a visitor navigates to a page that doesn't exist
    Then they see "We couldn't find that page"
    And a link to return to the homepage

  Scenario: System temporarily unavailable
    Given the system is experiencing issues
    When a user tries to perform an action
    Then they see "We're having trouble right now. Please try again in a few minutes."
    And their work is not lost

  Scenario: Form submission during connection loss
    Given a user filling out a form
    When they lose internet connection and submit
    Then they see "You appear to be offline. We'll save your work and try again when you're connected."
```

## Word-Flow Template

Use this structure when presenting a behavioral map:

```
🐕 Behavior: [Name]

[Trigger Event]
  → [First thing that happens]
  → [Decision point]?
    → yes → [This outcome]
    → no → [That outcome]

Edge: What if [unusual situation]?
  → [How the system handles it]

Status: [✓ Working | ✗ Failing | ? Untested]
```
