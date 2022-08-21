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

from wis2box.api.backend import load_backend
from wis2box.api.config import load_config

LOGGER = logging.getLogger(__name__)


def setup_collection(collection: str, meta: dict = {}) -> bool:
    """
    Add collection to api backend and mcf or collection configuration

    :param collection: `str` of collection name
    :param meta: `dict` of collection metadata


    :returns: `bool` of API collection metadata
    """
    if meta == {}:
        LOGGER.error(f'Invalid configuration for: {collection}')
        return False

    backend = load_backend()
    if backend.has_collection(collection) is False:
        backend.add_collection(collection)

    api_config = load_config()
    if api_config.has_collection(collection) is False:
        collection = api_config.prepare_collection(meta)
        api_config.add_collection(collection, collection)

    return True


def remove_collection(collection: str) -> bool:
    """
    Add collection to api backend and mcf or collection configuration

    :param name: `str` of collection name

    :returns: `bool` of API collection metadata
    """

    backend = load_backend()
    if backend.has_collection(collection) is True:
        backend.delete_collection(collection)

    api_config = load_config()
    if api_config.has_collection(collection) is True:
        api_config.delete_add_collection(collection)

    return True


def upsert_collection_item(collection: str, item: dict) -> str:
    """
    Add or update a collection item

    :param collection: name of collection
    :param item: `dict` of GeoJSON item data

    :returns: `str` identifier of added item
    """
    backend = load_backend()
    backend.upsert_collection_items(collection, [item])

    return True


def delete_collection_item(collection: str, item_id: str) -> str:
    """
    Delete an item from a collection

    :param collection: name of collection
    :param item_id: `str` of item identifier

    :returns: `str` identifier of added item
    """
    backend = load_backend()
    backend.delete_collection_item(collection, item_id)


def delete_collections_by_retention(days: int) -> None:
    """
    Delete collections by retention date

    :param days: `int` of number of days

    :returns: `None`
    """
    backend = load_backend()
    backend.delete_collections_by_retention(days)
