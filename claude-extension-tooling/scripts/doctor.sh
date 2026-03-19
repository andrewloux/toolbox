#!/usr/bin/env bash

set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_root="${TARGET_ROOT:-$HOME/ClaudeChromeExtension}"
ext="${EXT:-$target_root/latest}"
hooks="$repo_root/config/extension_transformer/hooks.sh"
rules="$repo_root/config/extension_transformer/rules"

status=0

pass() {
  printf '[ok] %s\n' "$*"
}

warn() {
  printf '[warn] %s\n' "$*" >&2
  status=1
}

section() {
  printf '\n%s\n' "$*"
}

check_command() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    pass "$name -> $(command -v "$name")"
  else
    warn "missing command: $name"
  fi
}

check_executable() {
  local path="$1"
  if [[ -x "$path" ]]; then
    pass "executable present: $path"
  else
    warn "missing or not executable: $path"
  fi
}

section 'Toolchain'
check_command sg
check_command node
check_command npx

section 'Repo wiring'
check_executable "$repo_root/scripts/extension_transformer"
check_executable "$repo_root/scripts/extension_ast"
if [[ -f "$repo_root/scripts/extension_explorer.ts" ]]; then
  pass "explorer present: $repo_root/scripts/extension_explorer.ts"
else
  warn "missing explorer: $repo_root/scripts/extension_explorer.ts"
fi

if [[ -f "$hooks" ]]; then
  pass "hooks file present: $hooks"
else
  warn "missing hooks file: $hooks"
fi

rule_count="$(find "$rules" -type f \( -name '*.yml' -o -name '*.yaml' \) | wc -l | tr -d ' ')"
if [[ "$rule_count" -gt 0 ]]; then
  pass "rule pack present: $rule_count rule(s) in $rules"
else
  warn "no rule files found in $rules"
fi

section 'Chrome source'
if dry_run_output="$("$repo_root/scripts/extension_transformer" --dry-run --hooks "$hooks" 2>&1)"; then
  pass "extension_transformer dry-run succeeded"
  printf '%s\n' "$dry_run_output" | sed -n '/Best version:/p;/Profiles:/p;/Source:/p'
else
  warn "extension_transformer dry-run failed"
  printf '%s\n' "$dry_run_output" >&2
fi

section 'Extracted extension'
if [[ -L "$ext" ]]; then
  pass "latest symlink -> $(readlink "$ext")"
else
  warn "latest symlink missing: $ext"
fi

if [[ -f "$ext/.source_manifest" ]]; then
  pass "source manifest present"
  sed -n '1,8p' "$ext/.source_manifest"
else
  warn "missing .source_manifest at $ext"
fi

if [[ -f "$ext/git-hash.txt" ]]; then
  pass "git hash present: $(sed -n '1p' "$ext/git-hash.txt")"
else
  warn "missing git-hash.txt at $ext"
fi

section 'Suggested next step'
if [[ "$status" -eq 0 ]]; then
  printf 'make transform\n'
else
  printf 'Fix the warnings above, then run: make transform\n'
fi

exit "$status"
