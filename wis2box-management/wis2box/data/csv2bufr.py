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

from csv2bufr import MAPPINGS, transform as transform_csv

from wis2box.data.base import BaseAbstractData
from wis2box.metadata.station import get_valid_wsi

LOGGER = logging.getLogger(__name__)


class ObservationDataCSV2BUFR(BaseAbstractData):
    """Observation data"""
    def __init__(self, defs: dict) -> None:
        """
        ObservationDataCSV2BUFR data initializer

        :param def: `dict` object of resource mappings

        :returns: `None`
        """

        super().__init__(defs)

        self.mappings = {}
        
        LOGGER.debug(f'Loading template {self.template}')
        if self.template.startswith('/'):
            mapping_bufr4 = self.template            
        else:
            mapping_bufr4 = Path(MAPPINGS) / self.template        

        with mapping_bufr4.open() as fh1:
            self.mappings['bufr4'] = json.load(fh1)

        self.station_metadata = None

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        LOGGER.debug('Processing CSV data')

        if isinstance(input_data, Path):
            LOGGER.debug('input_data is a Path')
            filename = input_data.name

        if self.validate_filename_pattern(filename) is None:
            msg = f'Invalid filename format: {filename} ({self.file_filter})'
            LOGGER.error(msg)
            raise ValueError(msg)

        LOGGER.debug('Generating BUFR4')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Transforming data')
        results = transform_csv(input_bytes.decode(),
                                self.mappings['bufr4'])

        # convert to list
        LOGGER.debug('Iterating over BUFR messages')
        for item in results:
            wsi = item['_meta']['properties']['wigos_station_identifier']
            if get_valid_wsi(wsi) is None:
                msg = f'Station not in station list: wsi={wsi}; skipping'
                LOGGER.error(msg)
                self.publish_failure_message(
                        description="Station not in station list",
                        wsi=wsi)
                continue
            LOGGER.debug('Setting obs date for filepath creation')
            identifier = item['_meta']['id']
            data_date = item['_meta']['properties']['datetime']

            self.output_data[identifier] = item
            self.output_data[identifier]['_meta']['relative_filepath'] = \
                self.get_local_filepath(data_date)

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return (Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath)
