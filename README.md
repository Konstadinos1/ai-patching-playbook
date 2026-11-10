# AI Patching Playbook

An operating procedure for AI-assisted Linux webserver patching: inventory the workload, assess real findings, approve a bounded change, prepare recovery, patch one layer, verify the workload, and preserve evidence.

Targets Debian/Ubuntu hosts with systemd, Docker Compose, Node.js, and Python. Other distributions and orchestrators require adapted commands. This repository supplies guidance and an inventory script; prompts alone cannot enforce permissions or guarantee uptime.

## Start here

1. Read [HOWTO](HOWTO.md), identify the service owner, and confirm recovery access.
2. Run `bash scripts/audit.sh` as your normal account. Local inspection does not install packages or restart services. Access failures remain unknowns.
3. Review and redact output before sharing. Optional dependency scans contact registries and can write caches; see [technical details](docs/TECHNICAL.md).
4. Fill the [change plan](templates/CHANGE_PLAN.md). Give the agent [PROMPT.md](PROMPT.md), the plan inputs, and the audit.
5. Approve exact scope and side effects. Verify recovery prerequisites, execute one bounded batch, and compare workload health against baseline.
6. Complete the [change report](templates/CHANGE_REPORT.md), including incomplete checks and deferred findings.

```bash
# Local inventory; no automatic sudo or registry scans.
bash scripts/audit.sh

# Explicit app root; authorize npm registry traffic and possible cache writes.
bash scripts/audit.sh --app-root /srv/api --network-scans
```

## Documentation map

| Document | Purpose |
|---|---|
| [HOWTO](HOWTO.md) | Lifecycle, roles, gates, and completion criteria |
| [Workflow runbooks](docs/WORKFLOWS.md) | OS, reboots, Compose, Node, Python, emergencies, recurring reviews |
| [Technical breakdown](docs/TECHNICAL.md) | Trust boundaries, scanner semantics, audit behavior and limits |
| [Recovery and verification](docs/RECOVERY.md) | Backups, health contracts, abort decisions, incident handoff |
| [Worked example](docs/EXAMPLE.md) | A fictional change from finding to closure |
| [Agent prompt](PROMPT.md) | Instructions for advise and execute modes |
| [Change plan](templates/CHANGE_PLAN.md) | Evidence, commands, approval, and recovery prerequisites |
| [Change report](templates/CHANGE_REPORT.md) | Before/after evidence, observed health, and deferred work |

## Operating modes

**Advise:** the agent proposes commands; an operator executes them and returns output. Proposed commands are never reported as executed.

**Execute:** the agent inspects the target and performs the explicitly approved change. Restrict its account, tools, and network separately from the prompt. Installation can run maintainer scripts and restart services; approval must cover those effects before installation begins.

Prioritize verified exploitation, exposure, and workload impact. Use a workload baseline, preserve old deployable artifacts and state recovery, and stop on unexpected scope changes or health regressions. Host release upgrades and database major upgrades need separate approved procedures.

## Validation

When changing workflows, keep the prompt and templates consistent. When changing the script, run:

```bash
bash -n scripts/audit.sh
python3 -m unittest discover -s tests -v
git diff --check
```

## License

The original README states MIT licensing. No LICENSE file is currently present; the maintainer should add the intended license text to make redistribution terms explicit.
