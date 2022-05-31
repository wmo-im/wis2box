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

from datetime import datetime
import json
import logging
from pathlib import Path
import re
from urllib.parse import urlparse

from csv2bufr import transform as transform_csv
import paho.mqtt.publish as publish

from wis2box.data.base import BaseAbstractData
from wis2box.env import DATADIR, DATADIR_CONFIG, DATADIR_PUBLIC, BROKER

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

        mapping_bufr4 = DATADIR_CONFIG / "csv2bufr" / self.template

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

            self.output_data[identifier] = item
            self.output_data[identifier]['_meta']['relative_filepath'] = \
                self.get_local_filepath(data_date)

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return (Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath)

    def notify(self):
        for identifier, item in self.output_data.items():
            LOGGER.debug(f'Notifying product {identifier}')
            # get relative file path
            rfp = item['_meta']['relative_filepath']
            # iterate over formats
            for format_, the_data in item.items():  # only bufr4 and _meta
                if format_ == '_meta':  # not data, skip
                    continue
                filename = (rfp) / f'{identifier}'
                filename = filename.with_suffix(f'.{format_}')
                if the_data is None:
                    msg = f'Empty data for {identifier}-{key}; not publishing'  # noqa
                    LOGGER.warning(msg)
                else:
                    msg = {
                        'pubTime': datetime.now().strftime('%Y%m%dT%H%M%S.00'),
                        # noqa
                        'baseUrl': 'file:/',
                        'relPath': str(DATADIR_PUBLIC / filename),
                        'integrity': {
                            'method': 'md5',
                            'value': item['_meta']['md5']
                        }
                    }
                    msg = json.dumps(msg)

                    LOGGER.debug(
                        f'Publishing: {msg} to {self.topic_hierarchy.dirpath}')  # noqa

                    # Parse BROKER into components
                    o = urlparse(BROKER)

                    # separate uid and pwd from url
                    uidpwd, url = o.netloc.split('@')
                    # now separate uid and pwd
                    uid, pwd = uidpwd.split(':')

                    # set topic
                    topic = f'xlocal/v03/data/wis2box/{self.topic_hierarchy.dirpath}'  # noqa

                    # set arguments for publishing
                    pubargs = {
                        'topic': topic,
                        'payload': msg,
                        'hostname': f'{url}',
                        'auth': {'username': uid, 'password': pwd}
                    }

                    # update port if specified
                    if o.port is not None:
                        pubargs['port'] = o.port

                    # now publish
                    try:
                        publish.single(**pubargs)

                    except Exception as err:
                        LOGGER.error(pubargs)
                        raise err

        return True


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
