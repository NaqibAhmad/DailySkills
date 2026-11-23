# Coding Skills

Some of the skills that I use during my coding sessions. Some are personally built and some are taken from the internet.

Each skill is a folder with a `SKILL.md` in the open [Agent Skills](https://agentskills.io) format, so the same files work in Claude Code and in other agentic tools that read skills (Codex, Cursor, Gemini CLI, OpenCode and others).

## The skills

| Skill | What it does | Source |
|---|---|---|
| [context-retention](skills/context-retention/SKILL.md) | Keeps a `context.md` handoff note at the repo root: loads it at the start of a session, creates it when missing, and updates it after tasks that change status, decisions or gotchas. | Personally built |
| [best-coding-practices](skills/best-coding-practices/SKILL.md) | Coding standards for Python/FastAPI backends and React/TypeScript frontends, built on one layered layout (router → service → repository). Includes reference docs for the data, API, security and frontend layers, a review checklist, and a `security_scan.py` script. | Personally built |
| [karpathy-guidelines](skills/karpathy-guidelines/SKILL.md) | Behavioural guardrails against common LLM coding mistakes: think before coding, keep it simple, make surgical changes, and define verifiable success criteria. | From the internet: based on [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876), via [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) |
| [writing-for-agents](skills/writing-for-agents/SKILL.md) | How to write documents agents read (skills, `AGENTS.md`, `CLAUDE.md`): context pointers, information hierarchy, completion criteria, leading words, and pruning. | From the internet: [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, © Matt Pocock) |

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add NaqibAhmad/DailySkills
/plugin install coding-skills@coding-skills
```

To try it from a local clone without publishing:

```
/plugin marketplace add ./path/to/this-repo
/plugin install coding-skills@coding-skills
```

Plugin skills are namespaced, so they show up as `coding-skills:context-retention` and so on.

### Claude Code (as plain skills)

Copy the folders you want into your skills directory:

```bash
# for every project
cp -r skills/* ~/.claude/skills/

# for one project only
cp -r skills/* .claude/skills/
```

### Other agentic tools

With the [`skills` CLI](https://github.com/vercel-labs/skills), which installs into Claude Code, Codex, Cursor and other agents:

```bash
npx skills add NaqibAhmad/DailySkills
```

Or copy the folders by hand into the tool's skills directory, for example `~/.codex/skills/` for Codex or `.agents/skills/` in a project. `writing-for-agents` also ships an `agents/openai.yaml` with display metadata for Codex.

## Using them

The skills trigger on their own from their descriptions. You can also call them by name:

- **context-retention**: say "load context" at the start of a session, "create context.md" in a new repo, or "update context" after a chunk of work.
- **best-coding-practices**: loads when writing, reviewing or refactoring Python or React/TS code. Run the scanner directly with `python skills/best-coding-practices/scripts/security_scan.py <path>`.
- **karpathy-guidelines**: loads when writing, reviewing or refactoring code.
- **writing-for-agents**: loads when creating or editing skills, `AGENTS.md` or `CLAUDE.md`.

## Repo layout

```
.claude-plugin/
├── plugin.json        # Claude Code plugin manifest
└── marketplace.json   # lets the repo be added as a plugin marketplace
skills/
├── context-retention/
├── best-coding-practices/
├── karpathy-guidelines/
└── writing-for-agents/
```

## Licences

The third-party skills keep their original MIT licences: see [skills/writing-for-agents/LICENSE](skills/writing-for-agents/LICENSE) and the `license` field in [skills/karpathy-guidelines/SKILL.md](skills/karpathy-guidelines/SKILL.md). Credit for those skills goes to their authors.
