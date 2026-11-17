# Contributing

Thanks for helping improve divide-et-impera.

## Before you open a pull request

- **Open an issue first** for anything beyond a typo, so we can agree on the change.
- **Keep instructions goal-based.** The skill and agents state goals and constraints rather than step-by-step scripts; newer models do better with that. Give every prohibition its reason.
- **Back behavior claims with a run.** If a change affects routing, criticality or verification, run the affected scenario headless and include the result in the PR:

  ```bash
  claude -p "/divide-et-impera:divide-et-impera <task>" --plugin-dir . --output-format stream-json --verbose
  ```

  Say which model ran each part and whether the generated tests pass.
- **Do not invent numbers** in the README. Test results there come from real runs.

## Checks

CI runs `claude plugin validate .` and a frontmatter check on every push and pull request. Run the validator locally before pushing:

```bash
claude plugin validate .
```

## Developing the plugin with itself

If you load this repository as a plugin (`--plugin-dir .`) while editing it, Claude Code treats the plugin's own files as sensitive and asks before writing them. In headless runs nobody can approve, so the write is refused. Edit in an interactive session, or load the plugin from a separate copy.

## License

By contributing, you agree that your contributions are licensed under the MIT License.
