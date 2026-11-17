"""Fail if the skill or an agent definition has missing or unparseable frontmatter."""
import glob
import sys

import yaml

REQUIRED = {
    "skill": ("name", "description"),
    "agent": ("name", "description", "model", "tools"),
}

failures = 0
files = [("skill", "skills/divide-et-impera/SKILL.md")]
files += [("agent", f) for f in sorted(glob.glob("agents/*.md"))]

for kind, path in files:
    text = open(path, encoding="utf-8").read()
    problems = []
    if not text.startswith("---\n"):
        problems.append("frontmatter must start on line 1")
    else:
        try:
            meta = yaml.safe_load(text.split("---\n", 2)[1]) or {}
        except yaml.YAMLError as exc:
            meta, problems = {}, [f"frontmatter does not parse: {exc}"]
        problems += [f"missing '{key}'" for key in REQUIRED[kind] if key not in meta]
    if problems:
        failures += 1
        for p in problems:
            print(f"FAIL {path}: {p}")
    else:
        print(f"ok   {path}")

sys.exit(1 if failures else 0)
