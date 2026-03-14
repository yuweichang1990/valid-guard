@feature:e-commerce-checkout @risk:high
Feature: E-Commerce Checkout
  End-to-end checkout flow: cart validation, pricing/discounts, payment
  processing, inventory reservation, and order lifecycle management.

  # ── Happy Path ──────────────────────────────────────────────

  @risk:high @technique:ep @smoke @critical-path
  Scenario: Successful checkout with a single item
    Given an authenticated customer
    And the cart contains 1 "SHOE-42" at $89.99
    And the item is in stock
    When the customer checks out with credit card to US address 94105
    Then the order should be confirmed with status 201
    And the total should be $89.99

  @risk:high @technique:ep @smoke @critical-path
  Scenario: Successful checkout with multiple items
    Given an authenticated customer
    And the cart contains:
      | sku     | qty | unit_price |
      | SHOE-42 | 2   | 89.99      |
      | SOCK-M  | 3   | 12.99      |
      | BELT-L  | 1   | 34.99      |
    When the customer checks out with credit card
    Then the order should be confirmed with 3 line items
    And the total should be $253.94

  @risk:medium @technique:ep @guest
  Scenario: Guest checkout without authentication
    Given an unauthenticated user with email "guest@example.com"
    And the cart contains 1 "HAT-S" at $24.99
    When the user checks out with digital wallet
    Then the order should be confirmed as a guest order

  # ── Edge Cases ──────────────────────────────────────────────

  @risk:low @technique:ep @validation
  Scenario: Empty cart checkout attempt
    Given an authenticated customer with an empty cart
    When the customer attempts to check out
    Then the response status should be 400
    And the error code should be "CART_EMPTY"

  # ── Boundary Values ─────────────────────────────────────────

  @risk:medium @technique:bva @pricing @boundary
  Scenario Outline: Order total boundaries
    Given a cart with total <total>
    When the customer checks out
    Then the response status should be <status>

    Examples:
      | total      | status |
      | $0.50      | 201    |
      | $0.49      | 400    |
      | $99,999.99 | 201    |
      | $100,000   | 400    |

  @risk:low @technique:bva @validation @boundary
  Scenario Outline: Quantity per SKU boundaries
    Given a cart with <qty> units of "PEN-1"
    When the customer attempts to check out
    Then the result should be <result>

    Examples:
      | qty | result   |
      | 99  | accepted |
      | 100 | rejected |
      | 0   | rejected |

  # ── Error Handling ──────────────────────────────────────────

  @risk:high @technique:ep @technique:eg @payment @error-handling
  Scenario Outline: Payment declined by issuer
    Given a valid cart ready for checkout
    When payment is declined with code "<decline_code>"
    Then the response status should be 402
    And the error code should be "PAYMENT_DECLINED"

    Examples:
      | decline_code       |
      | insufficient_funds |
      | stolen_card        |

  # ── State Transition — Order Lifecycle ──────────────────────

  @risk:high @technique:st @state-machine @critical-path
  Scenario: Order lifecycle state transitions
    # Valid transitions
    Given an order in "confirmed" state
    When the customer requests cancellation within 15 minutes
    Then the order should transition to "cancelled"
    And a refund should be initiated

  @risk:high @technique:st @state-machine
  Scenario: Cancellation after window closes
    Given an order in "confirmed" state
    When the customer requests cancellation after 45 minutes
    Then the cancellation should be rejected with "CANCELLATION_WINDOW_EXPIRED"

  @risk:high @technique:st @state-machine
  Scenario: Invalid state transition
    Given an order in "cart" state
    When a "delivery_confirmed" event is received
    Then it should be rejected with "INVALID_STATE_TRANSITION"

  # ── Decision Table — Discounts ──────────────────────────────

  @risk:high @technique:dt @technique:pw @pricing @discounts @decision-table
  Scenario Outline: Discount calculation rules
    Given a <loyalty_tier> customer
    And coupon "<coupon>" is <coupon_status>
    And the cart total is <cart_range>
    And promotions are <promo_status>
    When the discount engine calculates
    Then coupon discount should be <coupon_pct>%
    And loyalty discount should be <loyalty_pct>%
    And free shipping should be <free_ship>

    Examples: Discount combinations
      | loyalty_tier | coupon  | coupon_status | cart_range  | promo_status | coupon_pct | loyalty_pct | free_ship |
      | gold         | SAVE15  | valid         | over $100   | active       | 15         | 10          | yes       |
      | none         | SAVE15  | valid         | over $100   | inactive     | 15         | 0           | yes       |
      | none         |         | none          | under $100  | inactive     | 0          | 0           | no        |
      | gold         | EXP20   | expired       | over $100   | active       | 0          | 10          | yes       |

  # ── Security ────────────────────────────────────────────────

  @risk:high @technique:eg @security @fraud
  Scenario: Price tampering via modified cart payload
    Given the catalog price for "SHOE-42" is $89.99
    When the client submits a cart with "SHOE-42" at $0.01
    Then the server should charge catalog price $89.99
    And the total should be $89.99

  @risk:high @technique:eg @security @idempotency
  Scenario: Replay attack with duplicate order submission
    Given a valid checkout with idempotency key "abc-123"
    When the same request is submitted twice
    Then only one order should be created
    And the second response should return the original order
