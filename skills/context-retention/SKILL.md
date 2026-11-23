---
name: context-retention
description: Project memory kept in context.md at the repo root. Use before the first code task of a session when no project context is loaded yet, when the user asks to create context.md or onboard a project, or when they ask to update or sync it.
---

# Context retention

`context.md` is the project's **handoff note**: what the next session needs and cannot get by reading the repo. Write it for a capable teammate who has never seen the project: they can read the code, but not your mind.

So it records only what the environment cannot answer: the purpose, where the work stands, what's next, why things are built the way they are, and the gotchas. File trees, routes, models, dependencies and env vars already live in the repo (the directory layout, router files, `package.json` / `pyproject.toml`, `.env.example`). context.md points at them rather than copying them, so it cannot go stale. When the repo has a `CLAUDE.md` or `AGENTS.md`, that file owns conventions and commands, and context.md links to it.

Look for `context.md` in the repo root, then take the matching branch.

## Load (file exists)

1. Read `context.md` in full, plus anything it marks as required reading.
2. Post one line: `✅ Context loaded: **<project>**: <purpose>. Now: <current status>. Next: <top item>.`
3. Go straight into the user's task, building on what the note says.

Done when the line is posted and you are working on the user's request.

## Create (file missing)

1. Draft from the repo first: README, manifest files, top-level layout, `CLAUDE.md` / `AGENTS.md`, recent `git log`.
2. Ask the user, in one message, only for what the repo cannot tell you: the problem and who it's for, current status, what's next, and any decisions or gotchas worth recording. If they paste a README or planning doc, mine it instead.
3. Write `context.md` from [template.md](template.md).
4. Tell the user: `✅ context.md created. Say "load context" at the start of a session to pick it up.`

Done when every template section is filled in or marked `TBD: <what's missing>`.

## Update (after each task, or on "update context" / "sync context")

Before reporting a finished task, check whether it changed anything the note owns:

| The task… | Section |
|---|---|
| finished a feature or hit a milestone | Current status |
| set a new next step or changed priorities | What's next |
| chose between alternatives for a reason | Key decisions |
| hit a trap, workaround or surprising behaviour | Gotchas |
| added a top-level area, entry point or external service | Where things live |

When no row applies (a refactor, a small fix, one more route in an existing area), the note stays as it is. When a row applies, edit only that section, replace any earlier decision the task made wrong (saying why), bump `Last updated`, and close with `✅ context.md updated: <what changed>.`

On an explicit "update context" or "sync context", run the table across everything done since the note was loaded, and **prune**: delete lines that no longer hold. Confirm with the list of changes.

Done when every row the work touched is recorded and no line in the note contradicts the code.
