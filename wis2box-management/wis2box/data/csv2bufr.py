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
import re
from typing import Union

from csv2bufr import transform as transform_csv

from wis2box.data.base import BaseAbstractData
from wis2box.env import DATADIR, DATADIR_CONFIG

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
        mapping_bufr4 = DATADIR_CONFIG / "csv2bufr" / self.template

        with mapping_bufr4.open() as fh1:
            self.mappings['bufr4'] = json.load(fh1)

        self.station_metadata = None

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        LOGGER.debug('Procesing CSV data')

        if isinstance(input_data, Path):
            LOGGER.debug('input_data is a Path')
            filename = input_data.name

        try:
            LOGGER.debug('Extracting WSI from filename')
            regex = self.file_filter
            wsi = re.match(regex, filename).group(1)
        except AttributeError:
            msg = f'Invalid filename format: {filename} ({self.file_filter})'
            LOGGER.error(msg)
            raise ValueError(msg)

        sm = DATADIR / 'metadata' / 'station' / f'{wsi}.json'
        if not sm.exists():
            msg = f'Missing station metadata file {sm}'
            LOGGER.error(msg)
            raise FileNotFoundError(msg)

        with sm.open() as fh1:
            self.station_metadata = json.load(fh1)

        LOGGER.debug('Generating BUFR4')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Transforming data')
        results = transform_csv(input_bytes.decode(),
                                self.station_metadata,
                                self.mappings['bufr4'])

        # convert to list
        LOGGER.debug('Iterating over BUFR messages')
        for item in results:
            LOGGER.debug('Setting obs date for filepath creation')
            identifier = item['_meta']['identifier']
            data_date = item['_meta']['data_date']

            self.output_data[identifier] = item
            self.output_data[identifier]['_meta']['relative_filepath'] = \
                self.get_local_filepath(data_date)

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return (Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath)
