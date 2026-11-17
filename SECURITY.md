# Security policy

## Reporting a vulnerability

Please report security issues privately through [GitHub's private vulnerability reporting](https://github.com/AtaJudge/divide-et-impera/security/advisories/new), not in a public issue.

Useful reports include:
- what you found and how to reproduce it;
- which version of this plugin and of Claude Code you used;
- the impact you expect, for example an agent getting tools or permissions beyond its definition, or work being routed to an agent it should not reach.

You should get a first response within a week.

## Scope

This repository contains prompts and agent definitions, not executable code. In scope:
- instructions that could lead an agent to take actions beyond its stated role;
- agent definitions that grant broader tools than documented;
- documentation that recommends unsafe settings.

Out of scope: vulnerabilities in Claude Code itself. Report those to Anthropic.
