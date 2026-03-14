@feature:user-authentication @risk:high
Feature: User Authentication
  Authentication system supporting email/password login, multi-factor
  authentication (TOTP and SMS), session management with refresh tokens,
  account lockout after failed attempts, and password policy enforcement.

  # ── Happy Path ──────────────────────────────────────────────

  @risk:high @technique:ep @smoke @critical-path
  Scenario: Successful login with valid credentials
    Given a registered active user with email "alice@example.com"
    And the stored password is "Str0ng!Pass#42"
    When the user logs in with email "alice@example.com" and password "Str0ng!Pass#42"
    Then the response status should be 200
    And the response should include a "Bearer" access token
    And the response should include a refresh token

  @risk:high @technique:ep @critical-path
  Scenario: Successful logout invalidates tokens
    Given a user is authenticated with valid access and refresh tokens
    When the user logs out
    Then the response status should be 200
    And the access token should no longer be valid
    And the refresh token should no longer be valid

  @risk:high @technique:ep @mfa @critical-path
  Scenario: Login with MFA TOTP
    Given a user "bob@example.com" with TOTP-based MFA enabled
    When the user logs in with correct password and TOTP code "482901"
    Then the response status should be 200
    And MFA should be verified
    And an access token should be issued

  # ── Error Handling ──────────────────────────────────────────

  @risk:high @technique:ep @technique:eg @security
  Scenario: Login with incorrect password
    Given a registered user with email "alice@example.com"
    When the user logs in with email "alice@example.com" and password "WrongPassword1!"
    Then the response status should be 401
    And the error code should be "INVALID_CREDENTIALS"
    And the message should be "Email or password is incorrect."

  @risk:high @technique:ep @technique:eg @security @enumeration
  Scenario: Login with non-existent email
    Given no account exists for "nobody@example.com"
    When the user logs in with email "nobody@example.com" and password "AnyPass1!"
    Then the response status should be 401
    And the error code should be "INVALID_CREDENTIALS"
    And the response time should be within 50ms of the wrong-password case

  @risk:high @technique:ep @mfa @security
  Scenario: Login with invalid MFA code
    Given a user "bob@example.com" with TOTP-based MFA enabled
    When the user logs in with correct password and TOTP code "000000"
    Then the response status should be 401
    And the error code should be "INVALID_MFA_CODE"
    And no access token should be issued

  @risk:medium @technique:eg @mfa @reliability
  Scenario: SMS MFA code delivery failure
    Given a user "carol@example.com" with SMS-based MFA enabled
    And the SMS provider returns a 503 error
    When the user requests an MFA code
    Then the response status should be 503
    And the error code should be "MFA_DELIVERY_FAILED"
    And an email fallback should be offered

  # ── Boundary — Password Policy ──────────────────────────────

  @risk:medium @technique:bva @password-policy @boundary
  Scenario Outline: Password length boundaries
    When a user sets password to a <length>-character string meeting complexity requirements
    Then the password should be <result>

    Examples:
      | length | result   |
      | 8      | accepted |
      | 7      | rejected |
      | 128    | accepted |
      | 129    | rejected |

  @risk:medium @technique:ep @technique:ce @password-policy
  Scenario Outline: Password complexity requirements
    When a user sets password to "<password>"
    Then the password should be rejected
    And the error should be "<error>"

    Examples:
      | password        | error                      |
      | alllowercase1!  | PASSWORD_MISSING_UPPERCASE |
      | ALLUPPERCASE1!  | PASSWORD_MISSING_LOWERCASE |
      | NoDigitsHere!!  | PASSWORD_MISSING_DIGIT     |
      | NoSpecial123Aa  | PASSWORD_MISSING_SPECIAL   |

  # ── State Transition — Account Lockout ──────────────────────

  @risk:high @technique:st @technique:bva @security @state-machine @brute-force
  Scenario Outline: Account lockout after failed login attempts
    Given an active user account
    And <previous_failures> consecutive failed login attempts
    When the user attempts to log in with a <credential> password
    Then the account state should be "<expected_state>"

    Examples: Lockout boundaries
      | previous_failures | credential | expected_state |
      | 4                 | wrong      | locked         |
      | 4                 | correct    | active         |
      | 2                 | wrong      | active         |

  @risk:high @technique:st @security @state-machine
  Scenario: Permanent lockout after repeated lockout cycles
    Given a user account that has been locked 3 times
    When the user fails login again after the latest lockout expires
    Then the account should be permanently locked
    And only an admin unlock should restore access

  # ── Session Management ──────────────────────────────────────

  @risk:high @technique:st @technique:bva @session @tokens
  Scenario: Access token expiry and refresh
    Given a user with an access token that expired 1 minute ago
    And a valid refresh token
    When the client requests a token refresh
    Then a new access token should be issued
    And the refresh token should be rotated

  @risk:high @technique:eg @technique:st @security @tokens @critical-path
  Scenario: Refresh token reuse detection
    Given a refresh token that has already been rotated
    When a client attempts to use the old refresh token
    Then the response status should be 401
    And the error code should be "TOKEN_REUSE_DETECTED"
    And all tokens in the session family should be revoked

  @risk:medium @technique:bva @session @boundary
  Scenario: Concurrent sessions limit
    Given a user with 5 active sessions
    When the user logs in from a 6th device
    Then the total active sessions should remain 5
    And the oldest session should be revoked

  @risk:high @technique:ep @security @session
  Scenario: Session invalidation on password change
    Given a user with 3 active sessions
    When the user changes their password from session "sess-3"
    Then sessions "sess-1" and "sess-2" should be revoked
    And session "sess-3" should remain active
