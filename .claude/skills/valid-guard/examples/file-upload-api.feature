@feature:file-upload-api @risk:medium
Feature: File Upload API
  REST API for uploading files (documents, images, archives). Supports
  up to 100 MB, MIME validation, virus scanning, S3 storage, per-user throttle.

  Background:
    Given an authenticated user with available storage quota

  # ── Happy Path ──────────────────────────────────────────────

  @risk:medium @technique:ep @smoke @critical-path
  Scenario: Upload a valid image file
    When the user uploads "photo.jpg" (image/jpeg, 2.5 MB)
    Then the response status should be 201
    And the response should include a file ID
    And the virus scan status should be "clean"

  @risk:medium @technique:ep @smoke
  Scenario: Upload a valid PDF document
    When the user uploads "report.pdf" (application/pdf, 10 MB)
    Then the response status should be 201
    And the response should include a file ID

  # ── Equivalence Partitioning — File Types ───────────────────

  @risk:high @technique:ep @security @validation
  Scenario Outline: File type validation
    When the user uploads "<filename>" with content type "<content_type>"
    Then the response status should be <status>

    Examples: Allowed types
      | filename         | content_type     | status |
      | image.png        | image/png        | 201    |
      | spreadsheet.xlsx | application/xlsx | 201    |
      | archive.zip      | application/zip  | 201    |

    Examples: Disallowed types
      | filename    | content_type             | status |
      | malware.exe | application/x-msdownload | 415    |
      | script.sh   | application/x-sh         | 415    |
      | data.xyz    | application/octet-stream | 415    |

  # ── Boundary Values — File Size ─────────────────────────────

  @risk:medium @technique:bva @boundary @validation
  Scenario Outline: File size boundaries
    When the user uploads a file of <size_bytes> bytes
    Then the response status should be <status>

    Examples:
      | size_bytes  | status |
      | 1           | 201    |
      | 0           | 400    |
      | 104857600   | 201    |
      | 104857601   | 413    |

  # ── Error Handling ──────────────────────────────────────────

  @risk:medium @technique:ep @security
  Scenario: Upload with missing authentication
    Given an unauthenticated request
    When the user uploads "photo.jpg"
    Then the response status should be 401
    And the error code should be "AUTHENTICATION_REQUIRED"

  @risk:high @technique:eg @security @virus-scan
  Scenario: Virus detected in uploaded file
    When the user uploads "document.pdf" containing a test virus signature
    Then the response status should be 422
    And the error code should be "VIRUS_DETECTED"
    And the file should not be stored in user space
    And the file should be quarantined
