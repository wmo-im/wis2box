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

FROM alpine:3.11

MAINTAINER "tomkralidis@gmail.com"

RUN apk add py3-pip build-base python3-dev libffi-dev git

ENV METPX_SR3_HOST ${METPX_SR3_HOST}
ENV METPX_SR3_BROKER_USERNAME ${METPX_SR3_BROKER_USERNAME}
ENV METPX_SR3_BROKER_PASSWORD ${METPX_SR3_BROKER_PASSWORD}
ENV METPX_SR3_PATH ${METPX_SR3_PATH}
ENV METPX_SR3_BASEURL ${METPX_SR3_BASEURL}

RUN python3 -m pip install --upgrade pip && \
    pip3 install wheel && \
    pip3 install metpx-sr3
    #pip3 install metpx-sarracenia

COPY ./sr3_watch.conf /etc/metpx-sr3/sr3_watch.conf

CMD ["sr3", "foreground", "/etc/metpx-sr3/sr3_watch.conf"]
