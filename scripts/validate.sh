#!/usr/bin/env bash
# Validate the earnings-desk marketplace: skill frontmatter, agent frontmatter,
# Python syntax, and (if the Claude CLI is installed) `claude plugin validate`.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
import os, re, sys, json

root = "plugins/earnings-desk"
errors, warnings = [], []
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CATEGORIES = {"0-orchestration", "1-data-foundations", "2-earnings-season", "3-forensics-quality", "4-valuation-competition", "5-thesis-desk"}

def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm, key, buf = {}, None, []
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if top and not line.startswith(" "):
            if key and buf:
                fm[key] = " ".join(buf).strip()
            key, val = top.group(1), top.group(2).strip()
            buf = [] if val in (">-", ">", "|", "|-", "") else [val.strip('"').strip("'")]
            fm[key] = val
        elif key:
            buf.append(line.strip())
    if key and buf:
        fm[key] = " ".join(buf).strip()
    return fm, text[m.end():]

skills_dir = os.path.join(root, "skills")
skills = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
for s in skills:
    p = os.path.join(skills_dir, s, "SKILL.md")
    if not os.path.exists(p):
        errors.append("%s: missing SKILL.md" % s); continue
    fm, body = frontmatter(p)
    if fm is None:
        errors.append("%s: missing YAML frontmatter" % s); continue
    name = fm.get("name", "")
    if name != s: errors.append("%s: name '%s' != folder" % (s, name))
    if not NAME.match(name) or len(name) > 64: errors.append("%s: invalid name" % s)
    desc = fm.get("description", "")
    if not desc: errors.append("%s: empty description" % s)
    if len(desc) > 1024: errors.append("%s: description is %d chars (max 1024)" % (s, len(desc)))
    cat = re.search(r'category:\s*"?([^"\n]+)"?', open(p).read())
    if not cat or cat.group(1).strip() not in CATEGORIES: errors.append("%s: metadata.category missing/invalid" % s)
    lines = body.count("\n")
    if lines > 500: warnings.append("%s: SKILL.md body is %d lines (keep under 500)" % (s, lines))
    for ref in re.findall(r"\]\(((?:references|assets|scripts)/[^)#]+)\)", body):
        if not os.path.exists(os.path.join(skills_dir, s, ref)):
            errors.append("%s: broken link %s" % (s, ref))

agents_dir = os.path.join(root, "agents")
agents = sorted(f for f in os.listdir(agents_dir) if f.endswith(".md")) if os.path.isdir(agents_dir) else []
for a in agents:
    fm, _ = frontmatter(os.path.join(agents_dir, a))
    if not fm or not fm.get("name") or not fm.get("description"):
        errors.append("agents/%s: needs name + description frontmatter" % a)
    elif fm["name"] != a[:-3]:
        errors.append("agents/%s: name '%s' != filename" % (a, fm["name"]))

for f in (".claude-plugin/marketplace.json", root + "/.claude-plugin/plugin.json"):
    try:
        json.load(open(f))
    except Exception as e:
        errors.append("%s: %s" % (f, e))
mp = json.load(open(".claude-plugin/marketplace.json"))
pj = json.load(open(root + "/.claude-plugin/plugin.json"))
if mp["plugins"][0]["name"] != pj["name"]:
    errors.append("marketplace entry name != plugin.json name")

print("skills: %d  agents: %d" % (len(skills), len(agents)))
for w in warnings: print("WARN  " + w)
for e in errors: print("ERROR " + e)
sys.exit(1 if errors else 0)
PY

echo "python syntax:"
find plugins -name "*.py" -print0 | xargs -0 python3 -m py_compile && echo "  ok"

if command -v claude >/dev/null 2>&1; then
  claude plugin validate .
  claude plugin validate ./plugins/earnings-desk
else
  echo "(claude CLI not found; skipping 'claude plugin validate')"
fi
echo "✔ validation passed"
