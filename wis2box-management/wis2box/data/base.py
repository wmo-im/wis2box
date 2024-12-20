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
import base64
import json
import logging
from pathlib import Path
import re
from typing import Iterator, Union

from wis2box.env import (STORAGE_PUBLIC,
                         STORAGE_SOURCE, BROKER_PUBLIC,
                         DOCKER_BROKER)
from wis2box.storage import exists, get_data, put_data

from wis2box.plugin import load_plugin, PLUGINS

from wis2box.pubsub.message import WISNotificationMessage

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
        self.incoming_filepath = defs.get('incoming_filepath')
        self.metadata_id = defs.get('metadata_id')
        self.topic_hierarchy = defs.get('topic_hierarchy')
        self.template = defs.get('template')
        self.file_filter = defs.get('pattern', '.*')
        self.enable_notification = defs.get('notify', False)
        self.buckets = defs.get('buckets', ())
        self.output_data = {}
        self.discovery_metadata = {}
        self.gts = None
        gts_ttaaii = defs.get('gts_ttaaii')
        gts_cccc = defs.get('gts_cccc')
        if None not in [gts_ttaaii, gts_cccc]:
            self.gts = {
                'ttaaii': gts_ttaaii,
                'cccc': gts_cccc
            }

#        if discovery_metadata:
#            self.setup_discovery_metadata(discovery_metadata)

    def publish_failure_message(self, description, wsi=None, identifier=None):
        message = {
            'incoming_filepath': self.incoming_filepath,
            'identifier': identifier,
            'description': description
        }
        if wsi is not None:
            message['wigos_station_identifier'] = wsi
        # load plugin for local broker
        defs = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': DOCKER_BROKER, # noqa
            'client_type': 'failure-publisher'
        }
        local_broker = load_plugin('pubsub', defs)
        # publish with qos=0
        success = local_broker.pub('wis2box/failure', json.dumps(message), qos=0) # noqa
        if not success:
            LOGGER.error('Failed to publish failure message on internal broker') # noqa

    def setup_discovery_metadata(self, discovery_metadata: dict) -> None:
        """
        Import discovery metadata

        :param discovery_metadata: `dict` of discovery metadata MCF

        :returns: `None`
        """

        self.discovery_metadata = discovery_metadata
        self.country = discovery_metadata['wis2box']['country']
        self.centre_id = discovery_metadata['wis2box']['centre_id']

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
               datetime_: str,
               geometry: dict = None,
               wigos_station_identifier: str = None,
               is_update: bool = False) -> bool:
        """
        Send notification of data to broker

        :param storage_path: path to data on storage
        :param identifier: identifier
        :param datetime_: `datetime` object of temporal aspect of data
        :param geometry: `dict` of GeoJSON geometry object
        :param wigos_station_identifier: WSI associated with the data

        :returns: `bool` of result
        """

        LOGGER.info('Publishing WISNotificationMessage to public broker')
        LOGGER.debug(f'Prepare message for: {storage_path}')

        topic = self.topic_hierarchy
        metadata_id = self.metadata_id

        operation = 'create' if is_update is False else 'update'

        wis_message = WISNotificationMessage(
            f"{metadata_id.replace('urn:wmo:md:','')}/{identifier}",
            metadata_id, storage_path, datetime_, geometry,
            wigos_station_identifier, self.gts,
            operation)

        # load plugin for public broker
        defs = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': BROKER_PUBLIC,
            'client_type': 'publisher'
        }
        broker = load_plugin('pubsub', defs)

        # publish using filename as identifier
        success = broker.pub(topic, wis_message.dumps())
        if not success:
            LOGGER.error('Failed to publish data notification message on public broker') # noqa
            return False
        else:
            LOGGER.info(f'WISNotificationMessage published for {identifier}')

        # load plugin for local broker
        defs_local = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': DOCKER_BROKER, # noqa
            'client_type': 'notify-publisher'
        }
        local_broker = load_plugin('pubsub', defs_local)
        success = local_broker.pub('wis2box/notifications', wis_message.dumps(), qos=0) # noqa
        if not success:
            LOGGER.error('Failed to publish notification message on internal broker') # noqa
        return True

    def publish(self) -> bool:
        """
        Publish data

        :returns: `bool` of result
        """

        LOGGER.info('Publishing output data')

        for identifier, item in self.output_data.items():
            self.publish_item(identifier, item)
        return True

    def publish_item(self, identifier, item) -> bool:
        """
        Publish item in data

        :param identifier: identifier
        :param item: item to be published

        :returns: `bool` of result
        """
        LOGGER.info('Publishing output data')

        try:
            wsi = item['_meta']['properties']['wigos_station_identifier']  # noqa
        except KeyError:
            wsi = item['_meta'].get('wigos_station_identifier')

        try:
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

                is_update = False
                is_new = True
                # check if storage_path already exists
                if exists(storage_path):
                    # if data exists, check if it is the same
                    if data_bytes == get_data(storage_path):
                        LOGGER.error(f'Data already published for {identifier}-{format_}; not publishing')  # noqa
                        is_new = False
                    else:
                        LOGGER.warning(f'Data already published for {identifier}-{format_}; updating')  # noqa
                        is_update = True
                if is_new:
                    LOGGER.info(f'Writing data to {storage_path}')
                    put_data(data_bytes, storage_path)

                if self.enable_notification and is_new:
                    LOGGER.debug('Sending notification to broker')
                    try:
                        datetime_ = item['_meta']['properties']['datetime']
                    except KeyError:
                        datetime_ = item['_meta'].get('data_date')
                    self.notify(identifier, storage_path,
                                datetime_,
                                item['_meta'].get('geometry'), wsi, is_update)
                else:
                    LOGGER.debug('No notification sent')
        except Exception as err:
            msg = f'Failed to publish item {identifier}: {err}'
            LOGGER.error(msg)
            self.publish_failure_message(
                    description='Failed to publish item',
                    identifier=identifier,
                    wsi=wsi)
        return True

    def validate_filename_pattern(
            self, filename: str) -> Union[re.Match, None]:
        """
        Validate a filename pattern against a configured file_filter

        :filename: `str` of filename

        :returns: `bool` of vadidation result
        """

        LOGGER.debug(f'Validating {filename} against {self.file_filter}')
        return re.match(self.file_filter, filename)

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

    def get_public_filepath(self):
        """Public filepath"""

        raise NotImplementedError()

    @staticmethod
    def as_bytes(input_data):
        """Return input data as bytes

        :param input_data: `str`, `bytes` or `Path` of data

        :returns: `bytes` of data
        """

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

    @staticmethod
    def as_string(input_data, base64_encode=False):
        """Return input data as string

        :param input_data: `str`, `bytes` or `Path` of data
        :param base64_encode: `bool` if to use base64-encode before decoding

        :returns: `str` of data
        """

        LOGGER.debug(f'input data is type: {type(input_data)}')
        if isinstance(input_data, bytes):
            if base64_encode:
                return base64.b64encode(input_data).decode('utf-8')
            else:
                return input_data.decode('utf-8')
        elif isinstance(input_data, str):
            return input_data
        elif isinstance(input_data, Path):
            if base64_encode:
                with input_data.open('rb') as fh:
                    return base64.b64encode(fh.read()).decode('utf-8')
            else:
                with input_data.open('r') as fh:
                    return fh.read()
        else:
            LOGGER.warning('Invalid data type')
            return None

    def __repr__(self):
        return '<BaseAbstractData>'
