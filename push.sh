#!/bin/bash
set -e -u

cmd_path=$(dirname -- "$( readlink -f -- "$0"; )")

if [[ $cmd_path == "/afs/sipb.mit.edu/project/sipb-projectdb"* ]]
then
    web_scripts_path=/mit/sipb-projectdb/web_scripts/
else
    web_scripts_path=/mit/$(whoami)/web_scripts/
fi

echo $cmd_path
echo $web_scripts_path


cd "$(dirname "$0")"
# rsync -av web_scripts/ $web_scripts_path

#chmod 0777 /mit/hwops/web_scripts/robots.txt
#rsync -av manuals/ /mit/hwops/web_scripts/manuals/
