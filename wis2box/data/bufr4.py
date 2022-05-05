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

from bufr2geojson import transform as as_geojson

from wis2box.data.base import BaseAbstractData
from wis2box.env import DATADIR_PUBLIC

LOGGER = logging.getLogger(__name__)


class ObservationDataBUFR(BaseAbstractData):
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

    def transform(self, input_data: Path) -> bool:
        LOGGER.debug('Processing bufr data')
        fh = open(input_data)
        results = as_geojson(fh)
        LOGGER.debug('Iterating over GeoJSON features')
        # need to fix the next section, need to iterate over item['geojson']
        for collection in results:
            LOGGER.debug(collection)
            for key, item in collection.items():
                LOGGER.debug("Processing feature")
                LOGGER.debug('Setting obs date for filepath creation')
                identifier = key
                data_date = item['_meta']['data_date']
                # some dates can be range/period, split and get end date/time
                if '/' in data_date:
                    data_date = data_date.split("/")[1]
                self.output_data[identifier] = item
                LOGGER.debug('Setting relative path')
                self.output_data[identifier]['_meta']['relative_filepath'] = \
                    self.get_local_filepath(data_date)
        fh.close()
        LOGGER.debug("Transform complete")
        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')

        # return (Path(yyyymmdd) / 'wis' / self.publish_topic.dirpath)
        return (Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath)

    def files(self) -> bool:
        LOGGER.debug('Listing processed files')
        for identifier, item in self.output_data.items():
            rfp = item['_meta']['relative_filepath']
            filename = DATADIR_PUBLIC / (rfp) / f"{identifier}.geojson"
            yield filename

    def publish(self) -> bool:
        LOGGER.debug('Saving data files')
        for identifier, item in self.output_data.items():
            rfp = item['_meta']['relative_filepath']
            filename = DATADIR_PUBLIC / (rfp) / f"{identifier}.geojson"
            with filename.open('w') as fh:
                fh.write(json.dumps(item['geojson'], indent=4))
        return True

def process_data(data: str, discovery_metadata: dict) -> bool:
    """
    Data processing workflow for observations

    :param data: `str` of data to be processed
    :param discovery_metadata: `dict` of discovery metadata MCF

    :returns: `bool` of processing result
    """

    d = ObservationDataBUFR(discovery_metadata)
    LOGGER.info('Transforming data')
    d.transform(data)
    LOGGER.info('Publishing data')
    d.publish()

    return True
