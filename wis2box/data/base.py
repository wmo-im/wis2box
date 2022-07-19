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
from typing import Iterator, Union

from wis2box.api.backend import load_backend
from wis2box.env import (DATADIR_INCOMING, DATADIR_PUBLIC,
                         STORAGE_PUBLIC, STORAGE_SOURCE, BROKER_PUBLIC)
from wis2box.storage import put_data
from wis2box.topic_hierarchy import TopicHierarchy
from wis2box.plugin import load_plugin, PLUGINS

from wis2box.pubsub.message import WISNotificationMessage

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

    def transform(self, input_data: Union[bytes, str],
                  filename: str = '') -> bool:
        """
        Transform data

        :param input_data: `bytes` or `str` of data payload
        :param filename, to be used in case input_data is bytes

        :returns: `bool` of processing result
        """

        raise NotImplementedError()

    def notify(self, identifier: str, storage_path: str,
               geometry: dict = None) -> bool:
        """
        Publish data to broker

        :param storage_path: path to data on storage
        :param identifier: identifier
        :param geometry: `dict` of GeoJSON geometry object

        :returns: `bool` of result
        """

        LOGGER.info("Publishing WISNotificationMessage to public broker")
        LOGGER.debug(f"storage_path={storage_path}")
        wis_message = WISNotificationMessage(identifier, storage_path,
                                             geometry)
        #  load plugin for broker
        defs = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': BROKER_PUBLIC
        }
        broker = load_plugin('pubsub', defs)
        # TODO how is topic on BROKER_PUBLIC to be defined ??
        topic = 'xpublic/wis2box-data'
        # publish using filename as identifier
        broker.pub(topic, wis_message.dumps())
        LOGGER.info(f'WISNotificationMessage published for {self.filename}')

        LOGGER.debug('Publishing to API')
        api_backend = load_backend()
        api_backend.upsert_collection_items(collection_id='messages',
                                            items=[wis_message.message])
        return True

    def publish(self, notify: bool = False) -> bool:
        # save output_data to disk and send notification if requested
        LOGGER.info('Writing output data')
        # iterate over items to publish
        for identifier, item in self.output_data.items():
            # get relative filepath
            rfp = item['_meta']['relative_filepath']

            # now iterate over formats
            for format_, the_data in item.items():
                if format_ == '_meta':  # not data, skip
                    continue
                # check that we actually have data
                if the_data is not None:
                    storage_path = f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}/{rfp}/{identifier}.{format_}'  # noqa
                    LOGGER.info(f'Writing data to {storage_path}')
                    data_bytes = None
                    if isinstance(the_data, str):
                        data_bytes = str(the_data).encode()
                    elif isinstance(the_data, bytes):
                        data_bytes = the_data
                    else:
                        LOGGER.warning('the_data is neither bytes nor str')
                    LOGGER.debug('Publishing data')
                    put_data(data_bytes, storage_path)
                    if notify:
                        LOGGER.debug('Sending notification to broker')
                        self.notify(item['_meta']['identifier'], storage_path,
                                    item['_meta'].get('geometry'))
                    else:
                        LOGGER.debug('No notification sent')
                else:
                    msg = f'Empty data for {identifier}-{format_}; not publishing'  # noqa
                    LOGGER.warning(msg)
        return True

    def files(self) -> Iterator[str]:
        """
        Provide list of files

        :returns: generator of filenames
        """

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
