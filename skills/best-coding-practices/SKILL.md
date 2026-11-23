---
name: best-coding-practices
description: Coding standards for Python/FastAPI backends and React/TypeScript frontends, built on one layered module layout (router → service → repository). Use when writing, reviewing or refactoring Python or React/TS code, laying out a new project or module, or auditing security or database access.
---

# Best coding practices

**The One Pattern**: every module uses the same layers, file layout and rules, so a reviewer can predict where any piece of logic lives before opening a file. When the task touches a module that breaks the pattern, bring that module into line and say so in your summary. Other modules stay as they are.

Read the reference for the work in front of you before writing code:

| Work | Read |
|---|---|
| Models, queries, sessions, transactions, indexes, migrations | [references/data-layer.md](references/data-layer.md) |
| Routes, dependencies, schemas, async, settings | [references/api-layer.md](references/api-layer.md) |
| Auth, secrets, CORS, rate limits, a security audit | [references/security.md](references/security.md) |
| React / TypeScript | [references/frontend.md](references/frontend.md) |

## The One Pattern

One-directional layers:

```
Router ──► Service ──► Repository ──► Models ──► Database
(HTTP)    (business)   (SQL only)     (tables)
```

- **Router**: HTTP only. Parse input, run the auth dependency, call the service, map domain exceptions to HTTP. A **thin router**: past ~15 lines in a route body, logic is leaking into it.
- **Service**: business logic. Orchestration, validation rules, AI and external calls. Talks to repositories and external clients.
- **Repository**: the only place SQL lives, in SQLAlchemy 2.0 `select()` style. Returns ORM objects or plain dicts.
- **Models**: SQLAlchemy 2.0 typed declarative models (`Mapped` / `mapped_column`).

### Layout: one package per domain

```
app/
├── main.py           # app factory, middleware, router wiring only
├── config.py         # Settings (pydantic-settings)
├── database.py       # async engine, session factory, Base
├── security.py       # auth/JWT + access-control dependencies
└── <domain>/         # one package per domain concept
    ├── router.py         # this domain's APIRouter
    ├── schemas.py        # pydantic request/response models
    ├── models.py         # SQLAlchemy models for this domain's tables
    ├── service.py        # business logic
    ├── repository.py     # SQL for this domain's tables
    ├── dependencies.py   # FastAPI dependencies (validation chains)
    ├── exceptions.py     # domain exceptions
    └── constants.py      # domain constants/enums
```

Organise by domain. Top-level `routers/`, `crud/`, `models/` folders fit only a trivial microservice. Shared infrastructure is the four root files; everything else lives in its domain package.

### Imports

1. Imports follow the layers downward: router → service → repository → models. Each layer imports only from the layers below it.
2. Cross-domain imports use module aliases: `from app.meetings import service as meetings_service`.
3. A leading `_` means module-private. When a second module needs it, make it public in the owning domain.

### The three security rules

These are structural, so they apply to every route and query you write:

1. **Identity comes from the verified JWT** (`sub`). A `user_id` from the path or body is input, not identity. Comparing it to the token or ignoring it is the IDOR defence.
2. **Every sensitive route runs the auth dependency.** Public routes are an explicit, reviewed exception.
3. **Every query is scoped** to its tenant or owner (`organization_id`, `discovery_id`, …) in the repository, and access to that scope is checked first thing in the route through one shared helper in `app/security.py`.

## Code discipline

- Files ~300 lines max: split by sub-domain (`guides/router.py` stays; generation logic moves to `guides/generator.py`). Functions ~40 lines max, with helpers named by intent.
- One concept per file: one APIRouter per domain router file.
- Docstrings: one line per module and per public function, saying what it does and, when non-obvious, why.
- Committed code carries only live code: unused code and commented-out blocks get deleted.

## Errors and logging

- Services raise domain exceptions from `<domain>/exceptions.py` (`MeetingNotFoundError`). Routers map them to HTTP once (404/409/422). `HTTPException` below the router is reserved for infrastructure failures (502/503).
- Catch specific exceptions. A best-effort cleanup that swallows an error says so in a comment.
- Log with `logging.getLogger(__name__)` (structlog where the project uses it), as events with context: `guide_generated discovery_id=… version=…`. Logs carry ids, never secrets, tokens or PII payloads.

## Testing and tooling

- Async test client from day 0 (`httpx.ASGITransport`). Tests mirror the layout: `tests/<domain>/test_*.py`.
- Keep pure logic pure and unit-test it without the DB: prompt builders, wire-shape converters, sanitisers, renderers, normalisers. These break silently.
- Auth gets dedicated tests: valid, expired, wrong audience, wrong key.
- New projects: `uv` (`uv sync`, `uv run pytest`), `ruff check --fix` + `ruff format`, `pytest`. Existing projects keep their own tooling.

## Review checklist

Before asking for review, every box is checked against the diff:

- [ ] Every file sits in its domain package, matching the layout
- [ ] SQL appears only in repositories: no `sqlalchemy` import in a router, no `select`/`text()` in a service
- [ ] Imports only go down the layers; no cross-module `_private` imports
- [ ] Files ~300 lines, functions ~40 lines; no dead or commented-out code
- [ ] Every route: auth dependency, scope check first, `response_model`, correct status code
- [ ] Every repository query is scoped; no lookup by primary key alone
- [ ] One commit per request, at the session boundary
- [ ] Validation at the pydantic boundary; route bodies stay thin
- [ ] Domain exceptions mapped to HTTP in the router; no bare or blanket `except`
- [ ] No secrets in code, logs or migrations
- [ ] Pure-logic tests added or updated; suite green; app boots; touched routes return 401 unauthenticated
- [ ] Schema changes ship as migration files, handed to the project owner to apply
- [ ] Frontend: the [frontend.md](references/frontend.md) checks pass
- [ ] Every changed line traces to the request, or to bringing a touched module into the pattern
- [ ] `python <this skill's folder>/scripts/security_scan.py <changed path>` exits 0 (no CRITICAL or HIGH findings)
