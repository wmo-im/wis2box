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
import multiprocessing as mp

from time import sleep

import click

from wis2box import cli_helpers
import wis2box.data as data_

from wis2box.api import (setup_collection, upsert_collection_item,
                         delete_collection_item, remove_collection)

from wis2box.data_mappings import get_data_mappings
from wis2box.data.message import MessageData

from wis2box.env import (DATADIR, DOCKER_BROKER,
                         STORAGE_SOURCE, STORAGE_ARCHIVE,
                         STORAGE_INCOMING)
from wis2box.handler import Handler, NotHandledError
import wis2box.metadata.discovery as discovery_metadata
from wis2box.plugin import load_plugin, PLUGINS
from wis2box.pubsub.message import gcm
from wis2box.storage import put_data

LOGGER = logging.getLogger(__name__)


def get_gts_mappings():
    # read gts mappings from CSV file in DATADIR
    gts_mappings = {}
    mapping_file = 'gts_headers_mapping.csv'
    try:
        with open(f'{DATADIR}/{mapping_file}', 'r') as f:
            for line in f:
                key = line.strip().split(',')[0]
                if key == 'string_in_filepath':
                    continue
                ttaaii = line.strip().split(',')[1]
                cccc = line.strip().split(',')[2]
                value = {'ttaaii': ttaaii, 'cccc': cccc}
                gts_mappings[key] = value
                LOGGER.info(f'GTS mapping: string_in_filepath={key}, {value}')
    except FileNotFoundError:
        LOGGER.warning(f'To add GTS headers, please create {mapping_file} in WIS2BOX_HOST_DATADIR') # noqa
    except Exception as err:
        LOGGER.error(f'Error reading GTS mappings: {err}')
    return gts_mappings


class WIS2BoxSubscriber:

    def __init__(self, broker):
        self.data_mappings = get_data_mappings()
        self.gts_mappings = get_gts_mappings()
        self.broker = broker
        self.broker.bind('on_message', self.on_message_handler)
        self.broker.sub('wis2box/#')

    def handle(self, filepath):
        try:
            LOGGER.info(f'Processing {filepath}')
            # load handler
            handler = Handler(filepath=filepath,
                              data_mappings=self.data_mappings,
                              gts_mappings=self.gts_mappings)
            if handler.handle():
                LOGGER.debug('Data processed')
                for plugin in handler.plugins:
                    for filepath in plugin.files():
                        LOGGER.debug(f'Public filepath: {filepath}')
        except NotHandledError as err:
            msg = f'not handled: {err}'
            LOGGER.info(msg)
        except ValueError as err:
            LOGGER.error(err)
        except Exception as err:
            msg = f'handle() error: {err}'
            raise err

    def handle_publish(self, message, publisher='wis2box'):
        LOGGER.debug('Loading MessageData plugin to publish data from message') # noqa
        topic_hierarchy = message['channel']
        metadata_id = message.get('metadata_id')

        # if metadata_id not provided, log error and return
        if metadata_id is None:
            LOGGER.error('metadata_id not provided in message received on topic wis2box/data/publication') # noqa
        # ensure topic_hierarchy starts with 'origin/a/wis2/'
        if not topic_hierarchy.startswith('origin/a/wis2/'):
            topic_hierarchy = f'origin/a/wis2/{topic_hierarchy}'

        defs = {
            'topic_hierarchy': topic_hierarchy,
            '_meta': message['_meta'],
            'notify': True,
            'metadata_id': metadata_id
        }
        plugin = MessageData(defs=defs)
        try:
            input_bytes = base64.b64decode(message['data'].encode('utf-8'))
            plugin.transform(
                input_data=input_bytes,
                filename=message['filename']
            )
        except Exception as err:
            msg = f'MessageData-transform failed: {err}'
            LOGGER.error(msg, exc_info=True)
            return False
        try:
            plugin.publish()
        except Exception as err:
            msg = f'MessageData-publish failed: {err}'
            LOGGER.error(msg, exc_info=True)
            return False

    def on_message_handler(self, client, userdata, msg):
        LOGGER.debug(f'Raw message: {msg.payload}')

        topic = msg.topic
        message = json.loads(msg.payload)
        LOGGER.info(f'Incoming message on topic {topic}')
        if topic == 'wis2box/notifications':
            LOGGER.info(f'Notification: {message}')
            # store notification in messages collection
            upsert_collection_item('messages', message)
        elif (topic == 'wis2box/storage' and
              message.get('EventName', '') in ['s3:ObjectCreated:Put', 's3:ObjectCreated:CompleteMultipartUpload']): # noqa
            LOGGER.debug('Storing data')
            key = str(message['Key'])
            # if key ends with / then it is a directory
            if key.endswith('/'):
                LOGGER.info(f'Do not process directories: {key}')
                return
            filepath = f'{STORAGE_SOURCE}/{key}'
            if key.startswith(STORAGE_ARCHIVE):
                LOGGER.info(f'Do not process archived-data: {key}')
                return
            # start a new process to handle the received data
            while len(mp.active_children()) == mp.cpu_count():
                sleep(0.05)
            mp.Process(target=self.handle, args=(filepath,)).start()
        elif topic == 'wis2box/cap/publication':
            LOGGER.debug('Publishing data received by cap-editor')
            # get filename and data from message and store in incoming-data
            metadata_id = message.get('metadata_id')
            if metadata_id is None:
                LOGGER.error('metadata_id not found in message')
                return False
            filename = message.get('filename')
            if filename is None:
                LOGGER.error('filename not found in message')
                return False
            data = message.get('data')
            if data is None:
                LOGGER.error('data not found in message')
                return False
            # convert base64 encoded data to bytes
            data_bytes = base64.b64decode(data.encode('utf-8'))
            # store data in incoming-data
            path = f'{STORAGE_INCOMING}/{metadata_id}/{filename}'
            put_data(data_bytes, path)
        elif topic == 'wis2box/data/publication':
            LOGGER.debug('Publishing data')
            self.handle_publish(message)
        elif topic == 'wis2box/data_mappings/refresh':
            LOGGER.info('Refreshing data mappings')
            self.data_mappings = get_data_mappings()
            LOGGER.info(f'Data mappings: {self.data_mappings}')
        elif topic == 'wis2box/dataset/publication':
            LOGGER.debug('Publishing dataset')
            metadata = message
            discovery_metadata.publish_discovery_metadata(metadata)
            data_.add_collection_data(metadata)
            self.data_mappings = get_data_mappings()
        elif topic.startswith('wis2box/dataset/unpublication'):
            LOGGER.debug('Unpublishing dataset')
            identifier = topic.split('/')[-1]
            delete_collection_item('discovery-metadata', identifier)
            if message.get('force', False):
                LOGGER.info('Deleting data')
                remove_collection(identifier)
            self.data_mappings = get_data_mappings()
        else:
            LOGGER.debug('Ignoring message')


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def subscribe(ctx, verbosity):
    """Subscribe to the internal broker and process incoming messages"""
    click.echo('Adding messages collection')
    setup_collection(meta=gcm())

    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': DOCKER_BROKER,  # noqa
        'client_type': 'subscriber'
    }

    broker = load_plugin('pubsub', defs)

    # start the wis2box subscriber
    click.echo('Starting wis2box subscriber')
    WIS2BoxSubscriber(broker=broker)
