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
from typing import Union

from wis2node.env import DATADIR_CONFIG, DATADIR_INCOMING, DATADIR_PUBLIC
from wis2node.topic_hierarchy import TopicHierarchy

LOGGER = logging.getLogger(__name__)


class BaseAbstractData:
    """Abstract data"""
    def __init__(self, topic_hierarchy: TopicHierarchy) -> None:
        """
        Abstract data initializer

        :param topic_hierarchy: `wis2node.topic_hierarchy.TopicHierarchy`
                                object

        :returns: `None`
        """

        self.filename = None
        self.incoming_filepath = None
        self.topic_hierarchy = TopicHierarchy(topic_hierarchy)

        self.output_data = {}
        self.discovery_metadata = {}

#        if discovery_metadata:
#            self.setup_discovery_metadata(discovery_metadata)

    def setup_discovery_metadata(self, discovery_metadata: dict) -> None:
        """
        Import discovery metadata

        :param discovery_metadata: `dict` of discovery metadata MCF

        :returns: `None`
        """

        self.discovery_metadata = discovery_metadata

        self.topic_hierarchy = TopicHierarchy(
            discovery_metadata['metadata']['identifier'])

        self.originator = discovery_metadata['wis2node']['originator']
        self.data_category = discovery_metadata['wis2node']['data_category']
        self.country_code = discovery_metadata['wis2node']['country_code']
        self.representation = None

    def setup_dirs(self) -> bool:
        """
        Create directory structure

        :returns: `bool` of result
        """

        for key, value in self.directories.items():
            LOGGER.debug(f'Creating directory {key} => {value}')
            value.mkdir(parents=True, exist_ok=True)

        return True

    def transform(self, input_data: Union[bytes, str]) -> bool:
        """
        Transform data

        :param input_data: `bytes` or `str` of data payload

        :returns: `bool` of processsing result
        """

        raise NotImplementedError()

    def publish(self) -> bool:
        LOGGER.debug('Writing output data')
        for key, value in self.output_data.items():
            LOGGER.debug(f'Writing product {key}')

            rfp = value['_meta']['relative_filepath']

            for key2, value2 in value.items():
                if key2 == '_meta':
                    continue
                filename = DATADIR_PUBLIC / (rfp) / key
                filename = filename.with_suffix(f'.{key2}')

                LOGGER.debug(f'Writing data to {filename}')
                filename.parent.mkdir(parents=True, exist_ok=True)

                if isinstance(value2, bytes):
                    mode = 'wb'
                if isinstance(value2, str):
                    mode = 'w'

                with filename.open(mode) as fh:
                    fh.write(value2)

                if key2 == 'geojson':
                    LOGGER.debug('Publishing data to API')

        return True

    # TODO: fix annotation/types
    def files(self) -> bool:
        LOGGER.debug('Listing processed files')
        for key, value in self.output_data.items():
            rfp = value['_meta']['relative_filepath']
            for key2, value2 in value.items():
                if key2 == '_meta':
                    continue
                filename = DATADIR_PUBLIC / (rfp) / key
                yield filename.with_suffix(f'.{key2}')

    @property
    def directories(self):
        """Dataset directories"""

        dirpath = self.topic_hierarchy.dirpath

        return {
            'config': DATADIR_CONFIG / dirpath,
            'incoming': DATADIR_INCOMING / dirpath,
            # 'public': DATADIR_PUBLIC / dirpath
        }

    def get_public_filepath(self):
        """Public filepath"""

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseAbstractData>'
