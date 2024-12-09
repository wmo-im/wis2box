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

import json
import logging
from pathlib import Path
from typing import Union

from wis2box.api import upsert_collection_item
from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class ObservationDataGeoJSON(BaseAbstractData):
    """Observation data"""

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        LOGGER.debug('Procesing GeoJSON data')
        data_ = json.loads(input_data)
        identifier = data_['id']
        data_date = data_['properties']['reportTime']
        self.output_data[identifier] = {
            '_meta': {
                'identifier': identifier,
                'data_date': data_date,
                'relative_filepath': self.get_local_filepath(data_date)
                },
            'geojson': data_
        }

    def publish(self) -> bool:
        LOGGER.info('Publishing output data')
        for identifier, item in self.output_data.items():
            # now iterate over formats
            for format_, the_data in item.items():
                if format_ == '_meta':  # not data, skip
                    continue

                LOGGER.debug(f'Processing format: {format_}')
                # check that we actually have data
                if the_data is None:
                    msg = f'Empty data for {identifier}-{format_}; not publishing'  # noqa
                    LOGGER.warning(msg)
                    continue

                LOGGER.debug('Publishing data to API')
                upsert_collection_item(self.metadata_id, the_data)

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.metadata_id
