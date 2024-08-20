#!/bin/bash
echo "Download directory in container: $DOWNLOAD_DIR"

ls -althF
ls -althF /home/wis2downloader/app
ls -althF /home/wis2downloader/app/data

# ensure DOWNLOAD_DIR exists
if [ ! -d "$DOWNLOAD_DIR" ]; then
    echo "Creating download directory: $DOWNLOAD_DIR"
    mkdir -p "$DOWNLOAD_DIR"
fi

envsubst < /home/wis2downloader/app/config/config.template > /home/wis2downloader/app/config/config.json

# if session-info.json does not exists in $DOWNLOAD_DIR, create it
if [ ! -f "$DOWNLOAD_DIR/.session-info.json" ]; then
    echo "Creating .session-info.json"
    echo "{" > "$DOWNLOAD_DIR/.session-info.json"
    echo '  "topics": {},' >> "$DOWNLOAD_DIR/.session-info.json"
    # generate a random string for client_id
    echo "Generating random client_id"
    client_id=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 32 | head -n 1)
    echo "  \"client_id\": \"wis2box-wis2downloader-${client_id}\"" >> "$DOWNLOAD_DIR/.session-info.json"
    echo "}" >> "$DOWNLOAD_DIR/.session-info.json"
fi

# print the config
echo "Config:"
cat /home/wis2downloader/app/config/config.json
echo "Initial session info:"
cat "$DOWNLOAD_DIR/.session-info.json"
# activate python env
# shellcheck source=/dev/null
source /home/wis2downloader/.venv/bin/activate
exec "$@"