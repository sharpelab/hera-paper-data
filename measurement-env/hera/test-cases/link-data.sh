#!/usr/bin/env bash
# Relocate a fixture's bulky binary layer out of the git repo and onto the data
# volume, replacing each moved artifact with a symlink. Keeps the authored layer
# (frontiers/, ground_truth/, *.md) tracked in git; moves notebooks, data/,
# images/, and runs/ to $HERA_DATA (default /data/sharpelab/hera-data, which is
# snapshotted but not on /home and not in git).
#
# A fixture is ~99.9% binary / 0.1% authored text, so this is the split that
# keeps git history small and the data partitionable for backups/sync.
#
# Usage:  HERA_DATA=/some/root ./link-data.sh <fixture-dir> [<fixture-dir> ...]
# Idempotent: artifacts already symlinked are skipped.
set -euo pipefail

HERA_DATA="${HERA_DATA:-/data/sharpelab/hera-data}"
# Glob patterns (relative to a fixture dir) for the binary layer.
BINARY_GLOBS=(data images runs '*.ipynb')

relocate() {
  local fixture="$1" name="$2" src dst
  src="$fixture/$name"
  [ -e "$src" ] || return 0
  [ -L "$src" ] && { echo "  skip (already linked): $name"; return 0; }
  dst="$HERA_DATA/test-cases/$(basename "$fixture")/$name"
  mkdir -p "$(dirname "$dst")"
  cp -a --reflink=auto "$src" "$dst"
  # verify before deleting the original
  if [ "$(du -sb "$src" | cut -f1)" = "$(du -sb "$dst" | cut -f1)" ]; then
    rm -rf "$src"
    ln -s "$dst" "$src"
    echo "  moved + linked: $name -> $dst"
  else
    rm -rf "$dst"
    echo "  ❌ size mismatch on $name — left in place" >&2
    return 1
  fi
}

for fixture in "$@"; do
  fixture="${fixture%/}"
  [ -d "$fixture" ] || { echo "not a dir: $fixture" >&2; exit 1; }
  echo "fixture: $fixture"
  for g in "${BINARY_GLOBS[@]}"; do
    for path in "$fixture"/$g; do
      [ -e "$path" ] || continue
      relocate "$fixture" "$(basename "$path")"
    done
  done
done
echo "done. HERA_DATA=$HERA_DATA"
