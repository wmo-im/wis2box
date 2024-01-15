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


import base64
import logging
import requests

from pathlib import Path
from typing import Union

from wis2box.data.geojson import ObservationDataGeoJSON
from wis2box.env import DOCKER_API_URL

LOGGER = logging.getLogger(__name__)


class ObservationDataBUFR2GeoJSON(ObservationDataGeoJSON):
    """Observation data"""

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        LOGGER.debug('Procesing BUFR data')

        LOGGER.debug('Posting data to wis2box-api')
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        url = f'{DOCKER_API_URL}/processes/bufr2geojson/execution'

        # check if input_data is Path object
        if isinstance(input_data, Path):
            payload = {
                'inputs': {
                    'data_url': input_data.as_posix()
                }
            }
        else:
            input_bytes = self.as_bytes(input_data)
            payload = {
                'inputs': {
                    'data': base64.b64encode(input_bytes).decode('utf-8')
                }
            }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            msg = f'Failed to post data to wis2box-api: {response.status_code}'
            LOGGER.error(msg)
            raise ValueError(msg)

        result = response.json()

        # check for errors
        if 'error' in result and result['error'] != '':
            LOGGER.error(result['error'])

        if 'items' not in result:
            LOGGER.error(f'file={filename} failed to convert to geojson')
            return False

        # loop over items in response
        for item in result['items']:
            id = item['id']

            data_date = item['properties']['resultTime']
            self.output_data[id] = {
                '_meta': {
                    'identifier': id,
                    'data_date': data_date,
                    'relative_filepath': self.get_local_filepath(data_date),
                },
                'geojson': item
            }

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
