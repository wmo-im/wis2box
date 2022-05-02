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

from csv2bufr import MAPPINGS, transform as transform_csv

from wis2box.data.base import BaseAbstractData
from wis2box.env import DATADIR

LOGGER = logging.getLogger(__name__)


class ObservationDataCSV(BaseAbstractData):
    """Observation data"""
    def __init__(self, topic_hierarchy: str) -> None:
        """
        Abstract data initializer

        :param topic_hierarchy: `wis2box.topic_hierarchy.TopicHierarchy`
                                object

        :returns: `None`
        """

        super().__init__(topic_hierarchy)

        self.mappings = {}
        self.output_data = {}

        mapping_bufr4 = Path(MAPPINGS) / self.template

        with mapping_bufr4.open() as fh1:
            self.mappings['bufr4'] = json.load(fh1)

        self.station_metadata = None

    def transform(self, input_data: Path) -> bool:
        LOGGER.debug('Processing data')

        LOGGER.debug('Extracting WSI from filename')
        try:
            regex = self.file_filter
            wsi = re.match(regex, input_data.name).group(1)
        except AttributeError:
            msg = f'Invalid filename format: {input_data} ({self.file_filter})'
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
        with input_data.open() as fh1:
            results = transform_csv(fh1.read(),
                                    self.station_metadata,
                                    self.mappings['bufr4'])
        # convert to list
        LOGGER.debug('Iterating over BUFR messages')
        for item in results:   # item = { 'bufr4': ..., '_meta': ...}
            LOGGER.debug('Setting obs date for filepath creation')
            identifier = item['_meta']['identifier']
            data_date = item['_meta']['data_date']
            if not isinstance(item['bufr4'], list):  # make sure item[bufr4] is a list. once csv2bufr is changed this can be removed.
                item['bufr4'] = [item['bufr4']]
            self.output_data[identifier] = item
            self.output_data[identifier]['_meta']['relative_filepath'] = \
                self.get_local_filepath(data_date)

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')

        # return (Path(yyyymmdd) / 'wis' / self.publish_topic.dirpath)
        return (Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath)


def process_data(data: str, discovery_metadata: dict) -> bool:
    """
    Data processing workflow for observations

    :param data: `str` of data to be processed
    :param discovery_metadata: `dict` of discovery metadata MCF

    :returns: `bool` of processing result
    """

    d = ObservationDataCSV(discovery_metadata)
    LOGGER.info('Transforming data')
    d.transform(data)
    LOGGER.info('Publishing data')
    d.publish()

    return True
