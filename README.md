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

Every scenario was run headless (`claude -p`), with the plugin loaded through `--plugin-dir` unless noted otherwise. Who did what comes from each session's log, and the generated tests were re-run after each session. Each scenario ran once, so read the costs as rough figures.

**Standard task**, used unless noted. It has three parts:
- a word-frequency CLI with tests (non-critical);
- a Python docs version lookup (simple);
- a function that deletes old files (critical: irreversible, and a security boundary).

### Orchestrator models and modes

| # | Scenario | Who did the critical part | Other parts | Tests | Cost | Result |
|---|---|---|---|---|---|---|
| 1 | Opus 5.5 | Opus itself | Sonnet builder, Haiku scout | 22/22 | $0.59 | ✅ |
| 2 | Fable 5.2 | Fable itself | Sonnet builder, Haiku scout | 33/33 | $1.28 | ✅ |
| 3 | Fable 5.2, `balanced` | Opus (Fable wrote no code) | Sonnet builder, Haiku scout | 33/33 | $1.66 | ✅ |
| 4 | Sonnet 5.5 | Escalated to an Opus subagent | Sonnet builder, Haiku scout | 29/29 | $0.58 | ✅ |
| 5 | Haiku 5.5 | Escalated to an Opus subagent | Sonnet builder; Haiku did the lookup itself | 30/30 | $0.41 | ✅ |
| 6 | Opus 5.5, `balanced` | A second Opus subagent | Sonnet builder, Haiku scout | 32/32 | $1.14 | ⚠️ fixed |

### Installation and configuration

| # | Scenario | Expected | Observed | Cost | Result |
|---|---|---|---|---|---|
| 7 | Manual copy (short agent names, `/divide-et-impera`) | Same as the plugin install | Found `dei-builder` and `dei-scout` by their short names; 24/24 tests | $0.64 | ✅ |
| 8 | Skill installed without its agents | Say so; do not fall back to built-in agents | Reported the missing agents, did everything itself, and listed which tier each part would have gone to; 23/23 tests | $0.48 | ✅ |
| 11 | `Critical in this project` in CLAUDE.md marks the CLI as critical | The orchestrator writes the CLI | Opus wrote the CLI and the deletion code itself; only the lookup went to the scout; 25/25 tests | $0.62 | ✅ |

### Task shapes

| # | Scenario | Expected | Observed | Cost | Result |
|---|---|---|---|---|---|
| 9 | One-line edit | No subagents | No subagents; edited the file directly | $0.18 | ✅ |
| 10 | Large task in two workstreams (Fable): 7 lookups and 5 modules | Delegate both; deputy only if worth it | One scout and two builders; no deputy, since the thresholds were not met; 42/42 tests | $1.36 | ✅ |
| 12 | Fable `balanced`, with a gap planted in the first spec | The gap goes back to Opus | Two rounds with the same Opus worker; Fable wrote no code; 20/20 tests | $1.24 | ✅ |
| 13 | Deputy forced, default environment | Deputy starts its own workers | The deputy had no Agent tool at runtime, so it stopped and reported this without working around it | $0.68 | ⚠️ see below |
| 13b | Same, with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=2` | Deputy starts its own workers | Orchestrator → Opus deputy → two Sonnet builders; 39/39 tests | $0.84 | ✅ |

### What the tests changed

- **#6: `balanced` on Opus.** Opus handed the critical code to a second Opus, which cost about twice as much as #1 for the same result. `balanced` now applies to Fable only; other models ignore it and say so.
- **#13: the deputy layer.** In the test environment, subagents did not get the Agent tool by default, although the Claude Code docs say three levels of nesting are allowed by default. The deputy layer worked once `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` was set to `2` (#13b). The skill now:
  - has the deputy check for the Agent tool first and report back if it is missing;
  - falls back to the flat structure;
  - tells the user to set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=2` to turn the deputy layer on.
- **In every run** with web research, the docs site was blocked by the test environment's network. Every run marked the citation as unverified instead of presenting it as fact.
- **No worker in any run** went outside its brief or worked around a denied command.

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

- **Deputy layer needs nesting:** if `dei-deputy` reports that it has no Agent tool, add `"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2"` to the `env` block of your settings. Without it, the skill falls back to a flat structure.

- **Subagent nesting depth:** this skill uses at most two layers: orchestrator → deputy → worker. The Claude Code docs say subagents can nest up to three layers by default, but in testing nesting was off until `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` was set (see above).
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
