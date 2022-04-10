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
from pathlib import Path
from typing import Any, Tuple, Union

from wis2box.env import DATADIR_DATA_MAPPINGS
from wis2box.plugin import load_plugin

LOGGER = logging.getLogger(__name__)


class TopicHierarchy:
    def __init__(self, path: Union[Path, str]) -> None:
        self.path = str(path)
        self.dotpath = None
        self.dirpath = None

        if '/' in self.path:
            LOGGER.debug('Transforming from directory to dotted path')
            self.dirpath = self.path
            self.dotpath = self.path.replace('/', '.')
        elif '.' in self.path:
            LOGGER.debug('Transforming from dotted to directory path')
            self.dotpath = self.path
            self.dirpath = self.path.replace('.', '/')

    def is_valid(self) -> bool:
        """
        Determines whether a topic hierarchy is valid

        :returns: `bool` of whether the topic hierarchy is validjo
        """

        # TODO: implement when WCMP 2.0 codelists are implemented
        return True


def validate_and_load(topic_hierarchy: str,
                      fuzzy: bool = False) -> Tuple[TopicHierarchy, Any]:
    """
    Validate topic hierarchy and load data defs

    :param topic_hierarchy: `str` of topic hierarchy path
    :param fuzzy: `bool` of whether to do fuzzy matching of topic hierarchy
                  (e.g. "*foo.bar.baz*).
                  Defaults to `False` (i.e. "foo.bar.baz")

    :returns: tuple of `wis2box.topic_hierarchy.TopicHierarchy` and
              plugin object
    """

    LOGGER.debug(f'Validating topic hierarchy: {topic_hierarchy}')

    th = TopicHierarchy(topic_hierarchy)

    if not th.is_valid():
        msg = 'Invalid topic hierarchy'
        LOGGER.error(msg)
        raise ValueError(msg)

    if not fuzzy:
        if th.dotpath not in DATADIR_DATA_MAPPINGS['data']:
            msg = 'Topic hierarchy not in data mappings'
            LOGGER.error(msg)
            raise ValueError(msg)

        LOGGER.debug('Loading plugin')

        defs = {
            'topic_hierarchy': topic_hierarchy,
            'codepath': DATADIR_DATA_MAPPINGS['data'][th.dotpath]['plugin'],
            'template': DATADIR_DATA_MAPPINGS['data'][th.dotpath]['template'],
            'pattern':  DATADIR_DATA_MAPPINGS['data'][th.dotpath]['file-pattern']  # noqa
        }
        plugin = load_plugin('data', defs)

    else:
        LOGGER.debug('Searching filename against data mappings')
        th = TopicHierarchy(topic_hierarchy)
        for key, value in DATADIR_DATA_MAPPINGS['data'].items():
            pattern = f'*{th.dirpath}*'
            LOGGER.debug(f'topic_hierarchy: {topic_hierarchy}')
            LOGGER.debug(f'pattern: {pattern}')
            if fnmatch(topic_hierarchy, pattern):
                LOGGER.debug(f'Matched {topic_hierarchy} to {pattern}')
                defs = {
                    'topic_hierarchy': key,
                    'codepath': value['plugin'],
                    'template': value['template'],
                    'pattern': value['file-pattern']
                }
                plugin = load_plugin('data', defs)
                th = TopicHierarchy(key)
                break
            else:
                msg = 'No handler found'
                LOGGER.error(msg)
                raise ValueError(msg)

    return th, plugin
