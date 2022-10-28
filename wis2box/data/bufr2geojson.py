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

from copy import deepcopy
import logging
from pathlib import Path
from typing import Union

from bufr2geojson import transform as as_geojson
from wis2box.data.geojson import ObservationDataGeoJSON

LOGGER = logging.getLogger(__name__)


class ObservationDataBUFR2GeoJSON(ObservationDataGeoJSON):
    """Observation data"""

    def transform(
        self, input_data: Union[Path, bytes], filename: str = ''
    ) -> bool:

        LOGGER.debug('Procesing BUFR data')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Generating GeoJSON features')
        results = as_geojson(input_bytes, serialize=False)

        LOGGER.debug('Processing GeoJSON features')
        for collection in results:
            # results is an iterator, for each iteration we have:
            # - dict['id']
            # - dict['id']['_meta']
            # - dict['id']
            for id, item in collection.items():
                LOGGER.debug(f'Processing feature: {id}')

                LOGGER.debug('Parsing feature datetime')
                data_date = item['_meta']['data_date']
                if '/' in data_date:
                    # date is range/period, split and get end date/time
                    data_date = data_date.split('/')[1]

                LOGGER.debug('Parsing feature fields')
                items_to_remove = [
                    key for key in item if key not in ('geojson', '_meta')
                ]
                for key in items_to_remove:
                    LOGGER.debug(f'Removing unexpected key: {key}')
                    item.pop(key)

                LOGGER.debug('Populating output data for publication')
                self.output_data[id] = item

                self.output_data[id]['_meta'][
                    'relative_filepath'
                ] = self.get_local_filepath(data_date)

        LOGGER.debug('Successfully finished transforming BUFR data')
        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
