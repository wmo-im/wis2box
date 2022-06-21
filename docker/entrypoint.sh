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

set +e

env

wis2box environment create
if test -f "$WIS2BOX_API_CONFIG"; then
    echo "$WIS2BOX_API_CONFIG already exists."
else
    echo "Creating $WIS2BOX_API_CONFIG."
    cp /wis2box-api/wis2box-api-config.yml $WIS2BOX_API_CONFIG
fi

if [ ! -d "$WIS2BOX_DATADIR/config/csv2bufr" ]; then
  git clone https://github.com/wmo-im/csv2bufr-templates.git $WIS2BOX_DATADIR/config/csv2bufr
fi
