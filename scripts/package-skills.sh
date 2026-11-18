#!/usr/bin/env bash
# Build one zip per skill (for Claude.ai / Claude Desktop "Upload skill") into dist/.
# Skills that use the shared toolkit also get a copy of sec-edgar's scripts and
# assets, so each zip works on its own.
set -euo pipefail
cd "$(dirname "$0")/.."
SKILLS=plugins/earnings-desk/skills
rm -rf dist && mkdir -p dist/tmp
for dir in "$SKILLS"/*/; do
  name=$(basename "$dir")
  stage="dist/tmp/$name"
  cp -R "$dir" "$stage"
  find "$stage" -name "__pycache__" -prune -exec rm -rf {} +
  if [ "$name" != "sec-edgar" ] && grep -q "\.\./sec-edgar/" "$stage/SKILL.md"; then
    mkdir -p "$stage/vendor/sec-edgar"
    cp -R "$SKILLS/sec-edgar/scripts" "$SKILLS/sec-edgar/assets" "$stage/vendor/sec-edgar/"
    printf '\n> Standalone bundle: the shared toolkit is included under `vendor/sec-edgar/`. Where this skill says `../sec-edgar/`, use `vendor/sec-edgar/`.\n' >> "$stage/SKILL.md"
  fi
  (cd dist/tmp && zip -qr "../earnings-desk-$name.zip" "$name")
done
rm -rf dist/tmp
ls -1 dist
