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

from fnmatch import fnmatch
import logging

from wis2node.env import DATADIR_DATA_MAPPINGS
from wis2node.plugin import load_plugin
from wis2node.topic_hierarchy import TopicHierarchy

LOGGER = logging.getLogger(__name__)


class Handler:
    def __init__(self, filepath: str, dotpath: str = None):
        self.filepath = filepath
        self.dotpath = dotpath
        self.plugin = None

        if self.dotpath is not None:
            LOGGER.debug('Topic hierarchy override')
            if self.dotpath not in DATADIR_DATA_MAPPINGS['data'].keys():
                msg = 'No handler found'
                LOGGER.error(msg)
                raise ValueError(msg)
            else:
                defs = {
                    'topic_hierarchy': self.dotpath,
                    'codepath': DATADIR_DATA_MAPPINGS['data'][self.dotpath]
                }
                self.plugin = load_plugin('data', defs)
            return

        LOGGER.debug('Searching filename against data mappings')
        th = TopicHierarchy(self.dotpath)
        for key, value in DATADIR_DATA_MAPPINGS['data'].items():
            pattern = f'*{th.dirpath}*'
            LOGGER.debug(f'filepath: {self.filepath}\npattern: {pattern}')
            if fnmatch(self.filepath, pattern):
                LOGGER.debug(f'Matched {self.filepath} to {pattern}')
                self.plugin = load_plugin('data', key, value)
                break
            else:
                msg = 'No handler found'
                LOGGER.error(msg)
                raise ValueError(msg)

    def handle(self) -> bool:
        self.plugin.transform(self.filepath)
        self.plugin.publish()
        return True
