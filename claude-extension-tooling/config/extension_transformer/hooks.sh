#!/usr/bin/env bash

apply_local_transforms() {
  local destination="$1"
  local repo_root

  repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  "$repo_root/scripts/extension_ast" apply "$destination" --rules "$repo_root/config/extension_transformer/rules"
}
