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

# wis2box-download entry script

echo "START /entrypoint.sh"

set -e

cp /app/local.base.yml /app/local.yml

# replace BROKER_DOWNLOAD_PATH
sed -i 's/BROKER_DOWNLOAD_PATH/$BROKER_DOWNLOAD_PATH/g' /app/local.yml

# add topics 
echo 'topics:' > /app/local.yml

IFS=,
for topic in $DOWNLOAD_TOPICS:
    echo '  - '$topic > /app/local.yml

echo "END /entrypoint.sh"
exec "$@"