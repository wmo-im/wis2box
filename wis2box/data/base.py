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
from typing import Iterator, Union

from wis2box.api import upsert_collection_item
from wis2box.env import (STORAGE_INCOMING, STORAGE_PUBLIC,
                         STORAGE_SOURCE, BROKER_PUBLIC,
                         BROKER_HOST, BROKER_USERNAME, BROKER_PASSWORD,
                         BROKER_PORT)
from wis2box.storage import put_data
from wis2box.topic_hierarchy import TopicHierarchy
from wis2box.plugin import load_plugin, PLUGINS

from wis2box.event.messages.message import WISNotificationMessage

LOGGER = logging.getLogger(__name__)


class BaseAbstractData:
    """Abstract data"""

    def __init__(self, defs: dict) -> None:
        """
        Abstract data initializer

        :param def: `dict` object of resource mappings

        :returns: `None`
        """

        LOGGER.debug('Parsing resource mappings')
        self.filename = None
        self.incoming_filepath = None
        self.topic_hierarchy = TopicHierarchy(defs['topic_hierarchy'])
        self.template = defs['template']
        self.file_filter = defs['pattern']
        self.enable_notification = defs['notify']
        self.buckets = defs['buckets']
        self.output_data = {}
        self.discovery_metadata = {}

        # load plugin for local broker
        defs2 = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': f"mqtt://{BROKER_USERNAME}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}", # noqa
            'client_type': 'notify-publisher'
        }
        self.local_broker = load_plugin('pubsub', defs2)

#        if discovery_metadata:
#            self.setup_discovery_metadata(discovery_metadata)

    def publish_failure_message(self, description, wsi=None):
        message = {
            'filepath': self.incoming_filepath,
            'description': description
        }
        if wsi is not None:
            message['wigos_station_identifier'] = wsi
        # publish message
        self.local_broker.pub('wis2box/failure', json.dumps(message))

    def setup_discovery_metadata(self, discovery_metadata: dict) -> None:
        """
        Import discovery metadata

        :param discovery_metadata: `dict` of discovery metadata MCF

        :returns: `None`
        """

        self.discovery_metadata = discovery_metadata

        self.topic_hierarchy = TopicHierarchy(
            discovery_metadata['metadata']['identifier'])

        self.center_id = discovery_metadata['wis2box']['center_id']
        self.data_category = discovery_metadata['wis2box']['data_category']
        self.country = discovery_metadata['wis2box']['country']
        self.representation = None

    def accept_file(self, filename: str = '') -> bool:
        """
        Transform data

        :param filename, file path
        :returns: `bool` of processing result
        """
        if self.buckets == ():
            return True
        else:
            for b in self.buckets:
                if b in str(filename):
                    return True
        return False

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
               geometry: dict = None,
               wigos_station_identifier: str = None) -> bool:
        """
        Send notification of data to broker

        :param storage_path: path to data on storage
        :param identifier: identifier
        :param geometry: `dict` of GeoJSON geometry object
        :param wigos_station_identifier: WSI associated with the data

        :returns: `bool` of result
        """

        LOGGER.info('Publishing WISNotificationMessage to public broker')
        LOGGER.debug(f'Prepare message for: {storage_path}')

        topic = f'origin/a/wis2/{self.topic_hierarchy.dirpath}'

        wis_message = WISNotificationMessage(identifier, topic, storage_path,
                                             geometry,
                                             wigos_station_identifier)

        # load plugin for public broker
        defs = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': BROKER_PUBLIC,
            'client_type': 'publisher'
        }
        broker = load_plugin('pubsub', defs)

        # publish using filename as identifier
        broker.pub(topic, wis_message.dumps())
        LOGGER.info(f'WISNotificationMessage published for {identifier}')

        # publish message for internal monitoring
        notify_msg = {
            'topic': topic,
            'wigos_station_identifier': wigos_station_identifier
        }
        self.local_broker.pub('wis2box/notifications', json.dumps(notify_msg))

        LOGGER.debug('Pushing message to API')
        upsert_collection_item('messages', wis_message.message)

        return True

    def publish(self) -> bool:
        """
        Publish data

        :returns: `bool` of result
        """
        LOGGER.info('Publishing output data')

        for identifier, item in self.output_data.items():
            # get relative filepath
            rfp = item['_meta']['relative_filepath']

            # now iterate over formats
            for format_, the_data in item.items():
                if format_ == '_meta':
                    continue

                LOGGER.debug(f'Processing format: {format_}')
                # check that we actually have data
                if the_data is None:
                    msg = f'Empty data for {identifier}-{format_}; not publishing'  # noqa
                    LOGGER.warning(msg)
                    continue

                LOGGER.debug('Publishing data')
                data_bytes = self.as_bytes(the_data)
                storage_path = f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}/{rfp}/{identifier}.{format_}'  # noqa

                LOGGER.info(f'Writing data to {storage_path}')
                put_data(data_bytes, storage_path)

                if self.enable_notification:
                    LOGGER.debug('Sending notification to broker')
                    self.notify(identifier, storage_path,
                                item['_meta'].get('geometry'),
                                item['_meta'].get('wigos_station_identifier'))
                else:
                    LOGGER.debug('No notification sent')

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

                yield f'{STORAGE_PUBLIC}/{rfp}/{identifier}.{format_}'

    @property
    def directories(self):
        """Dataset directories"""

        dirpath = self.topic_hierarchy.dirpath

        return {
            'incoming': f'{STORAGE_INCOMING}/{dirpath}',
            'public': f'{STORAGE_PUBLIC}/{dirpath}'
        }

    def get_public_filepath(self):
        """Public filepath"""

        raise NotImplementedError()

    @staticmethod
    def as_bytes(input_data):
        """Get data as bytes"""
        LOGGER.debug(f'input data is type: {type(input_data)}')
        if isinstance(input_data, bytes):
            return input_data
        elif isinstance(input_data, str):
            return str(input_data).encode()
        elif isinstance(input_data, Path):
            with input_data.open('rb') as fh:
                return fh.read()
        else:
            LOGGER.warning('Invalid data type')
            return None

    def __repr__(self):
        return '<BaseAbstractData>'
