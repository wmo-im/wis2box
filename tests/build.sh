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
echo "START /build.sh"

set +e
echo "Begining build"

ogr2ogr \
	-f PostgreSQL \
	PG:"host='${POSTGRES_HOST}' \
	    user='${POSTGRES_USER}' \
		password='${POSTGRES_PASSWORD}' \
		dbname='${POSTGRES_DB}'" \
	/data/observations.csv \
    -oo X_POSSIBLE_NAMES=X \
    -oo Y_POSSIBLE_NAMES=Y \
    -oo Z_POSSIBLE_NAMES=Z \
    -a_srs 'EPSG:4326'

echo "Done"