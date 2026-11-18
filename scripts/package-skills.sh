#!/usr/bin/env bash
# Build one zip per skill (for Claude.ai / Claude Desktop "Upload skill") into dist/.
# A skill that calls sibling skills' scripts (e.g. ../sec-edgar/scripts/edgar.py)
# gets copies of those siblings' scripts/ and assets/ under vendor/<sibling>/, so
# each zip works on its own. The Python scripts already look in ../vendor/ when
# the sibling folder is missing.
set -euo pipefail
cd "$(dirname "$0")/.."
SKILLS=plugins/earnings-desk/skills
rm -rf dist && mkdir -p dist/tmp

vendor_one() { # $1 = stage dir, $2 = sibling name
  local stage=$1 sib=$2
  [ -d "$SKILLS/$sib" ] || return 0
  [ -d "$stage/vendor/$sib" ] && return 0
  mkdir -p "$stage/vendor/$sib"
  for part in scripts assets; do
    if [ -d "$SKILLS/$sib/$part" ]; then cp -R "$SKILLS/$sib/$part" "$stage/vendor/$sib/"; fi
  done
}

for dir in "$SKILLS"/*/; do
  name=$(basename "$dir")
  stage="dist/tmp/$name"
  cp -R "$dir" "$stage"
  sibs=$(grep -rhoE '\.\./[a-z0-9-]+/(scripts|assets)' "$stage" 2>/dev/null | sed -E 's#\.\./([a-z0-9-]+)/.*#\1#' | sort -u | grep -vx "$name" || true)
  for sib in $sibs; do vendor_one "$stage" "$sib"; done
  # Scripts of vendored siblings import their own siblings (dcf.py -> statements.py -> edgar.py)
  for sib in sec-edgar financial-statements; do
    if [ -d "$stage/vendor" ] && grep -rqs "$sib" "$stage/vendor" "$stage/scripts" 2>/dev/null; then vendor_one "$stage" "$sib"; fi
  done
  if [ -d "$stage/vendor" ]; then
    printf '\n> **Standalone bundle:** shared toolkits are included under `vendor/`. Wherever this skill says `../<skill>/scripts/…`, use `vendor/<skill>/scripts/…`.\n' >> "$stage/SKILL.md"
  fi
  find "$stage" -name "__pycache__" -prune -exec rm -rf {} +
  (cd dist/tmp && zip -qr "../earnings-desk-$name.zip" "$name")
done
rm -rf dist/tmp
ls -1 dist
