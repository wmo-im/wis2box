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

ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    BUILD_PACKAGES="build-essential cmake gfortran python3-wheel" \
    ECCODES_VER="2.23.0" \
    ECCODES_DIR="/opt/eccodes" \
    PATH="$PATH;/opt/eccodes/bin"

COPY . /wis2node

# FIXME: eccodes: install latest stable from packages
# FIXME: csv2bufr: remove and install from requirements.txt once we have a stable release
# FIXME: pygeometa: remove and install from requirements.txt once we have a stable release
# FIXME: sarracenia: remove install from requirements.txt once we have a stable release
RUN apt-get update -y \
    && apt-get install -y ${BUILD_PACKAGES} \
    && apt-get install -y bash git python3-pip python3-dev python3-setuptools curl libffi-dev python3-cryptography libssl-dev \
    # install eccodes
    && mkdir -p /tmp/eccodes \
    && cd /tmp/eccodes \
    && curl https://confluence.ecmwf.int/download/attachments/45757960/eccodes-${ECCODES_VER}-Source.tar.gz --output eccodes-${ECCODES_VER}-Source.tar.gz \
    && tar xzf eccodes-${ECCODES_VER}-Source.tar.gz \
    && mkdir build && cd build && cmake -DCMAKE_INSTALL_PREFIX=${ECCODES_DIR} ../eccodes-${ECCODES_VER}-Source && make && ctest && make install \
    && cd / \
    && rm -rf /tmp/eccodes \
    # install wis2node dependencies
    && pip3 install eccodes \
    && pip3 install https://github.com/wmo-im/csv2bufr/archive/dev.zip \
    && pip3 install https://github.com/geopython/pygeometa/archive/master.zip \
    && pip3 install https://github.com/metpx/sarracenia/archive/v03_wip.zip \
    # install wis2node
    && cd /wis2node \
    && python3 setup.py install \
    # cleanup
    && apt-get remove --purge -y ${BUILD_PACKAGES} \
    && apt autoremove -y  \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/* \
    # add wis2node user
    && useradd -ms /bin/bash wis2node

USER wis2node
WORKDIR /home/wis2node
