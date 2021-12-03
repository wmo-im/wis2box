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
import logging

from wis2node.env import DATADIR_OUTGOING


LOGGER = logging.getLogger(__name__)


def get_today_as_string() -> str:
    """
    Helper function to generate today's date as YYYY-MM-DD

    :returns: `str` representation of YYYY-MM-DD
    """

    return datetime.today().strftime('%Y-%m-%d')


class AbstractData:
    """Abstract data"""
    def __init__(self, input_data: str, discovery_metadata: dict):
        """
        Abstract data initializer

        :param input_data: `str` of data payload
        :param discovery_metadata: `dict` of discovery metadata MCF
        """

        self.filename = None
        self.file_extension = None
        self.incoming_filepath = None

        self.input_data = input_data
        self.output_data = {}
        self.discovery_metadata = discovery_metadata
        self.date = get_today_as_string()

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
        if self.file_extension is None:
            raise ValueError('File extension not set')

        LOGGER.debug('Writing output data')
        for key, value in self.output_data.items():
            filename = self.public_filepath / key
            filename = filename.with_suffix(f'.{self.file_extension}')

            LOGGER.debug(f'Writing data to {filename}')
            filename.parent.mkdir(parents=True, exist_ok=True)

            with filename.open('wb') as fh:
                fh.write(value.read())

        return True

    @property
    def outgoing_filepath(self):
        """Outgoing filepath"""

        return DATADIR_OUTGOING / self.filename

    @property
    def public_filepath(self):
        """Public filepath"""

        raise NotImplementedError()

    def __repr__(self):
        return '<AbstractData>'
