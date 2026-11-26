# Change report

- Change ID / approved plan revision:
- Final status: verified complete | partially complete | deferred | failed | rolled back
- Target IDs, environment, layer:
- Operator / owner:
- Actual UTC start/end; local window/timezone:
- Evidence storage, access restrictions, retention:

## Outcome and artifact identity

| Item / finding | Before | Installed after | Active after | Advisory disposition / evidence | Remaining uncertainty |
|---|---|---|---|---|---|
| Fill | Fill | Fill | Fill | Fill | Fill |

An installed version is not proof the running process loaded it. Record scanner version/database freshness, matching scope, and any incomparable before/after results.

## Execution evidence

| UTC time | Command / automation revision | Target | Exit status | Redacted output / evidence reference | Deviation from plan |
|---|---|---|---|---|---|
| Fill | Fill | Fill | Fill | Fill | Fill |

For each proposed write, link the plan step and approval revision to the decision and observed effect. Use the request ID and backend receipt where the interface supplies them. For a human-run command, correlate the operator's timestamped command and exit status with an independent observation of the target. Include denied requests and disputed outcomes.

| Step or request ID / approval ref | Operator or executor identity / policy revision | Decision and dispatch time | Command record or backend receipt / outcome | Independent observation and time | Unresolved discrepancy / owner |
|---|---|---|---|---|---|
| Fill | Fill | Fill | Fill | Fill | Fill |

When the records cannot establish the effect, mark it unknown. Record any reconciliation before retrying. Keep sensitive diagnostics in the approved evidence store and use access-controlled references here.

## Health and observation

| Check | Baseline | Observed after | PASS / FAIL / NOT RUN / UNKNOWN | Evidence |
|---|---|---|---|---|
| Public + origin status/content | Fill | Fill | Fill | Fill |
| Functional request | Fill | Fill | Fill | Fill |
| Dependencies/workers/queues | Fill | Fill | Fill | Fill |
| Error/latency/resource signals | Fill | Fill | Fill | Fill |
| Units, process identity, activation | Fill | Fill | Fill | Fill |
| Applicable security rescan | Fill | Fill | Fill | Fill |

- Restarted services and reason:
- Observed downtime, measurement source, telemetry gaps:
- Observation interval and traffic coverage:
- Pending restarts/reboot and responsible owner:

## Recovery or incident

- Trigger and first failure time:
- Recovery decision/approval; incident reference:
- Restored artifacts/config/state; backup references:
- Observed recovery duration and any lost writes:
- Recovery verification and unresolved impact:

## Deferred work and sign-off

| Finding / unrun check | Residual exposure / reason | Compensating control | Owner | Deadline |
|---|---|---|---|---|
| Fill | Fill | Fill | Fill | Fill |

- Scope deviations and updated approval references:
- Owner acceptance of result and limitations:
- Follow-up review and post-window check:
