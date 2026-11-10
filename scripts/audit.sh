#!/usr/bin/env bash
# Local posture inventory. Optional npm scans require --network-scans.
# Never installs, escalates privilege, restarts, or refreshes package indexes.
set -uo pipefail

network_scans=0
app_roots=()
incomplete=0
usage() {
  echo 'Usage: bash scripts/audit.sh [--app-root PATH]... [--network-scans]'
  echo 'Default: local inventory. Network scans may transmit metadata/write caches.'
}
while (($#)); do
  case "$1" in
    --app-root)
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        usage >&2; exit 2
      fi
      app_roots+=("$2"); shift 2 ;;
    --network-scans) network_scans=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

section() { printf '\n--- %s ---\n' "$1"; }
unknown() { printf 'UNKNOWN: %s\n' "$1"; incomplete=1; }
# Capture stderr rather than discarding it; never report a failed command as clean.
run_local() {
  local output rc
  output=$("$@" 2>&1); rc=$?
  if ((rc == 0)); then
    printf '%s\n' "$output"
  else
    unknown "command failed (exit $rc): $*"
    printf '%s\n' "$output"
  fi
}

printf '=== Host: %s | UTC: %s ===\n' "$(hostname)" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'Review/redact output before sharing. No automatic privilege escalation.\n'
section 'OS / kernel / boot'
if [[ -r /etc/os-release ]]; then
  # Print selected fields without sourcing a file as shell code.
  sed -n -E '/^(PRETTY_NAME|VERSION_ID|ID)=/p' /etc/os-release
else
  unknown '/etc/os-release unavailable'
fi
run_local uname -r
run_local uptime -s

section 'APT simulation: local indexes only; freshness not established'
if command -v apt-get >/dev/null 2>&1; then
  apt_output=$(LC_ALL=C apt-get -s upgrade 2>&1); apt_rc=$?
  if ((apt_rc == 0)); then
    printf '%s\n' "$apt_output"
    printf 'Simulated package installations: %s\n' "$(printf '%s\n' "$apt_output" | awk '/^Inst /{n++} END{print n+0}')"
    echo 'Security applicability requires vendor advisory/repository evidence; no CVE count inferred.'
  else
    unknown "APT simulation failed (exit $apt_rc)"
    printf '%s\n' "$apt_output"
  fi
  if command -v apt-mark >/dev/null 2>&1; then
    run_local apt-mark showhold
  else
    unknown 'apt-mark unavailable; held packages not checked'
  fi
else
  unknown 'APT unavailable; use distribution-specific inventory'
fi

section 'Reboot marker (not a complete activation check)'
if [[ -f /var/run/reboot-required ]]; then
  echo 'PRESENT: distribution requests reboot'
else
  echo 'ABSENT: does not prove running kernel/libraries are current'
fi

section 'Failed systemd units'
if command -v systemctl >/dev/null 2>&1; then
  run_local systemctl --failed --no-legend --plain --no-pager
else
  unknown 'systemctl unavailable'
fi
section 'TCP / UDP listeners; process ownership may need additional privileges'
if command -v ss >/dev/null 2>&1; then
  run_local ss -lntup
else
  unknown 'ss unavailable'
fi

section 'Docker running containers and local image identity'
if command -v docker >/dev/null 2>&1; then
  run_local docker ps --no-trunc --format '{{.Names}}\t{{.Image}}\t{{.Status}}'
  run_local docker image ls --digests --no-trunc --format '{{.Repository}}:{{.Tag}}\t{{.Digest}}\t{{.ID}}\t{{.CreatedAt}}'
  echo 'Not vulnerability-scanned. Image age and Up status do not establish security/readiness.'
else
  echo 'NOT AVAILABLE: docker client; container coverage not established'
fi

section 'Explicit application roots'
if ((${#app_roots[@]} == 0)); then
  echo 'NOT SCANNED: no --app-root supplied; no automatic home-directory search'
fi
for root in "${app_roots[@]}"; do
  printf '\nApplication root: %s\n' "$root"
  if [[ ! -d "$root" ]]; then
    unknown 'application directory unavailable'; continue
  fi
  for manifest in package.json package-lock.json npm-shrinkwrap.json requirements.txt pyproject.toml uv.lock poetry.lock; do
    [[ ! -f "$root/$manifest" ]] || printf 'PRESENT: %s\n' "$manifest"
  done
  echo 'Python: actual service interpreter/environment and advisory-aware scan require separate assessment.'
  if [[ ! -f "$root/package-lock.json" && ! -f "$root/npm-shrinkwrap.json" ]]; then
    echo 'NOT SCANNED: no npm lockfile; use the actual package manager for this app'
    continue
  fi
  if ((network_scans == 0)); then
    echo 'NOT SCANNED: npm registry audit requires --network-scans'; continue
  fi
  if ! command -v npm >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
    unknown 'npm audit requires npm and Python 3 for structured parsing'; continue
  fi
  audit_output=$(cd -- "$root" && npm audit --json --omit=dev 2>&1); audit_rc=$?
  # Only accept the expected exit statuses AND a supported structured result.
  # Never coerce a registry failure, invalid JSON, or absent counts to zero.
  if ! printf '%s' "$audit_output" | python3 -c '
import json, sys
try:
    status = int(sys.argv[1])
    result = json.load(sys.stdin)
    if status not in (0, 1) or not isinstance(result, dict) or "error" in result:
        raise ValueError("command or registry error")
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("missing or invalid metadata")
    counts = metadata.get("vulnerabilities")
    if not isinstance(counts, dict):
        raise ValueError("missing or invalid severity mapping")
    keys = ("info", "low", "moderate", "high", "critical", "total")
    if not all(type(counts.get(k)) is int and counts[k] >= 0 for k in keys):
        raise ValueError("missing or invalid severity counts")
    if sum(counts[k] for k in keys[:-1]) != counts["total"]:
        raise ValueError("inconsistent severity counts")
    if (status == 0 and counts["total"] != 0):
        raise ValueError("inconsistent success status")
    print("SCANNED: npm runtime dependency findings: " + ", ".join(f"{k}={counts[k]}" for k in keys))
    print("Counts are package findings, not unique CVEs. Preserve detailed JSON separately.")
except (ValueError, KeyError, TypeError) as exc:
    print(f"UNKNOWN: npm audit result unusable ({exc})")
    sys.exit(1)
' "$audit_rc"; then
    incomplete=1
    echo 'Review npm diagnostics locally; raw registry errors may contain sensitive data.'
  fi
done

section 'Disk and inode headroom'
run_local df -h / /var
run_local df -i / /var
section 'Summary'
echo 'Inventory only: no packages installed, no restarts, no package-index refresh.'
if ((incomplete)); then
  echo 'INCOMPLETE: one or more attempted checks failed; unknown is not clean.'
  exit 1
fi
echo 'Requested checks completed. Skipped/unimplemented scans remain outside coverage.'
exit 0
