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

from wis2node.env import DATADIR_PUBLIC
from wis2node.env import DATADIR_OUTGOING


LOGGER = logging.getLogger(__name__)


class AbstractData:
    """Abstract data"""
    def __init__(self, input_data: str, discovery_metadata: dict):
        """
        Abstract data initializer

        :param input_data: `str` of data payload
        :param discovery_metadata: `dict` of discovery metadata MCF
        """

        self.filename = None
        self.incoming_filepath = None

        self.input_data = input_data
        self.output_data = {}
        self.discovery_metadata = discovery_metadata

        self.topic_hierarchy = self.discovery_metadata['metadata']['identifier']  # noqa

        self.representation = None
        self.originating_centre = None
        self.data_category = None

    def transform(self) -> bool:
        """
        Transform data

        :returns: `bool` of processsing result
        """

        raise NotImplementedError()

    def publish(self) -> bool:
        LOGGER.debug('Writing output data')
        for key, value in self.output_data.items():
            LOGGER.debug('Writing product {key}')

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

        return True

    @property
    def outgoing_filepath(self):
        """Outgoing filepath"""

        return DATADIR_OUTGOING / self.filename

    def get_public_filepath(self):
        """Public filepath"""

        raise NotImplementedError()

    def __repr__(self):
        return '<AbstractData>'
