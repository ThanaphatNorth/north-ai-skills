#!/bin/bash
# Change labels and fields of one issue: the AI loop's lock, verdict and class labels, and its summary field.
# Ids and label names live in config.md § AI loop.
#   jira-edit.sh ABC-12 --add-label ai-processing
#   jira-edit.sh ABC-12 --remove-label ai-processing --remove-label ai-queue --add-label ai-do-now
#   jira-edit.sh ABC-12 --field customfield_10050='{"value":"Level 4"}'     value is JSON
#   jira-edit.sh ABC-12 --field-md customfield_10100=summary.md            markdown file → ADF (multi-line text fields)
#   jira-edit.sh ABC-12 --dry-run --add-label x                            print the request body only; needs no credentials
set -euo pipefail
usage() { echo "usage: $0 <KEY> [--dry-run] (--add-label L | --remove-label L | --field ID=JSON | --field-md ID=FILE)..." >&2; exit 2; }
[ $# -ge 2 ] || usage
KEY=$1; shift
case $KEY in -*|*/*) usage ;; esac
DRY=0; ops=()
for a in "$@"; do
  if [ "$a" = "--dry-run" ]; then DRY=1; else ops+=("$a"); fi
done
[ ${#ops[@]} -gt 0 ] || usage
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"

body=$(python3 -I - "$SCRIPTS/md2adf.py" "${ops[@]}" <<'PY'
import importlib.util, json, re, sys

md2adf_path, args = sys.argv[1], sys.argv[2:]
labels, fields = [], {}

def fail(msg):
    print("jira-edit.sh: " + msg, file=sys.stderr)
    sys.exit(2)

def split_pair(opt, val):
    fid, sep, rest = val.partition("=")
    if not sep or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", fid):
        fail("%s %r: expected <field id>=<value>, field id like customfield_10100" % (opt, val))
    return fid, rest

def markdown_to_adf(path):
    spec = importlib.util.spec_from_file_location("md2adf", md2adf_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    text = re.sub(r"<!--.*?-->\n?", "", open(path, encoding="utf-8").read(), flags=re.S)
    return mod.convert(text, "0")

i = 0
while i < len(args):
    opt = args[i]
    if opt not in ("--add-label", "--remove-label", "--field", "--field-md"):
        fail("unknown option %s" % opt)
    if i + 1 >= len(args):
        fail("%s needs a value" % opt)
    val, i = args[i + 1], i + 2
    if opt in ("--add-label", "--remove-label"):
        if not val or re.search(r"\s", val):
            fail("label %r: Jira labels have no spaces" % val)
        labels.append({"add" if opt == "--add-label" else "remove": val})
    elif opt == "--field":
        fid, raw = split_pair(opt, val)
        try:
            fields[fid] = json.loads(raw)
        except ValueError:
            fail("--field %s: value is not JSON (quote strings: %s='\"text\"')" % (fid, fid))
    else:
        fid, path = split_pair(opt, val)
        try:
            fields[fid] = markdown_to_adf(path)
        except OSError as e:
            fail("--field-md %s: %s" % (fid, e))

if labels and "labels" in fields:
    fail("labels: use --add-label / --remove-label or --field labels=[...], not both")
body = {}
if labels:
    body["update"] = {"labels": labels}
if fields:
    body["fields"] = fields
print(json.dumps(body, ensure_ascii=False))
PY
) || exit 2

if [ "$DRY" = 1 ]; then printf '%s\n' "$body"; exit 0; fi

. "$SCRIPTS/_env.sh"
code=$(auth | curl -sS -K - -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary "$body" "$JIRA_SITE/rest/api/3/issue/$KEY")
labels=$(auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY?fields=labels" | python3 -I -c 'import json,sys; print(",".join(json.load(sys.stdin)["fields"].get("labels") or []))' || echo "?")
echo "$KEY edit → HTTP $code · labels now: ${labels:-none}"
[ "$code" = "204" ]
