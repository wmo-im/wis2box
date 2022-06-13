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

from wis2box.env import DATADIR_INCOMING, DATADIR_PUBLIC
from wis2box.topic_hierarchy import TopicHierarchy

LOGGER = logging.getLogger(__name__)


class BaseAbstractData:
    """Abstract data"""

    def __init__(self, defs: dict) -> None:
        """
        Abstract data initializer

        :param topic_hierarchy: `wis2box.topic_hierarchy.TopicHierarchy`
                                object

        :returns: `None`
        """

        self.filename = None
        self.incoming_filepath = None
        self.topic_hierarchy = TopicHierarchy(defs['topic_hierarchy'])
        self.template = defs['template']
        self.file_filter = defs['pattern']
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

        self.originator = discovery_metadata['wis2box']['originator']
        self.data_category = discovery_metadata['wis2box']['data_category']
        self.country_code = discovery_metadata['wis2box']['country_code']
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

        :returns: `bool` of processing result
        """

        raise NotImplementedError()

    def notify(self) -> bool:
        raise NotImplementedError()

    def publish(self, notify: bool = False) -> bool:
        # save output_data to disk and send notification if requested
        LOGGER.info('Writing output data')
        LOGGER.info(self.__repr__)
        # iterate over items to publish
        for identifier, item in self.output_data.items():
            # get relative filepath
            rfp = item['_meta']['relative_filepath']
            # now iterate over formats
            for format_, the_data in item.items():
                if format_ == '_meta':  # not data, skip
                    continue
                # check that we actually have data
                if the_data is None:
                    msg = f'Empty data for {identifier}-{key}; not publishing'  # noqa
                    LOGGER.warning(msg)
                filename = DATADIR_PUBLIC / (rfp) / f"{identifier}.{format_}"
                filename = filename.with_suffix(f'.{format_}')
                LOGGER.info(f'Writing data to {filename}')
                # make sure directory structure exists
                filename.parent.mkdir(parents=True, exist_ok=True)
                # check the mode we want to write data in
                if isinstance(the_data, bytes):
                    mode = 'wb'
                else:
                    mode = 'w'
                with filename.open(mode) as fh:
                    fh.write(item[format_])
        if notify:
            self.notify()
        return True

    # TODO: fix annotation/types

    def files(self) -> bool:
        LOGGER.debug('Listing processed files')
        for identifier, item in self.output_data.items():
            rfp = item['_meta']['relative_filepath']
            for format_, the_data in item.items():
                if format_ == '_meta':
                    continue
                if the_data is None:
                    continue

                filename = DATADIR_PUBLIC / (rfp) / f'{identifier}'
                filename = filename.with_suffix(f'.{format_}')
                yield filename

    @property
    def directories(self):
        """Dataset directories"""

        dirpath = self.topic_hierarchy.dirpath

        return {
            'incoming': DATADIR_INCOMING / dirpath
            # 'public': DATADIR_PUBLIC / dirpath
        }

    def get_public_filepath(self):
        """Public filepath"""

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseAbstractData>'
