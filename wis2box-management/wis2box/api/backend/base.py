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


class BaseBackend:
    """Abstract API backend"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
                     (url, host, port, username, password)
        """

        self.url = defs.get('url')
        self.host = defs.get('host')
        self.port = defs.get('port')
        self.username = defs.get('username')
        self.password = defs.get('password')

    def add_collection(self, name: str) -> bool:
        """
        Add a collection

        :param name: name of collection

        :returns: `bool` of result
        """

        raise NotImplementedError()

    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection

        :param name: name of collection

        :returns: `bool` of delete result
        """

        raise NotImplementedError()

    def has_collection(self, name: str) -> bool:
        """
        Checks a collection

        :param name: name of collection

        :returns: `bool` of collection result
        """

        raise NotImplementedError()

    def upsert_collection_item(self, collection: str, item: dict) -> str:
        """
        Add or update a collection item

        :param collection: name of collection
        :param item: `dict` of GeoJSON item data

        :returns: `str` identifier of added item
        """

        raise NotImplementedError()

    def delete_collection_item(self, collection: str, item_id: str) -> str:
        """
        Delete an item from a collection

        :param collection: name of collection
        :param item_id: `str` of item identifier

        :returns: `str` identifier of added item
        """

        raise NotImplementedError()

    def delete_collections_by_retention(self, days: int) -> None:
        """
        Delete collections by retention date

        :param days: `int` of number of days

        :returns: `None`
        """

        raise NotImplementedError()

    def __repr__(self):
        return f'<BaseBackend> (url={self.url})'
