#!/usr/bin/env sh

args="--api_key $API_KEY --API_URL $API_URL"

BASEDIR=$(dirname "$0")
echo $args | xargs python3 -u $BASEDIR/immich_auto_remove_offline_files.py