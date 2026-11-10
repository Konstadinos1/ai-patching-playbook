# Contributing

Contributions should make the procedure safer to operate and easier to verify. Read [the support boundaries](docs/SUPPORT.md) and [agent instructions](AGENTS.md) before changing behavior. Report sensitive issues through [SECURITY.md](SECURITY.md).

## Propose a focused change

Use a topic branch and pull request. Explain the problem, intended operator-visible behavior, affected files, and operational implications. For a new workflow, identify its platform/tool assumptions, inputs, approval requirements, automatic side effects, success evidence, abort criteria, and realistic recovery limits.

Do not add an unattended mutation to the inventory collector. Document new network calls, cache writes, privilege requirements, or external data disclosure explicitly. Prefer installed tools and standard-library tests; justify new dependencies and pin third-party CI actions to reviewed commit IDs.

## Verify before submitting

Install Bash, Python 3, Git, and ShellCheck using your development environment's normal package process. Run this from the repository root; the check command does not install tools:

```bash
bash scripts/check.sh
```

This runs Bash syntax checks, ShellCheck, isolated unit tests, offline inline Markdown path/anchor checks, and Git whitespace validation. It does not contact external links or check reference-style Markdown links. Use the [CI workflow](.github/workflows/quality.yml) as the reference for runner settings and inspect each run's tool versions. Report a missing local lint tool honestly; a skipped check is not a pass.

Changes to parsing, exit codes, argument handling, or error reporting need behavior tests, including the relevant failure path. Use fake commands and temporary roots. Do not contact package registries, invoke a real Docker daemon, or run production patch commands from tests. Documentation-only changes need link and consistency review rather than tests that simply repeat their wording.

## Review checklist

- Examples are clearly illustrative; target names and secrets are synthetic.
- Approval, backup, rollback, verification, and reporting steps agree across affected documents.
- Security findings trace to evidence; image age and package age are not treated as vulnerability proof.
- New behavior preserves unknown/error states and documents incomplete coverage.
- Claims distinguish automated tests, local smoke checks, and actual target validation.
- The PR records checks run, limitations, and any operator-visible compatibility change.

## Evidence and licensing

Keep private logs and actual host inventories out of commits and issues. Use advisory references and small redacted reproductions when needed. Screenshots and terminal recordings also need review for credentials and identifying data.

The README documents an unresolved license-file gap. This contribution guide does not resolve that gap or add licensing terms. Any license change needs an explicit maintainer decision.
