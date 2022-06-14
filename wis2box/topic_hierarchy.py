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

        :returns: `bool` of whether the topic hierarchy is valid
        """

        # TODO: implement when WCMP 2.0 codelists are implemented
        return True


def validate_and_load(topic_hierarchy: str, file_type: str = None,
                      fuzzy: bool = False) -> Tuple[TopicHierarchy, Any]:
    """
    Validate topic hierarchy and load plugin

    :param topic_hierarchy: `str` of topic hierarchy path
    :param file_type: `str` the type of file we are processing, e.g. csv, bufr, xml  # noqa
    :param fuzzy: `bool` of whether to do fuzzy matching of topic hierarchy
                  (e.g. "*foo.bar.baz*).
                  Defaults to `False` (i.e. "foo.bar.baz")

    :returns: tuple of `wis2box.topic_hierarchy.TopicHierarchy` and
              plugin object
    """

    LOGGER.debug(f'Validating topic hierarchy: {topic_hierarchy}')
    th = TopicHierarchy(topic_hierarchy)
    data_mappings = DATADIR_DATA_MAPPINGS['data']
    found = False

    if not th.is_valid():
        msg = 'Invalid topic hierarchy'
        LOGGER.error(msg)
        raise ValueError(msg)

    if fuzzy:
        LOGGER.debug('Searching data mappings for fuzzy topic match')
        for topic, defs in data_mappings.items():

            pattern = f'*{topic}*'
            LOGGER.debug(f'Attempting to fuzzy match with {pattern}')
            if fnmatch(th.dotpath, pattern):

                LOGGER.debug(f'Reloading topic to {topic}')
                th = TopicHierarchy(topic)

                LOGGER.debug(f'Matched topic {topic_hierarchy} on {th.dotpath}')
                found = True
                plugins = defs['plugins']


    else:
        LOGGER.debug('Searching data mappings for exact topic match')
        if th.dotpath in data_mappings:

            LOGGER.debug(f'Matched topic {th.path} on {th.dotpath}')
            found = True
            plugins = data_mappings[th.dotpath]['plugins']

    if not found:
        msg = f'No plugins for {th.path} in data mappings'
        LOGGER.error(msg)
        raise ValueError(msg)

    if file_type is None:
        LOGGER.warning('File type missing')
        file_type = next(iter(plugins))
        LOGGER.debug(f'File type set to first type: {file_type}')

    if file_type not in plugins:
        msg = f'Unknown file type ({file_type}) for topic {th.dotpath}'  # noqa
        LOGGER.error(msg)
        raise ValueError(msg)

    LOGGER.debug(f'Adding plugin definition for {file_type}')
    data_defs = {
        'topic_hierarchy': th.dotpath,
        'codepath': plugins[file_type]['plugin'],
        'template': plugins[file_type]['template'],
        'pattern': plugins[file_type]['file-pattern'],
        'format': file_type
    }
    plugin = load_plugin('data', data_defs)
    return th, plugin

