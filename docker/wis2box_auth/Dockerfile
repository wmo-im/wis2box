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

FROM python:3.9.13-slim

LABEL maintainer="tomkralidis@gmail.com"

ENV DEBIAN_FRONTEND="noninteractive" \
    DEBIAN_PACKAGES="python3-pip python3-setuptools python3-distutils python3-flask python3-flask-cors python3-gevent gunicorn python3-dateparser python3-tz"

RUN apt-get update -y \
    && apt-get install -y ${DEBIAN_PACKAGES} \
    # cleanup
    && apt autoremove -y  \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

# copy the app
COPY . /app
# install wis2box_auth
RUN cd /app \
    && pip3 install -r requirements.txt \
    && python3 setup.py install

COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
