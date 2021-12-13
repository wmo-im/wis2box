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

MAINTAINER "tomkralidis@gmail.com"

ENV ECCODES_VER=2.23.0
ENV ECCODES_DIR=/opt/eccodes

RUN apt-get update -y && \
    DEBIAN_FRONTEND="noninteractive" TZ="Europe/Bern" apt-get install -y bash git python3-pip python3-dev build-essential curl cmake gfortran libffi-dev libeccodes0 python3-eccodes && \
    echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until

WORKDIR /tmp/eccodes

RUN git clone https://github.com/wmo-im/csv2bufr.git -b dev && \
    cd csv2bufr && \
    python3 setup.py install && \
    useradd -ms /bin/bash wis2node

# TODO BEGIN: install sarra via debian/pip when stable
RUN apt-get install -y python3-cryptography libssl-dev

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

WORKDIR /tmp/sarracenia

RUN pip install cryptography==3.4.6 wheel && \
    git clone https://github.com/MetPX/sarracenia.git -b v03_wip && \
    cd sarracenia && \
    python3 setup.py install
# TODO END

WORKDIR /app
COPY . /app

RUN python3 setup.py install

USER wis2node
WORKDIR /home/wis2node
