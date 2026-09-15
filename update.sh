#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 scan.py "$@"
git add -A
if git diff --cached --quiet; then
  echo "Nothing new."
  exit 0
fi
git commit -m "Update progress"
git push
echo "Pushed. The site updates in about a minute."
