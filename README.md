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

There are two ways in. The **plugin** is a read-only bundle that updates itself when a new version is released. **[skills.sh](https://skills.sh)** copies editable files into your project or home folder, and you update them by hand. Pick one per agent: installing both gives you every skill twice.

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add NaqibAhmad/DailySkills
claude plugin install coding-skills@coding-skills
```

Or, inside a session: `/plugin marketplace add NaqibAhmad/DailySkills`, then `/plugin install coding-skills@coding-skills`. Add `--scope project` to install for one repo only.

Plugin skills are namespaced, so they show up as `coding-skills:context-retention` and so on.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add NaqibAhmad/DailySkills
codex plugin add coding-skills@coding-skills
```

Updates itself at startup when a new version is released.

</details>

<details>
<summary><strong>GitHub Copilot</strong> (CLI and VS Code)</summary>

```bash
copilot plugin marketplace add NaqibAhmad/DailySkills
copilot plugin install coding-skills@coding-skills
```

To get updates automatically, add this once to `~/.copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "coding-skills": { "source": { "source": "github", "repo": "NaqibAhmad/DailySkills" }, "autoUpdate": true }
  }
}
```

In VS Code, run **Chat: Install Plugin From Source** and enter `https://github.com/NaqibAhmad/DailySkills`.

</details>

<details>
<summary><strong>Gemini CLI</strong> (manual updates)</summary>

```bash
gemini skills install https://github.com/NaqibAhmad/DailySkills.git --path skills
```

Re-run the command to update.

</details>

<details>
<summary><strong>Cursor, OpenCode, Windsurf, Amp and any other agent</strong> (manual updates)</summary>

```bash
npx skills@latest add NaqibAhmad/DailySkills -a <agent>  # cursor, opencode, windsurf, amp, codex, claude-code…; omit -a to choose
```

Add `-g` to install for every project instead of the current one. To update, run `npx skills@latest update`.

</details>

<details>
<summary><strong>By hand</strong></summary>

Copy the folders you want from `skills/` into your agent's skills directory, for example `~/.claude/skills/` for Claude Code, `~/.gemini/skills/` for Gemini CLI, or `.agents/skills/` in a project. `writing-for-agents` also ships an `agents/openai.yaml` with display metadata for Codex.

</details>

## Using them

The skills trigger on their own from their descriptions. You can also call them by name:

- **context-retention**: say "load context" at the start of a session, "create context.md" in a new repo, or "update context" after a chunk of work.
- **best-coding-practices**: loads when writing, reviewing or refactoring Python or React/TS code. Run the scanner directly with `python skills/best-coding-practices/scripts/security_scan.py <path>`.
- **karpathy-guidelines**: loads when writing, reviewing or refactoring code.
- **writing-for-agents**: loads when creating or editing skills, `AGENTS.md` or `CLAUDE.md`.

## Repo layout

```
.claude-plugin/
├── plugin.json        # plugin manifest (read by Claude Code, Codex and Copilot)
└── marketplace.json   # lets the repo be added as a plugin marketplace
skills/
├── context-retention/
├── best-coding-practices/
├── karpathy-guidelines/
└── writing-for-agents/
```

## Releasing a change

Claude Code, Codex and Copilot reinstall the plugin only when the `version` in [.claude-plugin/plugin.json](.claude-plugin/plugin.json) changes. After editing a skill, bump it (for example `1.0.0` → `1.0.1`) in the same commit, or existing installs won't pick up the change.

## Licences

My own skills, `context-retention` and `best-coding-practices`, are MIT licensed: see [LICENSE](LICENSE), which each of those skill folders also carries.

The third-party skills keep their original MIT licences: see [skills/writing-for-agents/LICENSE](skills/writing-for-agents/LICENSE) and the `license` field in [skills/karpathy-guidelines/SKILL.md](skills/karpathy-guidelines/SKILL.md). Credit for those skills goes to their authors.
