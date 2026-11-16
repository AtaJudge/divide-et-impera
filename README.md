# divide-et-impera

<img src="assets/icon.svg" alt="divide-et-impera icon" width="128">

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

- **Fable** writes critical work itself. In `balanced` mode Fable writes no code at all. It writes specs and reviews the code line by line. Opus writes the critical code, and any fix Fable asks for goes back to the worker that wrote the code.
- **Opus** writes critical work itself.
- **Sonnet or Haiku** hands critical work to an Opus subagent along with a spec, then reviews the result.

When the critical parts are small, `balanced` mode can cost more than default mode, because every fix is a round trip to a worker. See the test results below.

## Test results

The same three-part task was run headless with the plugin loaded through `--plugin-dir`:
- a word-frequency CLI with tests (non-critical);
- a version lookup in the Python docs (simple);
- a function that deletes old files (critical: irreversible, and a security boundary).

| Orchestrator | CLI + tests | Docs lookup | File deletion (critical) | Tests | Cost |
|---|---|---|---|---|---|
| Opus 5.5 | `dei-builder` (Sonnet) | `dei-scout` (Haiku) | Opus itself | 22 / 22 pass | $0.59 |
| Fable 5.2 | `dei-builder` (Sonnet) | `dei-scout` (Haiku) | Fable itself | 33 / 33 pass | $1.28 |
| Fable 5.2, `balanced` | `dei-builder` (Sonnet) | `dei-scout` (Haiku) | Opus, to Fable's spec; Fable reviewed it | 33 / 33 pass | $1.66 |

What the runs showed:
- **Every run** put each part on the intended tier, pinned the right model for each worker, and decided correctly not to use a deputy.
- **Every run** marked a docs citation it could not load as unverified, instead of presenting it as fact.
- **In the `balanced` run**, Fable wrote no code. From the session log:
  - Sonnet wrote every line of the CLI and its tests.
  - Opus wrote every line of the deletion code and its tests.
  - Fable wrote specs, read all the code, and ran the tests and the CLI to check them.
  - The only file Fable wrote was `NOTES.md`, which holds the prose answer to the docs question.
  - Fable's review found nothing to send back, so this run did not exercise the fix round trip.

These are single runs with one task each, so read the costs as rough figures.

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

The plugin is versioned (current: 1.0.0), so installs stay on a release until a new version is published. Run `claude plugin update`, or use the `/plugin` menu, to install updates.

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

## License

MIT. See [LICENSE](LICENSE).
