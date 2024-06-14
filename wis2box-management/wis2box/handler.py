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

from wis2box.api import upsert_collection_item
from wis2box.storage import get_data
from wis2box.data_mappings import validate_and_load

from wis2box.plugin import load_plugin
from wis2box.plugin import PLUGINS

from wis2box.env import (DOCKER_BROKER, STORAGE_PUBLIC)

LOGGER = logging.getLogger(__name__)


class Handler:
    def __init__(self, filepath: str,
                 data_mappings: dict = None,
                 gts_mappings: dict = None) -> None:
        self.filepath = filepath
        self.plugins = ()
        self.input_bytes = None

        LOGGER.debug('Detecting file type')
        if isinstance(self.filepath, Path):
            LOGGER.debug('filepath is a Path object')
            self.filetype = self.filepath.suffix[1:]
            self.filepath = self.filepath.as_posix()
        else:
            LOGGER.debug('filepath is a string')
            self.filetype = self.filepath.split('.')[-1]

        # check if filepath is a url
        if self.filepath.startswith('http'):
            self.input_bytes = get_data(self.filepath)

        if '/metadata/' in self.filepath:
            msg = 'Passing on handling metadata in workflow'
            raise NotHandledError(msg)
        try:
            self.metadata_id, self.plugins = validate_and_load(
                self.filepath, data_mappings, gts_mappings, self.filetype)
        except Exception as err:
            msg = f'Path validation error: {err}'
            # errors in public storage are not handled
            if STORAGE_PUBLIC in self.filepath:
                raise NotHandledError(msg)
            else:
                raise ValueError(msg)

    def publish_failure_message(self, description, plugin=None):
        message = {
            'filepath': self.filepath,
            'description': description
        }
        if plugin is not None:
            cl = plugin.__class__
            message['plugin'] = f'{cl.__module__ }.{cl.__name__}'
        # handler uses local broker to publish success/failure messages
        defs = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': DOCKER_BROKER, # noqa
            'client_type': 'handler-publisher'
        }
        local_broker = load_plugin('pubsub', defs)
        success = local_broker.pub('wis2box/handler', json.dumps(message), qos=0) # noqa
        if not success:
            msg = f'Failed to publish message: {message}'
            LOGGER.error(msg)

    def handle(self) -> bool:
        for plugin in self.plugins:
            if not plugin.accept_file(self.filepath):
                msg = f'Filepath not accepted: {self.filepath} for class {plugin.__class__}' # noqa
                LOGGER.debug(msg)
                continue
            try:
                if self.input_bytes:
                    plugin.transform(
                        input_data=self.input_bytes,
                        filename=self.filepath.split('/')[-1]
                    )
                else:
                    plugin.transform(self.filepath)
            except Exception as err:
                msg = f'Failed to transform file {self.filepath} : {err}'
                LOGGER.error(msg, exc_info=True)
                self.publish_failure_message(
                    description='Failed to transform file',
                    plugin=plugin)
                return False
            try:
                plugin.publish()
            except Exception as err:
                msg = f'Failed to publish file {self.filepath}: {err}'
                LOGGER.error(msg, exc_info=True)
                self.publish_failure_message(
                    description='Failed to publish file to api-backend',
                    plugin=plugin)
                return False

        return True

    def publish(self) -> bool:
        index_name = self.metadata_id
        if self.input_bytes:
            geojson = json.load(self.input_bytes)
            upsert_collection_item(index_name, geojson)
        else:
            with Path(self.filepath).open() as fh1:
                geojson = json.load(fh1)
                upsert_collection_item(index_name, geojson)

        return True


class NotHandledError(Exception):
    pass
