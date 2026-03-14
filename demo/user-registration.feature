@feature:user-registration @risk:high
Feature: User Registration with Email Verification
  User registration system allowing new users to create an account with email
  and password credentials. Verification email with time-limited token required
  to activate the account.

  Background:
    Given the registration API is available
    And the email service is operational

  # ── Happy Path ──────────────────────────────────────────────

  @risk:high @technique:ep @smoke @critical-path
  Scenario: Successful registration with valid inputs
    Given no account exists for "alice@example.com"
    When the user registers with email "alice@example.com" and password "Str0ng!Pass#42" and confirmation "Str0ng!Pass#42"
    Then the response status should be 201
    And the account state should be "unverified"
    And a verification email should be sent to "alice@example.com"

  @risk:high @technique:ep @technique:st @critical-path @verification
  Scenario: Successful email verification with valid token
    Given an unverified account exists for "alice@example.com"
    And a valid verification token was issued 30 minutes ago
    When the user submits the verification token
    Then the response status should be 200
    And the account state should be "active"
    And the token should be invalidated

  # ── Error Handling ──────────────────────────────────────────

  @risk:high @technique:ep @technique:eg @security @enumeration
  Scenario: Registration with duplicate email
    Given an account already exists for "alice@example.com"
    When the user registers with email "alice@example.com" and password "An0ther!Pass99" and confirmation "An0ther!Pass99"
    Then the response status should be 200
    And the response message should contain "verification link has been sent"
    And the response time should be within 50ms of a non-duplicate registration

  @risk:medium @technique:ep @technique:ce @password-policy @validation
  Scenario Outline: Registration with weak password
    When the user registers with email "bob@example.com" and password "<password>" and confirmation "<password>"
    Then the response status should be 400
    And the error code should be "<error>"

    Examples:
      | password       | error                     |
      | short1!        | PASSWORD_TOO_SHORT        |
      | alllowercase1! | PASSWORD_MISSING_UPPERCASE |
      | NoDigitsHere!! | PASSWORD_MISSING_DIGIT     |

  @risk:medium @technique:ep @technique:eg @validation
  Scenario Outline: Registration with empty required fields
    When the user registers with email "<email>" and password "<password>" and confirmation "<confirmation>"
    Then the response status should be 400
    And the error code should be "<error>"

    Examples:
      | email          | password       | confirmation   | error             |
      |                | Str0ng!Pass#42 | Str0ng!Pass#42 | EMAIL_REQUIRED    |
      | bob@example.com |               |                | PASSWORD_REQUIRED |
      |                | Str0ng!Pass#42 | Str0ng!Pass#42 | EMAIL_REQUIRED    |

  @risk:medium @technique:ep @validation
  Scenario Outline: Password and confirmation mismatch
    When the user registers with email "carol@example.com" and password "<password>" and confirmation "<confirmation>"
    Then the response status should be 400
    And the error code should be "PASSWORD_CONFIRMATION_MISMATCH"

    Examples:
      | password       | confirmation   |
      | Str0ng!Pass#42 | Str0ng!Pass#43 |
      | Str0ng!Pass#42 | str0ng!pass#42 |

  # ── Boundary Values ─────────────────────────────────────────

  @risk:medium @technique:bva @technique:ep @validation @boundary
  Scenario Outline: Email format boundary cases
    When the user registers with email "<email>" and password "Str0ng!Pass#42" and confirmation "Str0ng!Pass#42"
    Then the email validation result should be "<valid>"

    Examples:
      | email                  | valid |
      | a@b.co                 | true  |
      | user+tag@example.com   | true  |
      | missing-at-sign.com    | false |
      | @no-local-part.com     | false |

  # ── Security ────────────────────────────────────────────────

  @risk:high @technique:eg @security @injection
  Scenario Outline: SQL injection in email field
    When the user registers with email "<malicious_email>" and password "Str0ng!Pass#42" and confirmation "Str0ng!Pass#42"
    Then the response status should be 400
    And the error code should be "INVALID_EMAIL_FORMAT"
    And the database should remain intact

    Examples:
      | malicious_email                    |
      | '; DROP TABLE users; --            |
      | admin@example.com' OR '1'='1       |

  # ── State Transition — Token Expiry ─────────────────────────

  @risk:high @technique:st @technique:bva @verification @boundary @state-machine
  Scenario Outline: Email verification token expiry
    Given an unverified account exists for "alice@example.com"
    And a verification token was issued <token_age_hours> hours ago
    When the user submits the verification token
    Then the response status should be <expected_status>
    And the verification result should be "<expected_state>"

    Examples:
      | token_age_hours | expected_status | expected_state |
      | 23              | 200             | active         |
      | 24              | 410             | expired        |
      | 25              | 410             | expired        |

  # ── Edge Case — Rate Limiting ───────────────────────────────

  @risk:medium @technique:bva @technique:eg @rate-limiting @verification
  Scenario Outline: Resend verification email rate limiting
    Given an unverified account exists for "alice@example.com"
    And <prior_resends> verification emails have been resent this hour
    When the user requests another verification email
    Then the response status should be <expected_status>

    Examples:
      | prior_resends | expected_status |
      | 2             | 200             |
      | 3             | 429             |
