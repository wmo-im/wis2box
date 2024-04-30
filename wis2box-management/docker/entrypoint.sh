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

# wis2box commands
# TODO: avoid re-creating environment if it already exists
# TODO: catch errors and avoid bounce in conjuction with restart: always
wis2box environment create
wis2box environment show
wis2box api setup
wis2box metadata discovery setup
wis2box metadata station setup

echo "Caching topic hierarchy CSVs"
pywis-topics bundle sync

# check if WIS2BOX_WEBAPP_USERNAME and WIS2BOX_WEBAPP_PASSWORD are set, otherwise set them
if [ -z "$WIS2BOX_WEBAPP_USERNAME" ]; then
    echo "WARNING: WIS2BOX_WEBAPP_USERNAME is not set in wis2box.env, using WIS2BOX_WEBAPP_USERNAME=wis2box-user"
    export WIS2BOX_WEBAPP_USERNAME=wis2box-user
fi
if [ -z "$WIS2BOX_WEBAPP_PASSWORD" ]; then
    echo "WARNING: WIS2BOX_WEBAPP_PASSWORD is not set in wis2box.env, using WIS2BOX_STORAGE_PASSWORD"
    export WIS2BOX_WEBAPP_PASSWORD=${WIS2BOX_STORAGE_PASSWORD}
fi

# create directory /home/wis2box/.htpasswd/ if not exists
if [ ! -d /home/wis2box/.htpasswd/ ]; then
    echo "Creating /home/wis2box/.htpasswd/"
    mkdir /home/wis2box/.htpasswd/
fi

# create /home/wis2box/.htpasswd/webapp if not exists
# otherwise, delete the file and create it
# in case of failure continue
if [ ! -f /home/wis2box/.htpasswd/webapp ]; then
    echo "Creating /home/wis2box/.htpasswd/webapp"
    htpasswd -bc /home/wis2box/.htpasswd/webapp $WIS2BOX_WEBAPP_USERNAME $WIS2BOX_WEBAPP_PASSWORD || true
else
    rm /home/wis2box/.htpasswd/webapp
    echo "Re-creating /home/wis2box/.htpasswd/webapp"
    htpasswd -bc /home/wis2box/.htpasswd/webapp $WIS2BOX_WEBAPP_USERNAME $WIS2BOX_WEBAPP_PASSWORD || true
fi

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
# repeat for collections/discovery-metadata
is_restricted=$(wis2box auth is-restricted-path --path collections/discovery-metadata)
if [ "$is_restricted" = "True" ]; then
    echo "collections/discovery-metadata execution is restricted"
else
    echo "restricting collections/discovery-metadata"
    # Add the token
    wis2box auth add-token --path collections/discovery-metadata -y
fi

echo "END /entrypoint.sh"
exec "$@"
