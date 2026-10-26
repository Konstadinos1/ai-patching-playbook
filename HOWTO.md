# HOWTO — Patching a webserver with an AI agent, end to end

This is the complete process. It assumes a Linux server (Ubuntu/Debian
examples) running Docker containers and/or Node apps — the most common
self-hosted shape. Adapt commands for other distros.

---

## 0. What an agent can and cannot do

| | ChatGPT (web, no tools) | Tool-using agent (Claude Code, Codex, Hermes) |
|---|---|---|
| Read your audit output | ✅ | ✅ |
| Explain CVEs, prioritize | ✅ | ✅ |
| Write exact patch commands | ✅ | ✅ |
| Run the commands | ❌ you do | ✅ (with approval gates) |
| Verify services after | ❌ you do | ✅ |
| Break production if unsupervised | ❌ (can't touch it) | ⚠️ **yes — hence this playbook** |

The agent is the junior engineer with infinite patience. You are the
approving senior. The process below enforces that relationship.

---

## 1. The six phases (what the agent will walk through)

```
0 DISCOVER ─► 1 ASSESS ─► 2 PLAN ─► 🛑 YOUR APPROVAL ─► 3 BACKUP ─► 4 PATCH ─► 5 VERIFY ─► 6 REPORT
   read-only    read-only    read-only      no mutations
                             (a table)       before this point   one layer     health      evidence
                                                              per window     checks
```

**Why the stop gate matters:** an agent that patches + restarts + reboots in
one autonomous run will eventually take down production at 3 AM. The gate is
cheap; an outage is not.

---

## 2. Step-by-step

### Step 1 — Snapshot the audit (5 min)

On the server:

```bash
bash audit.sh > audit-$(date +%F).txt 2>&1
```

The script is **read-only**: simulated upgrades, listening ports, container
ages, npm audits, disk space. Nothing installed, nothing restarted.

If you prefer the agent to do it (execute mode), it runs the same script
itself — still read-only.

### Step 2 — Brief the agent

Open ChatGPT (advise) or your terminal agent (execute). Paste:

1. The whole of `PROMPT.md`
2. Your first message with the filled template (TARGET, MODE, window,
   constraints)
3. The audit output

### Step 3 — Read the plan, not the confidence

The agent returns a table like:

| Finding | Layer | Fix | Restart? | Risk if patched | Risk if not | Rollback |
|---|---|---|---|---|---|---|
| openssl 3.0.2 (KEV-2026-XXXX) | OS | apt upgrade openssl | nginx restart (~2s) | low — staged rollout | active exploitation | apt install openssl=3.0.2-0ubuntu1 |
| lodash <4.17.21 | app | npm audit fix | no | low | DoS vector | git checkout package-lock.json |

Check before approving:

- [ ] Every CVE comes from **your audit output** (no invented CVEs — ask
  "which line of the audit shows this?" if unsure)
- [ ] Restarts are listed with expected downtime
- [ ] Rollback exists per item, or risk is explicitly accepted
- [ ] Layers aren't mixed (app deps ≠ OS packages ≠ release upgrade)
- [ ] Nothing touches things you didn't list in scope

### Step 4 — Approve, and let it patch one layer at a time

Safest order (each layer = its own maintenance window):

1. **App dependencies** (`npm audit fix`) — app restart only, instant rollback via lockfile
2. **App runtime minor bumps** — `node 22.1 → 22.9`, not `22 → 24`
3. **OS package upgrades** — `apt upgrade`, restart only flagged services
4. **Containers** — pull new images, recreate **one at a time**, health check between each
5. **OS release upgrade** (`22.04 → 24.04`) — only with a full snapshot and a real window

### Step 5 — Verify like a skeptic

After each layer, the agent (or you) runs:

```bash
# the service actually answers
curl -fsS -o /dev/null -w '%{http_code}\n' https://your-site.example/   # want 200/301
ss -tln | grep -E ':(80|443)\b'                                          # ports alive

# system level
systemctl --failed                    # want: 0 listed
docker ps --format '{{.Names}} {{.Status}}'   # want: healthy/up, not restarting

# one real functional request (log in, submit a form, hit the API)
```

Then re-run the audit — the patched layer's count should drop. Show the
before/after numbers in the report.

### Step 6 — Keep the evidence

The final report (agent produces it, you archive it) contains:
what changed (versions before → after), what restarted + observed downtime,
verification output, remaining findings with reasons, and anything deferred
to `LATER.md`. This is your audit trail for insurance, clients, and
future-you.

---

## 3. Rollback cheat sheet

| Layer | Rollback |
|---|---|
| npm deps | `git checkout package-lock.json && npm ci && restart app` |
| apt package | `apt install <pkg>=<old-version>` (find with `apt policy <pkg>`) |
| container | retag previous image `docker tag <old-sha> img:latest && docker compose up -d` |
| config file | restore from the `.bak-$(date +%F)` copy made in Phase 3 |
| whole box | cloud snapshot restore (only if you actually took one — Phase 3 asks) |

---

## 4. Traps this playbook exists to prevent

1. **The restart kills the box, not the patch.** A patched-but-unrestarted
   server is still vulnerable but *stable*; a restarted server with a broken
   unit file is *down*. That's why restarts get their own gate.
2. **Invented CVEs.** LLMs confidently cite CVEs that don't exist or don't
   apply. Rule: every finding must trace to a line in real scanner output.
3. **Silence ≠ health.** Empty logs on a dead service. Always hit the endpoint.
4. **Downtime fakes your metrics.** After a reboot, "incidents per 24h"
   numbers are window-truncated. Note boot time before interpreting graphs.
5. **The agent patches itself out of existence.** If the agent runs *on* the
   server it's patching (Hermes/Claude Code on the same box), upgrading its
   own runtime or restarting its host kills it mid-task. Its own stack is
   out of scope; a human does those.
6. **do-release-upgrade casually.** Never inside a tool-using agent. Ever.
7. **`apt dist-upgrade` ≠ `apt upgrade`.** The first removes/packages-swaps;
   default to the second unless the plan says otherwise.
8. **Unattended-upgrades double-patching.** If it's enabled, the agent's
   manual `apt upgrade` races it. Check `systemctl status unattended-upgrades` first and coordinate.

---

## 5. Scheduling (once the manual run works)

Cron the audit weekly; patch monthly. Example root crontab:

```cron
# Monday 06:10 — read-only posture snapshot, appended to a log
10 6 * * 1  bash /opt/ai-patching-playbook/scripts/audit.sh >> /var/log/audit-weekly.log 2>&1
```

Give the log to the agent once a month with MODE: advise, review the diff
with the previous month, and run execute-mode windows only for the delta.

---

## 6. What this playbook deliberately does NOT cover

- Firewall hardening, fail2ban, SSH key rotation → `LATER.md`, separate change
- Web Application Firewalls / Cloudflare config
- Database engine major-version upgrades (their own runbook)
- Compliance frameworks (use the evidence pack as *input*, not proof)
