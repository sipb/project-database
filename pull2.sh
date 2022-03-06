#!/bin/bash
set -e -u
cd "$(dirname "$0")"
rsync -av /mit/javsolis/web_scripts/ web_scripts/
git status
