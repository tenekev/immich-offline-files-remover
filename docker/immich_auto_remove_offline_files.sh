#!/usr/bin/env sh

args="--no_prompt --admin_apikey $API_KEY_ADMIN --user_apikey $API_KEY_USER --immichaddress $API_URL"

BASEDIR=$(dirname "$0")
echo $args | xargs python3 -u $BASEDIR/immich_auto_album.py