#!/usr/bin/env sh

args="--api_key $API_KEY --api_url $API_URL --offline_threshold $OFFLINE_THRESHOLD"

BASEDIR=$(dirname "$0")
echo $args | xargs python3 -u $BASEDIR/immich_auto_remove_offline_files.py