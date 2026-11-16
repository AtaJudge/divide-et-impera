# divide-et-impera

A Claude Code skill for large tasks. It splits the work into parts and gives each part to the cheapest model that can do it safely. The orchestrating model writes the critical parts itself, verifies what the other models return, and reports to you.

## How it works

| Role | Model | Does |
|---|---|---|
| Orchestrator | The session model (Fable / Opus) | Plans, writes specs, does the **critical work**, verifies, reports |
| `dei-deputy` | Opus | Optional middle manager that runs one large workstream |
| `dei-builder` | Sonnet | Substantial but non-critical work: code built to a spec, tests, docs |
| `dei-scout` | Haiku | Simple, isolated work: research, collecting sources, parsing, small scripts |

### Criticality test

A piece of work is critical if any answer is yes:

1. **Irreversible:** is a mistake hard to undo?
2. **Security:** does it touch a trust boundary?
3. **Blast radius:** would a mistake hit many users or systems?
4. **Silent failure:** could it be wrong without anyone noticing?
5. **Foundation:** will other work be built on it?
6. **Untestable here:** can it not be verified automatically in this environment?

When in doubt, the work counts as critical. To mark extra areas as critical for one project, list them in its `CLAUDE.md` under the heading `Critical in this project`. `examples/CLAUDE.md` shows the format.

### Behavior by session model

- **Fable** writes critical work itself. In `balanced` mode, Fable writes the spec, Opus writes the implementation, and Fable reviews it line by line.
- **Opus** writes critical work itself.
- **Sonnet or Haiku** hands critical work to an Opus subagent along with a spec, then reviews the result.

## Installation

### As a plugin (recommended)

In Claude Code 2.1.275 or later, run:

```
/plugin install divide-et-impera --marketplace AtaJudge/divide-et-impera
```

On older versions, add the marketplace first, then install:

```
/plugin marketplace add AtaJudge/divide-et-impera
/plugin install divide-et-impera@divide-et-impera
```

Claude Code adds the plugin's name as a prefix to everything it installs:
- The command is `/divide-et-impera:divide-et-impera`.
- The agents are `divide-et-impera:dei-scout`, `divide-et-impera:dei-builder` and `divide-et-impera:dei-deputy`. The skill accepts both these names and the short ones.

The plugin has no version number, so every new commit counts as an update. Run `claude plugin update`, or use the `/plugin` menu, to install updates.

### Manual: personal (all projects)

```bash
git clone https://github.com/AtaJudge/divide-et-impera.git
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r divide-et-impera/skills/divide-et-impera ~/.claude/skills/
cp divide-et-impera/agents/*.md ~/.claude/agents/
```

### Manual: single project

Copy the same files into the project's `.claude/skills/` and `.claude/agents/` folders and commit them. Use this method for cloud sessions (claude.ai/code).

## Usage

```
/divide-et-impera <task>
/divide-et-impera balanced <task>     # lower-cost mode for Fable sessions
```

If you installed it as a plugin, the command is `/divide-et-impera:divide-et-impera` instead.

The skill runs only when you invoke it yourself. It sets `disable-model-invocation: true`, so Claude cannot start it on its own and run up subagent costs you didn't ask for.

## Known limits and notes

- **Subagent nesting depth:** subagents can nest up to three layers deep by default; change this with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. This skill uses at most two layers: orchestrator → deputy → worker.
- **Model inheritance:** a subagent with no explicit model runs on its parent's model. For that reason the skill only delegates to the `dei-*` agents, whose definitions set the model. Run `/tasks` to see which model each subagent is running on.
- **`dei-scout` has Bash** so it can run small scripts. Its prompt tells it to stay read-only, but nothing at the tool level enforces this. For a hard limit, add `permissions.deny` rules in settings.
- **Pricing**, per 1M input/output tokens at the time of writing:

  | Model | Input | Output |
  |---|---|---|
  | Haiku 5.5 | $0.10 | $0.50 |
  | Sonnet 5.5 | $2 | $10 |
  | Opus 5.5 | $4 | $20 |
  | Fable 5.2 | $8 | $40 |
