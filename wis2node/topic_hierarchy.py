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

LOGGER = logging.getLogger(__name__)


class TopicHierarchy:
    def __init__(self, path: str) -> None:
        self.dotpath = None
        self.dirpath = None

        if '/' in path:
            LOGGER.debug('Transforming from directory to dotted path')
            self.dirpath = path
            self.dotpath = path.replace('/', '.')
        elif '.' in path:
            LOGGER.debug('Transforming from dotted to directory path')
            self.dotpath = path
            self.dirpath = path.replace('.', '/')

    def is_valid(self) -> bool:
        """
        Determines whether a topic hierarchy is valid

        :returns: `bool` of whether the topic hierarchy is validjo
        """

        # TODO: implement when WCMP 2.0 codelists are implemented
        return True
