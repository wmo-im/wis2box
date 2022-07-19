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

import logging

from pyoscar import OSCARClient

from ..env import OSCAR_API_TOKEN

LOGGER = logging.getLogger(__name__)


def upload_station_metadata(record: str) -> None:
    """
    Uploads a WIGOS Metadata Record (WMDR) to WMO OSCAR/Surface

    :param record: `str` of WMDR

    :returns: None
    """

    client = OSCARClient(api_token=OSCAR_API_TOKEN, env='prod')

    LOGGER.debug(f'Uploading metadata to OSCAR {client.api_url}')
    return client.upload(record)


def get_station_report(identifier: str) -> dict:
    """
    Fetch OSCAR/Surface station metadata report

    :param identifier: WIGOS Station Identifier (WSI)

    :returns: `dict` of station metadata report
    """

    client = OSCARClient(api_token=OSCAR_API_TOKEN)

    LOGGER.debug(f'Fetching station report for {identifier}')
    return client.get_station_report(identifier)
