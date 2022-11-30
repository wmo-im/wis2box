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
from wis2box.topic_hierarchy import validate_and_load

from wis2box.plugin import load_plugin
from wis2box.plugin import PLUGINS

from wis2box.env import (BROKER_HOST, BROKER_USERNAME,
                         BROKER_PASSWORD, BROKER_PORT)

LOGGER = logging.getLogger(__name__)


class Handler:
    def __init__(self, filepath: str, topic_hierarchy: str = None):
        self.filepath = filepath
        self.plugins = ()

        LOGGER.debug('Detecting file type')
        if isinstance(self.filepath, Path):
            LOGGER.debug('filepath is a Path object')
            self.filetype = self.filepath.suffix[1:]
            self.filepath = self.filepath.as_posix()
        else:
            LOGGER.debug('filepath is a string')
            self.filetype = self.filepath.split(".")[-1]

        self.is_http = self.filepath.startswith('http')

        if topic_hierarchy is not None:
            th = topic_hierarchy
            fuzzy = False
        else:
            th = self.filepath
            fuzzy = True

        try:
            self.topic_hierarchy, self.plugins = validate_and_load(
                th, self.filetype, fuzzy=fuzzy)
        except Exception as err:
            msg = f'Topic Hierarchy validation error: {err}'
            LOGGER.error(msg)
            self.publish_failure_message(
                description='Topic hierarchy validation'
            )
            raise ValueError(msg)

    def publish_failure_message(self, description, plugin=None):
        message = {
            'filepath': self.filepath,
            'description': description
        }
        if plugin is not None:
            cl = plugin.__class__
            message['plugin'] = f"{cl.__module__ }.{cl.__name__}"
        # handler uses local broker to publish success/failure messages
        defs = {
            'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
            'url': f"mqtt://{BROKER_USERNAME}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}", # noqa
            'client_type': 'handler-publisher'
        }
        local_broker = load_plugin('pubsub', defs)
        local_broker.pub('wis2box/failure', json.dumps(message))

    def handle(self) -> bool:
        for plugin in self.plugins:
            if not plugin.accept_file(self.filepath):
                msg = f'Filepath not accepted: {self.filepath}'
                LOGGER.warning(msg)
                self.publish_failure_message(
                    description="filepath not accepted",
                    plugin=plugin)
                continue
            try:
                if self.is_http:
                    plugin.transform(
                        get_data(self.filepath),
                        filename=self.filepath.split('/')[-1],
                    )
                else:
                    plugin.transform(self.filepath)
            except Exception as err:
                msg = f'Failed to transform file {self.filepath} : {err}'
                LOGGER.warning(msg)
                self.publish_failure_message(
                    description="failed to transform file",
                    plugin=plugin)
                return False
            try:
                plugin.publish()
            except Exception as err:
                msg = f'Failed to publish file {self.filepath}: {err}'
                LOGGER.warning(msg)
                self.publish_failure_message(
                    decription="Failed to publish file to api-backend",
                    plugin=plugin)
                return False

        return True

    def publish(self) -> bool:
        index_name = self.topic_hierarchy.dotpath
        if self.is_http:
            geojson = json.load(get_data(self.filepath))
            upsert_collection_item(index_name, geojson)
        else:
            with Path(self.filepath).open() as fh1:
                geojson = json.load(fh1)
                upsert_collection_item(index_name, geojson)

        return True
