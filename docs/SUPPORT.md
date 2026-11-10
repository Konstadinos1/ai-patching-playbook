# Support, validation, and release policy

## Intended scope versus demonstrated validation

| Area | Intended use | What repository checks establish |
|---|---|---|
| Inventory collector | Bash on Debian/Ubuntu Linux; optional installed APT, systemd, socket, and Docker clients | Syntax/lint and isolated command-stub tests; not a full distribution or service integration test |
| npm audit parser | Structured npm audit reports containing the documented severity metadata | Synthetic clean, finding, error, and malformed-result cases; not every npm/registry version |
| Patching guidance | Human-supervised systemd, Compose, Node.js, and Python changes | Documentation consistency and review; no automatic production compatibility guarantee |
| Recovery guidance | Operator-specific artifact, configuration, host, and state recovery | A required planning process; actual backups and restore rehearsals remain deployment-specific |
| Other distributions/orchestrators | Adapted site-specific runbooks | No general compatibility claim; unsupported collection must remain explicit |

See the CI workflow for the exact runner, tool versions, and checks exercised by each run. An Ubuntu CI runner is not proof that every supported Ubuntu release, Docker configuration, package transaction, or reboot path has been tested. A local inventory smoke test does not establish patch or restore safety. Examples are illustrative unless they link to a specific published validation record.

Before production use, validate on a representative non-production host: command permissions, configured Docker context, scanner schema/registry behavior, workload health contract, package-manager side effects, and recovery access. Rehearse recovery using the actual state/backup design.

## Maintenance and compatibility

The default branch is the current development and maintenance target. Contributions and issue handling are best effort; no service SLA, certification, long-term-support branch, or backport schedule is implied.

The audit's command-line flags and documented exit codes are interfaces to review explicitly. Its human-readable output is not a stable machine-readable API. Changes to defaults, opt-in side effects, privileges, coverage labels, or exit-code meaning require an operator-facing compatibility note and updated tests/docs.

## Release checklist

A maintainer preparing a release should:

1. Select an exact commit and verify its CI results. Review all changes since the previous release, especially new side effects and error semantics.
2. Confirm documented intended/tested environments remain accurate. Record tool/platform versions and any integration or restore exercise actually performed, without extrapolating beyond its coverage.
3. Re-run required checks from [CONTRIBUTING.md](../CONTRIBUTING.md), review examples for secrets and unsafe copy/paste behavior, and verify links and template consistency.
4. Review known issues, security fixes, deferred gaps, and licensing status. Resolve licensing terms explicitly before representing a release as licensed for redistribution.
5. Publish release notes with the commit/tag, compatibility changes, operator action, known limitations, and links to validation evidence. For initial releases, choose and document the versioning policy; do not imply a stable API before committing to one.
6. If distributing standalone scripts or archives, identify their source commit and publish checksums for those exact files. Checksums detect mismatch; they do not themselves prove publisher identity.

Creating or merging a PR does not authorize publishing a release or changing production. The maintainer decides when to tag and publish; operators separately approve use on their hosts.
