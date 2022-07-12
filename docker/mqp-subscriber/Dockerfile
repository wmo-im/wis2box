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

FROM python:3.8-slim-buster

ENV NO_PROXY="0.0.0.0,localhost,elasticsearch,aria2-pro"

RUN mkdir -p /usr/src/sub
RUN mkdir -p /usr/src/sub/configFiles
RUN mkdir -p /usr/src/sub/log
RUN mkdir -p /usr/src/sub/msg_store
RUN mkdir -p /usr/src/sub/caFiles

WORKDIR /usr/src/sub

COPY requirements.txt /usr/src/sub/
RUN pip install --no-cache-dir -r requirements.txt

COPY pubSubDWD_geoJSON.py /usr/src/sub/
COPY message-schema.json /usr/src/sub/

COPY configFiles/dwd_v04.txt /usr/src/sub/configFiles/
COPY configFiles/wis2box_whitelist.txt /usr/src/sub/configFiles/

COPY entrypoint.sh /mqp-sub_entrypoint.sh
RUN chmod +x /mqp-sub_entrypoint.sh

COPY cleanAria2Download.sh /cleanAria2Download.sh
RUN chmod +x /cleanAria2Download.sh

ENV PYTHONUNBUFFERED="true"

#ENTRYPOINT [ "/mqp-sub_entrypoint.sh" ]
