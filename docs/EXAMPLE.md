# Worked example — a single-service Compose patch

This scenario and every version, time, count, and health measurement below are fictional. They demonstrate the evidence flow and are not an advisory, executable production plan, or claim about this repository's infrastructure. No CVE or image digest is invented as if verified.

## Intake

A single Ubuntu host serves an API through Nginx. Compose runs the API and a database. The agent operates in advise mode; the operator executes commands. The approved scope is the API image only, with no schema/config/runtime/OS change. A five-minute interruption allowance is available during a stated local-time maintenance window. The operator has cloud console access independent of the host.

## Discovery and assessment

Local inventory identifies the API service, current image identity, listeners, disk headroom, and boot context. A separately authorized image scan supplies finding `F-01`, an advisory URL, affected package/version, fixed package/version, scanner version/database timestamp, and the actual affected image digest. Those real fields must be populated in a live plan.

The owner confirms the dependency is deployed and the relevant API path is reachable. KEV lookup status is recorded from the real catalog; unknown lookup is not labeled absent. A target image from the expected publisher is scanned, and the targeted finding is no longer reported. There is no claim that all vulnerabilities are resolved.

## Baseline and plan

- Public and direct-origin `/health` return the expected status and body.
- A synthetic API request succeeds using an approved test account without external side effects.
- Queue lag, error rate, and latency are recorded under representative traffic.
- The old image artifact and matching Compose revision are retained. No migrations run at startup; state remains backward compatible.
- Database backup scope and restore evidence are recorded even though this change does not intentionally modify the database. Destructive restore is not part of ordinary image rollback.
- Staging test evidence confirms the target's startup behavior and critical requests.

The plan pins the API to the real verified target digest in a reviewed override. It lists pull/recreate commands for the actual Compose project, anticipated service interruption, a normal startup deadline, observation period, and exact restore-to-old-image commands. The database is excluded from recreation. An owner approves this plan revision and window before pull/deployment.

## Execute and verify

The operator pulls the pinned image and recreates only the API service. The report retains actual commands, exit statuses, UTC times, and deployment identity. The operator checks running image ID, readiness, origin/public body and status, the functional request, and queue/telemetry behavior.

Suppose the fictional run takes 18 seconds of externally measured unavailability, the API becomes ready within the planned deadline, and the agreed observation period shows no regression. The report records those observations, not an estimate relabeled as measured downtime. The advisory-aware rescan and deployed digest together support the disposition of `F-01`.

## Failure branch

If readiness misses the deadline or the functional request fails, the operator stops. Because there was no schema change and the old image/config is retained, the approved recovery is to restore the old manifest/image and recreate only the API. The same health contract must pass after recovery. Status becomes **rolled back**, even if service health recovers; `F-01` remains open with exposure, mitigation, owner, and deadline.

If an unexpected migration occurred, simple image rollback is no longer assumed safe. The operator preserves evidence and escalates through the state recovery/incident decision in [RECOVERY.md](RECOVERY.md), rather than blindly running the old application against changed data.

## Closure

The report separates artifact installation, activation, workload health, and security evidence. Any unrelated OS findings, unscanned Python environments, or remaining container advisories are deferred explicitly. The next check covers delayed jobs and traffic patterns outside the initial observation period.
