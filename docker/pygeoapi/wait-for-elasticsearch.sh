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

set -e

host="$1"
shift
cmd="$@"


until $(curl --output /dev/null --silent --head --fail "$host")  ; do
    echo 'Checking if Elasticsearch server is up'
    sleep 5
    counter=$((counter+1))
done

# First wait for ES to start...
response=$(curl $host)

until [ "$response" = "200" ]  ; do
    response=$(curl --write-out %{http_code} --silent --output /dev/null "$host")
    >&2 echo "Elasticsearch is up but unavailable - No Response - sleeping"
    sleep 10

done


# next wait for ES status to turn to green or yellow
health="$(curl -fsSL "$host/_cat/health?h=status")"
health="$(echo "$health" | sed -r 's/^[[:space:]]+|[[:space:]]+$//g')" # trim whitespace (otherwise we'll have "green ")

until [ "$health" = 'yellow'  ] || [ "$health" = 'green'  ]  ; do
    health="$(curl -fsSL "$host/_cat/health?h=status")"
    health="$(echo "$health" | sed -r 's/^[[:space:]]+|[[:space:]]+$//g')"
    >&2 echo "Elasticsearch status is not green or yellow - sleeping"
    sleep 10
done

>&2 echo "Elasticsearch is up"


exec $cmd
