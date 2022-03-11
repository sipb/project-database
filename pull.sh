#!/bin/bash
set -e -u
cd "$(dirname "$0")"
rsync -av /mit/$(whoami)/web_scripts/ web_scripts/
git status
