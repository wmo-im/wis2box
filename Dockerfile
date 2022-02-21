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

ARG WIS2BOX_PIP3_EXTRA_PACKAGES
ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    BUILD_PACKAGES="build-essential cmake gfortran python3-wheel"

COPY docker/wis2box/config /root/.config/sr3

COPY . /app

RUN if [ "$WIS2BOX_PIP3_EXTRA_PACKAGES" = "None" ]; \
    then export WIS2BOX_PIP3_EXTRA_PACKAGES=echo; \
    else export WIS2BOX_PIP3_EXTRA_PACKAGES=pip3 install ${WIS2BOX_PIP3_EXTRA_PACKAGES}; \
    fi

# FIXME: install newer version of eccodes
# FIXME: csv2bufr: remove and install from requirements.txt once we have a stable release
# FIXME: pygeometa: remove and install from requirements.txt once we have a stable release
# FIXME: sarracenia: remove install from requirements.txt once we have a stable release
# TODO: remove build packages for a smaller image
RUN apt-get update -y \
    && apt-get install -y ${BUILD_PACKAGES} \
    && apt-get install -y bash vim git python3-pip python3-dev curl libffi-dev libeccodes0 python3-eccodes python3-cryptography libssl-dev libudunits2-0 \
    # install wis2box dependencies
    && pip3 install https://github.com/wmo-im/csv2bufr/archive/dev.zip \
    && pip3 install https://github.com/geopython/pygeometa/archive/master.zip \
    && pip3 install https://github.com/metpx/sarracenia/archive/v03_wip.zip \
    # install wis2box
    && cd /app \
    && python3 setup.py install \
    # install wis2box plugins, if defined
    && $PIP_PLUGIN_PACKAGES \
    # cleanup
    && apt-get remove --purge -y ${BUILD_PACKAGES} \
    && apt autoremove -y  \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/* \
    # add wis2box user
    && useradd -ms /bin/bash wis2box

WORKDIR /home/wis2box

CMD sh -c "wis2box environment create && sr3 --logStdout start && sleep infinity"
