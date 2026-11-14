#!/usr/bin/env bash
# Copy the shared board repo into the run folder and commit it as the base the agent starts from.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/../_shared/board-repo/." .
git add -A
git -c user.name="Plugin Eval" -c user.email=eval@example.invalid commit -qm "fixture: base"
