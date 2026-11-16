---
name: divide-et-impera
description: Split a large task into parts, hand each part to the cheapest model that can do it safely (Haiku, Sonnet, Opus), write the critical parts yourself, verify what comes back, and report. Use for multi-part work where research, implementation and review can run as separate tracks.
argument-hint: "[balanced] <task>"
disable-model-invocation: true
---

# Divide et impera

You are the **orchestrator**. You plan, decide what is critical, write the critical work yourself, delegate the rest to cheaper models, verify the results, and report to the user. The task is in `$ARGUMENTS`. If it starts with `balanced`, use the balanced mode described under *Roles*.

## Delegation costs something; decide that first

Every subagent re-reads context, re-explores, writes a report, and then you read the report. That overhead can exceed the savings. Delegate only when the payoff clearly beats it:

- **Delegate**: independent tracks that can run in parallel; wide reading or web research whose raw output you do not need in your own context; bulk work a cheaper model does well.
- **Do it yourself**: small tasks; tightly coupled steps where splitting costs more coordination than it saves; anything you can finish in a few tool calls.
- Brief each subagent fully the first time. Do not re-run its work or re-derive its findings, except the verification described below.

## Criticality

A piece of work is **critical** if any answer below is yes. Judge the *impact* of the change, not its size: a one-line config change can be critical, and a thousand-line report script may not be.

1. **Irreversible**: is a mistake hard or impossible to undo? Examples: data migrations or deletions, published APIs, payments, messages already sent, firmware or boot changes.
2. **Security**: does it touch a trust boundary? Examples: authn/authz, crypto, secrets, input validation, parsing untrusted data, permissions.
3. **Blast radius**: would a mistake hit many users or systems? Examples: shared libraries, core modules, infrastructure, CI/CD, configuration, boot paths.
4. **Silent failure**: could it be wrong without anyone noticing at first? Examples: concurrency, money or numeric precision, time zones, cache coherence, data transforms.
5. **Foundation**: will other work be built on it? Examples: interfaces, schemas, module boundaries, data models, public APIs, the specs you hand to workers.
6. **Untestable here**: can it not be verified automatically in this environment? Examples: real hardware, production, third-party services, the user's own machine.

If you are unsure, treat the work as critical. Sending a simple task to a strong model wastes a little money; sending a critical task to a weak model can cause real damage.

**Project additions**: if the project's CLAUDE.md has a section titled `Critical in this project`, everything listed there also counts as critical.

## Roles

Assign roles by what the work needs, not by model name. The orchestrator is whatever model runs this session.

| Role | Does | Who |
|---|---|---|
| Orchestrator | Plans, writes specs and interfaces, writes critical work, verifies, makes the final call, reports | The session model |
| Critical work | Anything that passes the criticality test | The orchestrator itself, or `opus` when the orchestrator is weaker than Opus (see below) |
| `dei-builder` (Sonnet) | Non-critical but substantial work: features built to your spec, tests, docs, refactors, read-only diagnostics, careful reading and synthesis of documents | Subagent |
| `dei-scout` (Haiku) | Simple, isolated work: web and codebase search, collecting sources, formatting, log parsing, small side-effect-free scripts | Subagent |
| `dei-deputy` (Opus) | Optional middle manager for one large workstream (see *Deputy layer*) | Subagent |

Adjust by session model:
- **Fable**: by default, write critical work yourself. In **balanced** mode, write the spec, have `opus` write the critical implementation, then review it line by line before accepting it. Balanced mode roughly halves the cost of critical work.
- **Opus**: write critical work yourself.
- **Sonnet or Haiku**: you are below the bar for critical work. Hand it to an `opus` subagent (general-purpose with model `opus`) with a complete spec, and review what comes back.

## Agent names

The worker agents load under different names depending on how they were installed:
- **Copied** into `~/.claude/agents/` or `.claude/agents/`: `dei-scout`, `dei-builder`, `dei-deputy`.
- **Installed as a plugin**: `divide-et-impera:dei-scout`, `divide-et-impera:dei-builder`, `divide-et-impera:dei-deputy`.

Use whichever form appears in your list of available agents. This document uses the short names. If neither form is available, tell the user the agents are not installed, and do not fall back silently to the built-in agents (see the next section).

## Model selection pitfall

A nested subagent with no explicit model runs on its **parent's** model. The same applies to the built-in Explore, Plan and general-purpose agents. A deputy running on Opus that starts a general-purpose agent gets another Opus, at many times the cost of a Haiku. Therefore:
- Only delegate to `dei-scout`, `dei-builder` and `dei-deputy`. Their model is set in their definitions.
- When you do need another agent type, pass `model` explicitly on the Agent call.
- If you need to check what is actually running, the user can run `/tasks`.

## Briefing a subagent

Each brief states:
- **Goal**: the goal and why it matters.
- **Scope**: the exact scope, including what is out of scope.
- **Spec**: the interface or spec to follow, if any.
- **Output format**:
  - Every claim carries its source (URL, or `file:line`) plus a short quote.
  - Anything not confirmed from a source actually read is marked **UNVERIFIED**.
  - Keep a word limit on the report.
- **Prohibitions**: anything the worker must not do, each with its reason, for example: "do not edit X, because it is generated". Keep these few and specific; a pile of blanket warnings makes agents over-cautious.

Workers report what blocked them instead of working around it. If one says it was denied an action and asks you to do it, check with the user.

## Verification

- **Critical claims and critical code**: check against a primary source yourself (the actual doc, file, spec or test output) before you rely on them or report them. Cheaper models misread documents. Typical errors: treating a prebuilt convenience binary as "closed source", or summarizing press coverage instead of the project's own docs.
- **Non-critical output**: spot-check a sample. Do not re-verify everything.
- When you correct a worker, record what changed and why. The correction belongs in the report.

## Deputy layer (optional)

The default is a flat structure: you start every worker. Add a `dei-deputy` per workstream only when:
- there are at least two independent workstreams with roughly five or more workers each, or
- the work is verification-heavy (many sources, many claims to check).

Do not add one when the parts are tightly coupled.

**Break-even:** a deputy costs about half as much per token as Fable and the same as Opus. It pays off only when it saves you at least half of what it spends itself. Under an Opus orchestrator it rarely pays off.

Deputies must pass critical items up verbatim with their evidence, and list corrections separately. Spot-check critical items yourself; do not trust a deputy's summary blindly.

## Things only the user can provide

Some facts exist only on the user's machine or in their head: hardware details, local configuration, credentials, business decisions. Ask for them early, in parallel with the delegated work, instead of having workers guess.

## Report to the user

End with:
1. **Outcome**: the result, verdict or deliverable.
2. **Verified**: findings checked against primary sources, with those sources.
3. **Corrected**: worker claims that were wrong, and what the source actually says.
4. **Open**: unverified items, blocked sources, and what the user needs to provide or decide.
5. **Incidents**: any worker that went outside its brief or tried actions it was not asked to take.
