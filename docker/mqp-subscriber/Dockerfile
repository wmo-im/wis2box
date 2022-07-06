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

FROM ubuntu:focal

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
RUN pip install setuptools pip --upgrade --force-reinstall

RUN mkdir -p /data/wis2box/mqp-subscriber
WORKDIR /data/wis2box/mqp-subscriber

COPY requirements.txt /data/wis2box/mqp-subscriber/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install https://github.com/wmo-im/GTStoWIS2.git

RUN mkdir -p /data/wis2box/mqp-subscriber/configFiles
RUN mkdir -p /data/wis2box/mqp-subscriber/log
RUN mkdir -p /data/wis2box/mqp-subscriber/msg_store

COPY configFiles/dwd_v04.txt /data/wis2box/mqp-subscriber/configFiles/
COPY configFiles/wis2box_whitelist.txt /data/wis2box/mqp-subscriber/configFiles/
COPY message-schema.json /data/wis2box/mqp-subscriber/
COPY pubSubDWD_geoJSON.py /data/wis2box/mqp-subscriber/
RUN chmod +x /data/wis2box/mqp-subscriber/pubSubDWD_geoJSON.py

COPY entrypoint.sh /mqp-sub_entrypoint.sh
RUN chmod +x /mqp-sub_entrypoint.sh

ENTRYPOINT [ "/mqp-sub_entrypoint.sh" ]
