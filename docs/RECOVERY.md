# Recovery and workload verification

## Define the health contract before patching

| Check | Baseline and success evidence | Failure meaning |
|---|---|---|
| Target identity | Correct host, service, release, image/runtime | Wrong target or deployment |
| Local process | Expected unit/process and readiness state | Startup/supervisor issue |
| Origin request | Expected status, content, and latency | App/reverse proxy issue |
| Public request | Correct DNS/TLS/routing, response content | Edge, cache, DNS, or routing issue |
| Functional flow | A representative API/login/form/worker flow | Business behavior regressed |
| Dependencies | Database/cache/queue access and lag | Partial availability |
| Telemetry | Error rate, latency, resources, restart counts | Degradation after startup |
| Security activation | Fixed artifact active; applicable rescan complete | Installed but inactive or unverified fix |

Set expected status codes per endpoint. A redirect can be correct for a website; it is not proof an API health endpoint works. A cached public 200 can conceal a failed origin. A port probe only proves a listener. Avoid exposing secrets in URLs or command logs.

Example read-only HTTP probe (replace the illustrative URL):

```bash
curl --connect-timeout 5 --max-time 15 --silent --show-error \
  --output /dev/null --write-out '%{http_code} %{time_total}\n' \
  https://service.example/health
```

This prints status and elapsed time; the operator must compare both with agreed criteria and check body content separately. Do not disable TLS verification. Authentication should use the existing secure test harness rather than tokens pasted into chat/history. A functional test that creates data needs an approved test account, cleanup, and protection from billing/email side effects.

Set concrete abort criteria: for example, a failed readiness check after the normal startup deadline, a failed critical workflow, an error-rate increase over the agreed threshold, or queue lag above its limit. Thresholds and observation duration depend on baseline and workload; this document does not prescribe universal numbers.

## Recovery readiness by layer

| Layer | Retain before changing | Recovery constraint |
|---|---|---|
| App dependencies | Previous built artifact, source revision, manifests/lock, config | Lockfile alone does not restore assets or data |
| Runtime | Previous executable/image, native modules, supervisor config | ABI and state compatibility |
| Container | Old immutable digest/artifact and manifests | Volumes and external state are separate |
| OS packages | Package inventory, config, available old packages, tested host restore | Downgrades may be unsupported or unavailable |
| Config | Versioned copy with ownership, mode, ACLs where required | Restore and syntax validation must precede activation |
| Persistent data | Application-consistent backup, restore procedure, keys | RPO, restore duration, newer writes, and schema compatibility |
| Whole host | Bootable snapshot/rebuild procedure plus all required volumes | Snapshot scope, crash consistency, network identity, credentials |

Store sensitive backups separately with encryption/access control appropriate to the workload. Verify completion and integrity; test a restore on an isolated target and record the result. A successful backup command alone does not prove a usable restore. Document RTO (time to recover) and RPO (acceptable data loss) with the owner.

A filesystem copy of a live database or a `docker commit` is not an application-consistent backup. An image registry is not a volume backup. A cloud snapshot may omit separate disks and cannot recover writes made after its recovery point.

## Decision when a change fails

1. Stop further hosts/layers. Keep the failed instance out of traffic if redundancy and capacity permit.
2. Record first failure time, current artifact, commands and exit codes, relevant redacted logs, user impact, and current writes/state. Do not destroy evidence to make the dashboard green.
3. Decide with the named operator whether the approved rollback is still safe. If a migration or state change makes old code incompatible, stop and use the pre-approved state recovery/forward-fix procedure; do not blindly downgrade.
4. Redeploy the retained prior artifact/config or restore the host/state via the rehearsed procedure. A destructive state restore needs the plan's explicit authorization and write-loss decision; a generic “rollback approved” is insufficient.
5. Re-run the same health contract and record observed recovery time and any lost writes. A rollback command exiting zero is not recovery evidence.
6. Keep the change open as failed/rolled back. Reopening traffic, continuing the rollout, or applying a different fix requires the scope and health decision to be recorded.

## Recovery handoff packet

Record incident/change ID, target IDs, operator and owner, last known-good artifact and time, current artifact, backup IDs and scope, accepted RPO/RTO, console access procedure (no credentials), exact next actions, completed/failed checks, active user impact, and abort conditions. Store the packet somewhere accessible if the target and agent both stop.
