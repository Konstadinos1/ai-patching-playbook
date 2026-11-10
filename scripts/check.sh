#!/usr/bin/env bash
# Run local checks without registry scans, installs, Docker access, or sudo.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

for tool in bash python3 shellcheck git; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'Required quality tool missing: %s. Install it locally before running checks.\n' "$tool" >&2
    exit 1
  fi
done

printf '\nQuality tool versions\n'
bash --version
python3 --version
shellcheck --version
git --version

mapfile -t shell_scripts < <(find scripts -type f -name '*.sh' -print | sort)
for script in "${shell_scripts[@]}"; do
  bash -n "$script"
done
shellcheck "${shell_scripts[@]}"
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
git diff --check
