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

while true
do
  old_date=$(date -d "- 2 hours" '+%Y%m%d%H%M')
  touch -t $old_date /tmp/old_clean
  listDir_notUsedDownloads=$(find /aria2-downloads -type f ! -newer /tmp/old_clean)
  echo "clean job deleted following files from aria2-download directory: "
  echo "$listDir_notUsedDownloads"
  find /aria2-downloads -type f ! -newer /tmp/old_clean -exec rm {} \;
  echo "clean goes sleeping for one hour"
  sleep 3600
done
