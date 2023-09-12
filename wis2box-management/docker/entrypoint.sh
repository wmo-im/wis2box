#!/bin/bash
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

# wis2box entry script

echo "START /entrypoint.sh"

set -e

#ensure environment-variables are available for cronjob
printenv | grep -v "no_proxy" >> /etc/environment

# ensure cron is running
service cron start
service cron status

echo "Caching topic hierarchy JSON"
rm -fr /tmp/all.json /tmp/all.json.zip ~/.pywcmp/wis2-topic-hierarchy
mkdir -p ~/.pywcmp/wis2-topic-hierarchy
curl https://wmo-im.github.io/wis2-topic-hierarchy/all.json.zip --output /tmp/all.json.zip
cd ~/.pywcmp/wis2-topic-hierarchy && unzip -j /tmp/all.json.zip

# wis2box commands
# TODO: avoid re-creating environment if it already exists
# TODO: catch errors and avoid bounce in conjuction with restart: always
wis2box environment create
wis2box environment show | grep -v "password" | grep -v "PASSWORD"  # avoid printing passwords in logs
wis2box api setup
wis2box metadata discovery setup
wis2box metadata station publish-collection

# Check if the path is restricted and capture the output
is_restricted=$(wis2box auth is-restricted-path --path processes/wis2box)
if [ "$is_restricted" = "True" ]; then
    echo "processes/wis2box execution is restricted"
else
    echo "restricting processes/wis2box"
    # Add the token
    wis2box auth add-token --path processes/wis2box -y
fi
# repeat for collections/stations
is_restricted=$(wis2box auth is-restricted-path --path collections/stations)
if [ "$is_restricted" = "True" ]; then
    echo "collections/stations execution is restricted"
else
    echo "restricting collections/stations"
    # Add the token
    wis2box auth add-token --path collections/stations -y
fi

echo "END /entrypoint.sh"
exec "$@"
