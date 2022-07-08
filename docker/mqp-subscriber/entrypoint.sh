#!/bin/sh
###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

set +e
DIR="/data/wis2box/config/mqp-subscriber"
if [ -d "$DIR" ]; then
  echo "$DIR already exists"
  DIR2="/data/wis2box/config/mqp-subscriber/configFiles"
  if [ -d "$DIR2" ]; then
    echo "$DIR2 already exists"
    FILE="/data/wis2box/config/mqp-subscriber/configFiles/dwd_v04.txt"
    if [ -f "$FILE" ]; then
      echo "$FILE already exists"
    else
      cp /usr/src/sub/configFiles/dwd_v04.txt /data/wis2box/config/mqp-subscriber/configFiles/
    fi
    FILE2="/data/wis2box/config/mqp-subscriber/configFiles/wis2box_whitelist.txt"
    if [ -f "$FILE2" ]; then
      echo "$FILE2 already exists"
    else
      cp /usr/src/sub/configFiles/wis2box_whitelist.txt /data/wis2box/config/mqp-subscriber/configFiles/
    fi
  else
    mkdir /data/wis2box/config/mqp-subscriber/configFiles
    cp /usr/src/sub/configFiles/dwd_v04.txt /data/wis2box/config/mqp-subscriber/configFiles/
  fi
else
  mkdir /data/wis2box/config/mqp-subscriber
  mkdir /data/wis2box/config/mqp-subscriber/configFiles
  cp /usr/src/sub/configFiles/dwd_v04.txt /data/wis2box/config/mqp-subscriber/configFiles/
  cp /usr/src/sub/configFiles/wis2box_whitelist.txt /data/wis2box/config/mqp-subscriber/configFiles/
fi

cp /usr/src/sub/caFiles/tls-ca-bundle.pem /usr/src/sub/configFiles/ca-bundle.crt

PID_FILE="/data/wis2box/config/mqp-subscriber/configFiles/dwd_sub.txt"
python3 /usr/src/sub/pubSubDWD_geoJSON.py --config /data/wis2box/config/mqp-subscriber/configFiles/dwd_v04.txt
echo $! > $PID_FILE

# check process running
PID=$(cat $PID_FILE)
if ! kill -0 $PID 2>/dev/null;
then
  echo "$PID not running exit container"
  SUB_RUNNING=false
else
  SUB_RUNNING=true
fi

while $SUB_RUNNING
do
  if ! kill -0 $PID 2>/dev/null;
  then
    echo "$PID not running exit container"
    SUB_RUNNING=false
  else
    sleep 10
  fi
done
# sleep infinity

