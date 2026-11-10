# Layer-specific workflows

These runbooks implement [the lifecycle](../HOWTO.md). Resolve all placeholders, review commands for the target, and put mutations and side effects in an approved [change plan](../templates/CHANGE_PLAN.md). Examples assume Bash and Debian/Ubuntu where applicable. Do not run every workflow as one change.

## 1. Debian/Ubuntu package security updates

**Inputs:** distribution support status, architecture, enabled repositories, package versions, held packages, index freshness, vendor advisories, baseline, backup, and maintenance window.

1. Inspect `cat /etc/os-release`, `dpkg --audit`, `apt-mark showhold`, `apt-cache policy PACKAGE`, and `apt-get -s upgrade`. Capture the full simulation, not just counts. Resolve broken package state before routine upgrades.
2. Inspect unattended-upgrade/apt timer status and arrange a non-overlapping window. Active package-manager locks mean wait and investigate; never remove the lock files.
3. If approved, run `sudo apt-get update`. If any required repository fails, stop and resolve stale or partial indexes rather than calling the result current.
4. Re-simulate the exact planned transaction, for example `apt-get -s install --only-upgrade PACKAGE`. Review dependency additions, removals, holds, configuration prompts, downloads, storage, and service effects. A targeted package can still change dependencies.
5. Approve the resulting package set and effects. Availability of the old version must be checked before treating downgrade as recovery. Preserve a tested host snapshot/rebuild path when downgrades are unsafe or unavailable.
6. Run the reviewed transaction, for example `sudo apt-get install --only-upgrade PACKAGE`. Do not add `-y`, `--force-*`, broad upgrade scope, or repository changes unless reviewed. Handle config prompts according to the plan and preserve local configuration.
7. Check exit status, `dpkg --audit`, installed package versions with `dpkg-query -W PACKAGE`, affected service state, and workload health. Use installed distribution tools such as `needrestart` according to local policy to identify processes needing restart; do not install new tooling mid-change without approval.
8. Record pending restart/reboot requirements and vendor-specific guidance. Re-run relevant advisory/scanner checks. Do not claim a host is remediated while affected old code still runs.

**Abort:** unexpected removals, failed repository refresh, package transaction failure, config merge uncertainty, unavailable recovery, or health regression.

**Recovery:** follow [the recovery decision](RECOVERY.md). Package downgrades can fail due to repository retention, dependencies, maintainer scripts, and state formats. Restoring only `/var/lib/dpkg` is not a system rollback. Interrupted transactions require package-manager-specific repair under an updated plan; do not reboot blindly.

## 2. Service reload, restart, kernel activation, and reboot

Treat activation as an explicit part of the change, including installation-triggered restarts.

1. Identify affected units and their dependency order, current process/version, supervisor, socket activation, traffic routing, and auto-restart behavior. Validate the relevant configuration before touching the service; for example `sudo nginx -t` for Nginx.
2. Decide reload versus restart from vendor behavior. A config reload may not replace a process mapping an old library. Identify required restart semantics instead of assuming reload activates the fix.
3. For redundancy, drain one instance using the actual load balancer, wait for in-flight work, then restart it. There is no generic drain command that works for every deployment.
4. Run the approved activation, such as `sudo systemctl restart SERVICE`. Verify unit status, fresh process identity, dependency health, external routing, and the functional smoke test before restoring traffic.
5. For reboot, confirm console access, boot disk/free space, `/boot` space, known-good kernel/boot path, encrypted-disk unlock requirements, startup dependencies, and recovery operator availability. Restart the agent's own host/runtime only via a separate operator/session with durable handoff.
6. Reboot only within the approved window. An SSH disconnect is expected but does not prove successful reboot. Reconnect through a new session, compare boot time and `uname -r`, check failed units, mount points, containers, timers/workers, and public/functional health.
7. Measure downtime from external monitoring timestamps. Record gaps and unfinished scans.

**Abort:** no console access, boot risk, unexpected dependency outage, invalid config, or failed canary health. Boot recovery and kernel selection are platform-specific and must be written into the plan beforehand.

## 3. Docker Compose image replacement

**Inputs:** trusted Compose files, project name, service identity, registry authorization, current and target immutable digests, volume/state inventory, startup and health behavior, compatibility, and previous deployable configuration.

1. Inspect `docker compose version`, `docker compose ps`, and `docker ps --no-trunc`. Use narrow `docker inspect --format` fields for image ID/health as needed; full inspection and rendered Compose config can reveal secrets.
2. Resolve the release tag to the approved immutable digest. Scan that image using a trusted scanner, record scanner/database timestamp and platform, and review publisher/release provenance according to local policy. Scanning may pull artifacts and write caches; authorize those actions.
3. Preserve previous Compose/config revision and exact old image reference; retain or export the artifact if registry retention is uncertain. Record anonymous and named volumes, bind mounts, and external database state. `docker commit` does not back up volumes and is not the normal release rollback mechanism.
4. Build/test the target in staging. Check healthcheck dependencies, startup grace, required environment variables, and startup migrations. A backward-incompatible state migration blocks simple image rollback.
5. In a reviewed override or versioned manifest, pin the service to `registry.example/app@sha256:...` using the real verified digest. Validate locally without exposing expanded secrets. The repository does not supply a production override.
6. Pull and recreate only the approved service, using the actual project/files:

   ```bash
   docker compose -f compose.yaml -f patch.override.yaml pull api
   docker compose -f compose.yaml -f patch.override.yaml up -d --no-deps api
   ```

   `--no-deps` limits recreation but does not prove dependency compatibility. A single Compose service replacement usually interrupts traffic. Do not claim Compose automatically supplies a rolling update.

7. Verify the running image ID/digest, stable process status, configured healthcheck where present, direct-origin/public endpoint, functional request, and workers. “Up” without a healthcheck is process state, not readiness.
8. Observe before proceeding. Do not prune old images or volumes during the recovery window.

**Recovery:** restore the previous manifest/config and immutable image, recreate the affected service, then verify. Restore state only through an approved consistency procedure. Never use `docker compose down -v` as patch cleanup.

## 4. Node.js dependencies and runtime

1. Identify repository revision, package manager and version, lockfile, Node runtime, app unit/image, environment, build process, and production artifact. Include build dependencies when assessing supply-chain exposure even if runtime audit omits dev dependencies.
2. In an isolated checkout, obtain structured audit evidence with the repository's package manager. For npm, `npm audit --json --omit=dev` can return nonzero for findings; distinguish that from authentication, connectivity, parse, or registry failures.
3. Map each advisory to direct/transitive dependency path and deployed use. Verify fixed versions and Node engine compatibility. Prefer a reviewed targeted dependency change; do not run blind `npm audit fix --force` on production.
4. Update manifests and lockfile together in development, review the dependency diff and lifecycle scripts, then run the project's clean install/build/test suite and critical integration tests. `npm ci` removes/recreates `node_modules`, can run scripts, and belongs in a build environment rather than an ad hoc live repair.
5. Build an immutable artifact/container. Preserve the previous artifact, matching manifests/lockfile, runtime, and config. Deploy through the normal supervisor and verify both artifact identity and workload health.
6. For runtime changes, verify upstream support status, supported ABI/native modules, engine ranges, TLS/crypto behavior, process-manager compatibility, and clean rebuild requirements. A minor bump can break compatibility; a major bump is a separate tested change.

**Recovery:** redeploy the previous complete artifact and compatible runtime/config. Reverting only `package-lock.json` may conflict with `package.json` and does not restore built assets or state. If rebuilding is unavoidable, restore both manifests from the same revision and reproduce the original build inputs.

## 5. Python dependencies and runtime

1. Identify the actual service interpreter and virtual environment, not the user's global `pip`. Record project revision, Python version, platform, lockfile/constraints, worker supervisor, and deployed artifact.
2. Use an approved advisory-aware scanner against the actual resolved dependency set. `pip list --outdated` and `uv tree` describe age/structure, not vulnerability applicability. Record private-index disclosure considerations and scanner network/cache behavior.
3. Resolve targeted updates in an isolated environment using the project's lock tool. Review transitive changes, Python requirements, native wheels/system-library dependencies, and hashes where used. Do not repair a production venv with an unreviewed global `sudo pip install`.
4. Reproduce the environment, run unit/integration tests, import/startup tests, and critical request/worker checks. Build a new immutable environment/image or release directory.
5. Switch the service to the reviewed artifact and restart through the supervisor. Verify the running interpreter/environment, actual dependencies, functional behavior, and advisory disposition.

**Recovery:** switch to the retained previous environment/image with matching config and compatible data. Reinstalling old requirements alone may not reproduce the previous resolver result or binary artifacts. Treat Python major/minor migrations as compatibility work requiring a separate test plan.

## 6. Emergency exploited vulnerability

Urgency shortens elapsed time, not the need for ownership and evidence.

1. Confirm component applicability, known exploitation evidence, exposure, and any compromise indicators. If compromise is suspected, involve incident response; patching does not remove persistence or establish the host is trustworthy.
2. Name the emergency approver and incident/change ID. Select the smallest tested fix or vendor-supported temporary mitigation. Exposure controls outside ordinary patch scope need explicit emergency authorization.
3. Record a shortened test/observation plan, recovery limits, and accepted risk. Preserve evidence required by incident responders before destructive recovery.
4. Apply a bounded canary when feasible; otherwise document why unavailable. Verify activation and critical workload behavior immediately.
5. Perform full follow-up scanning, compatibility checks, mitigation removal planning, and retrospective. Give every deferred check an owner and deadline.

## 7. Recurring review and multiple hosts

- Schedule inventory first; agree evidence retention, permissions, registry traffic, alert routing, and an owner for failed audits. Example: weekly local collection and a risk-based patch review cadence, with emergency handling for urgent findings.
- Save timestamped evidence with restrictive permissions. Avoid world-readable logs and unbounded append-only cron output. Nonzero audit exit status needs attention even if some sections succeeded.
- Compare host inventories and advisory dispositions, including stale/unknown scans. Do not rank a host safer simply because its scanner failed or uptime reset.
- For a fleet, group by OS/workload/version, test staging, patch a representative canary, observe, then expand bounded waves with concurrency and failure thresholds set beforehand.
- Check capacity, load balancer state, replica lag/quorum, and cross-version compatibility before each wave. Stop the wave on threshold breach; do not continue because other hosts are healthy.
- Treat host OS release upgrades, Kubernetes control-plane/node upgrades, and database engine major upgrades as separate product-specific runbooks. This repository does not provide their execution commands.
