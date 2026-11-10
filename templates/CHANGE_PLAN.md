# Change plan

Status: DRAFT — fill all required fields before approval. This template grants no authority by itself.

## Identity and scope

- Change ID / plan revision:
- Target hostname(s), resource IDs, environment:
- OS/release/architecture; service/app roots:
- Operator / service owner / approver / recovery operator:
- Mode: advise or execute
- Layer and explicit allowed changes:
- Excluded changes:
- Maintenance start/end and timezone; maximum interruption:
- Agent/session dependency on target; independent recovery access:

## Evidence and prioritization

| Finding ID | Component / installed version | Advisory or scanner evidence + timestamp | Applicability / exposure / KEV status | Fixed target | Priority / uncertainty |
|---|---|---|---|---|---|
| Fill | Fill | Fill | Fill | Fill | Fill |

Record scanner version/database timestamp, package index freshness, environment/lockfile/image scope, and missing permissions/tools. Do not substitute outdated-package counts for vulnerability evidence.

## Baseline and success contract

| Check / actual command or test harness | Baseline | Success criteria | Abort threshold / startup deadline | Evidence location |
|---|---|---|---|---|
| Target identity | Fill | Fill | Fill | Fill |
| Public + origin endpoint and response content | Fill | Fill | Fill | Fill |
| Critical functional request | Fill | Fill | Fill | Fill |
| Dependencies, workers, queues | Fill | Fill | Fill | Fill |
| Errors, latency, resources, failed units | Fill | Fill | Fill | Fill |
| Artifact activation and security rescan | Fill | Fill | Fill | Fill |

## Ordered execution

| Step | Exact command / automation revision | Target / from-to artifact | Expected side effects (network, files, scripts, restarts) | Expected time / downtime | Check / abort action |
|---|---|---|---|---|---|
| Recovery preparation | Fill | Fill | Fill | Fill | Fill |
| Canary or bounded batch | Fill | Fill | Fill | Fill | Fill |
| Activation | Fill | Fill | Fill | Fill | Fill |
| Observation / remaining wave | Fill | Fill | Fill | Fill | Fill |

Include working directory, account/privilege, file paths, environment selectors (no secrets), service dependencies, and commands required for cleanup. Resolve placeholders before execution. Record staging/build/test evidence and artifact provenance.

## Recovery prerequisites and commands

- Old artifact/digest/package availability and configuration revision:
- Persistent data, volume, and attached-disk coverage:
- Backup IDs/times, consistency method, restore rehearsal evidence:
- RPO / RTO and accepted loss of new writes:
- Schema compatibility and restrictions on old code:
- Exact rollback steps and health verification:
- Rollback trigger, decision owner, and latest safe recovery time:
- Recovery if SSH/agent/host fails; handoff location:
- Exceptions: affected item, unavailable prerequisite, risk, accepting owner:

## Approval record

- Approver and recorded approval reference/time:
- Approved plan revision, target set, artifact versions, layer, window:
- Approved automatic/manual restarts and reboot:
- Approved recovery actions, including any destructive state restore and write-loss decision:
- Explicit exceptions and deferred checks:
- Reapproval triggers: changed scope/version, removals, new services, migration, or expanded downtime.

## Closure and follow-up

- Observation period and post-window check time:
- Report/evidence location and access/retention:
- Remaining findings and owners/deadlines:
