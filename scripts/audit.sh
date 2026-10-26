#!/usr/bin/env bash
# audit.sh — read-only security posture snapshot for a Linux webserver.
# Changes nothing, installs nothing. Paste the output into the AI patching
# agent (see PROMPT.md). Safe to run any time, including in production.

set -uo pipefail

echo "=== $(hostname) — $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="

echo
echo "--- OS / kernel ---"
(. /etc/os-release 2>/dev/null && echo "${PRETTY_NAME:-unknown}") || echo "unknown"
uname -r

echo
echo "--- Last boot (context: downtime corrupts rate metrics) ---"
uptime -s 2>/dev/null || uptime

echo
echo "--- Pending OS updates (simulated, nothing installed) ---"
if command -v apt-get >/dev/null 2>&1; then
  total=$(apt-get -s upgrade 2>/dev/null | grep -c '^Inst' || true)
  sec=$(apt-get -s upgrade 2>/dev/null | grep '^Inst' | grep -ci 'secur' || true)
  echo "upgradable: ${total} (security: ${sec})"
  apt-get -s upgrade 2>/dev/null | grep '^Inst' | grep -i 'secur' | awk '{print "  " $2}' | head -25
else
  echo "apt not found (non-Debian system — adapt)"
fi

echo
echo "--- Reboot required? ---"
if [ -f /var/run/reboot-required ]; then
  echo "YES — $(cat /var/run/reboot-required 2>/dev/null)"
else
  echo "no"
fi

echo
echo "--- Failed systemd units ---"
systemctl --failed --no-legend --plain 2>/dev/null | head -10
count=$(systemctl --failed --no-legend --plain 2>/dev/null | grep -c . || true)
echo "failed units: ${count}"

echo
echo "--- Listening ports (top 20) ---"
(ss -tlnp 2>/dev/null || ss -tln 2>/dev/null) | head -20

echo
echo "--- Docker containers & image ages ---"
if command -v docker >/dev/null 2>&1; then
  docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>/dev/null || echo "(docker present but no access — try sudo or docker group)"
  echo
  echo "images older than 30 days:"
  docker images --format '{{.Repository}}:{{.Tag}}\t{{.CreatedSince}}' 2>/dev/null \
    | grep -vE '<none>' | while IFS=$'\t' read -r img age; do
        case "$age" in
          *day*|*week*|*month*|*year*)
            n=$(echo "$age" | grep -oE '[0-9]+')
            case "$age" in
              *month*|*year*) echo "  $img  ($age)";;
              *week*)  [ "${n:-0}" -ge 5 ] && echo "  $img  ($age)";;
              *day*)   [ "${n:-0}" -ge 30 ] && echo "  $img  ($age)";;
            esac
            ;;
        esac
      done
  echo "dangling images: $(docker images -f dangling=true -q 2>/dev/null | wc -l)"
else
  echo "docker not installed"
fi

echo
echo "--- Node apps: known vulnerabilities (npm audit --omit=dev) ---"
found_locks=$(find "$HOME" -maxdepth 3 -name package-lock.json -not -path '*/node_modules/*' 2>/dev/null | head -20)
if [ -z "$found_locks" ]; then
  echo "no package-lock.json found under $HOME (depth 3)"
else
  echo "$found_locks" | while read -r f; do
    d=$(dirname "$f")
    out=$(cd "$d" && npm audit --omit=dev 2>/dev/null || true)
    high=$(echo "$out" | grep -oE '[0-9]+ high' | grep -oE '[0-9]+' || echo 0)
    crit=$(echo "$out" | grep -oE '[0-9]+ critical' | grep -oE '[0-9]+' || echo 0)
    echo "  $d → high: ${high:-0}  critical: ${crit:-0}"
  done
fi

echo
echo "--- Python: outdated packages (top-level, if pip available) ---"
if command -v pip3 >/dev/null 2>&1; then
  pip3 list --outdated 2>/dev/null | head -12 || true
else
  echo "pip3 not on PATH (check venvs manually)"
fi

echo
echo "--- Disk space (patching needs headroom) ---"
df -h / /var 2>/dev/null | grep -vE '^Filesystem.*tmpfs' | head -5

echo
echo "=== END AUDIT — read-only, nothing was changed ==="
