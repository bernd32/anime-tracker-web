#!/bin/sh
set -eu

SOURCE="/home/bernd/Documents/programs/python/anime-tracker-web" 
DEST="/opt/docker/anime-tracker-web"
SERVER_ALIAS="home-borg" 

rsync -av --exclude-from='scripts/rsyncignore.txt' "${SOURCE}/" "${SERVER_ALIAS}:${DEST}/"