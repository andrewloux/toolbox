#!/usr/bin/env bash

set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
backup_root="$HOME/.toolbox-backups/claude-extension-tooling/$(date +%Y%m%d-%H%M%S)"

info() {
  printf '[info] %s\n' "$*"
}

success() {
  printf '[ok] %s\n' "$*"
}

backup_path() {
  local path="$1"
  local label="$2"

  if [[ -L "$path" || -e "$path" ]]; then
    mkdir -p "$backup_root"
    mv "$path" "$backup_root/$label"
    info "backed up $path -> $backup_root/$label"
  fi
}

link_path() {
  local source="$1"
  local destination="$2"
  local label="$3"

  mkdir -p "$(dirname "$destination")"

  if [[ -L "$destination" && "$(readlink "$destination")" == "$source" ]]; then
    success "already linked: $destination"
    return
  fi

  backup_path "$destination" "$label"
  ln -s "$source" "$destination"
  success "linked $destination -> $source"
}

link_path "$repo_root/scripts/extension_transformer" "$HOME/extension_transformer" "extension_transformer"
link_path "$repo_root/scripts/extension_ast" "$HOME/extension_ast" "extension_ast"
link_path "$repo_root/scripts/extension_explorer.ts" "$HOME/extension_explorer.ts" "extension_explorer.ts"
link_path "$repo_root/config/extension_transformer" "$HOME/.config/extension_transformer" "extension_transformer-config"

if [[ -d "$backup_root" ]]; then
  info "backups stored in $backup_root"
fi

printf '\n'
printf 'Global command layer now points at this repo.\n'
printf 'Run from anywhere:\n'
printf '  ~/extension_transformer --dry-run\n'
printf '  ~/extension_transformer\n'
printf '  ~/extension_ast preview ~/ClaudeChromeExtension/latest\n'
