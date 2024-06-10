#!/bin/bash

echo "START /entrypoint.sh"

set -e

# ensure cron is running
service cron start
service cron status

echo "END /entrypoint.sh"

# print the download_dir
echo "Download directory in container: $DOWNLOAD_DIR"
# print the retention period hours
echo "Retention period in hours: $RETENTION_PERIOD_HOURS"

# ensure DOWNLOAD_DIR exists
if [ ! -d $DOWNLOAD_DIR ]; then
    echo "Creating download directory: $DOWNLOAD_DIR"
    mkdir -p $DOWNLOAD_DIR
fi
envsubst < config.template > config.json

# if session-info.json does not exists in $DOWNLOAD_DIR, create it
if [ ! -f $DOWNLOAD_DIR/session-info.json ]; then
    echo "Creating session-info.json"
    echo "{" > $DOWNLOAD_DIR/session-info.json
    echo '  "topics": {},' >> $DOWNLOAD_DIR/session-info.json
    # generate a random string for client_id
    echo "Generating random client_id"
    echo '  "client_id": "wis2box-wis2downloader-'$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)'"' >> $DOWNLOAD_DIR/session-info.json
    echo "}" >> $DOWNLOAD_DIR/session-info.json
fi

# print the config
echo "Config:"
cat /app/config.json

exec "$@"
