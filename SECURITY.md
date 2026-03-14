# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Valid Guard, please report it responsibly.

**Email**: yuweichang1990@gmail.com

**What to include**:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

**Response time**: We aim to acknowledge reports within 48 hours.

## Scope

Valid Guard is a Claude Code skill (prompt-based instructions). It does not run as a standalone service, does not store user data, and does not have network access beyond what Claude Code provides.

Security concerns most likely relate to:
- Generated test code that introduces vulnerabilities
- YAML plan files containing sensitive data (e.g., real credentials used as test examples)
- HTML reports exposing internal system details

## Best Practices

- Do not use real credentials, API keys, or PII in test plan examples
- Add `valid-guard/reports/` to `.gitignore` to avoid committing HTML reports with internal details
- Review generated test code before committing, especially for security-related scenarios
