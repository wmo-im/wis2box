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


class BaseConfig:
    """Abstract API config"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
        """

    def add_collection(self, name: str, collection: dict) -> bool:
        """
        Add a collection

        :param name: `str` of collection name
        :param collection: `dict` of collection properties

        :returns: `bool` of add result
        """

        raise NotImplementedError()

    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection

        :param name: name of collection

        :returns: `bool` of delete collection result
        """

        raise NotImplementedError()

    def has_collection(self, name: str) -> bool:
        """
        Checks a collection

        :param name: name of collection

        :returns: `bool` of collection result
        """

        raise NotImplementedError()

    def prepare_collection(self, meta: dict) -> bool:
        """
        Add a collection

        :param meta: `dict` of collection properties

        :returns: `dict` of collection configuration
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseConfig>'
