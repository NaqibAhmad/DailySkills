# Security

Builds on the three security rules in SKILL.md (identity from the JWT, auth on every sensitive route, every query scoped). For an audit, also run `python <this skill's folder>/scripts/security_scan.py <path>`: it flags bare/broad `except`, `%`-formatted SQL, `jwt.decode` without `algorithms`, suspected plaintext password assignment, and `print`.

## Secrets and credentials

- Secrets come from env through `Settings`, and stay server-side: absent from code, logs, responses, migrations and the browser. `.env` is gitignored; production secrets live in a vault, different per environment.
- Passwords: argon2 or bcrypt via `pwdlib`.
- Stored tokens (API keys, reset links): keep a hash, compare with `hmac.compare_digest`.
- Dev escape hatches (`AUTH_DISABLED`, …) default off, log a loud warning at startup, and are documented as local-only.

## Defence in depth

- Service-owned tables get RLS enabled with no policies (service role only), so a frontend bug cannot become a data leak.
- Admin routes check the role in a shared dependency.
- Auth failures return one generic message; error responses carry no stack traces.

## HTTP hardening

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,      # an explicit list
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Rate-limit auth and other expensive routes (`slowapi`: `@limiter.limit("5/minute")`). Uploads have size and content-type limits.

## Audit sweep

Check every row against the code in scope:

| Vulnerability | Look for |
|---|---|
| IDOR | A resource fetched by an id the token doesn't own; an unscoped query |
| SQL injection | String-built SQL; `text()` with f-strings |
| XSS | Unescaped user content rendered as HTML (`dangerouslySetInnerHTML`, markdown without sanitising) |
| CSRF | Cookie-authenticated state changes without a CSRF token or SameSite |
| Timing attacks | Token or signature compared with `==` |
| Mass assignment | ORM objects updated straight from request dicts |
| Race conditions | Read-then-write without a constraint, lock or single transaction |
| Data leakage | Secrets or PII in logs, errors or responses |
