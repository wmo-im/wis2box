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

import click
import logging

from wis2box.api.backend import load_backend
from wis2box.api.config import load_config
from wis2box import cli_helpers

LOGGER = logging.getLogger(__name__)


def setup_collection(meta: dict = {}) -> bool:
    """
    Add collection to api backend and configuration

    :param meta: `dict` of collection metadata

    :returns: `bool` of API collection setup result
    """

    try:
        name = meta['id'].lower()
    except KeyError:
        LOGGER.error(f'Invalid configuration: {meta}')
        return False

    if 'topic_hierarchy' in meta:
        data_name = meta['topic_hierarchy']
    else:
        data_name = meta['id']

    backend = load_backend()
    if not backend.has_collection(data_name):

        if not backend.add_collection(data_name):
            msg = f'Unable to setup backend for collection {data_name}'
            LOGGER.error(msg)
            return False

    api_config = load_config()
    if not api_config.has_collection(name):

        collection = api_config.prepare_collection(meta)
        if not api_config.add_collection(name, collection):
            msg = f'Unable to setup configuration for collection {name}'
            LOGGER.error(msg)
            return False

    return True


def remove_collection(collection_id: str, backend: bool = True,
                      config: bool = True) -> bool:
    """
    Remove collection from api backend and configuration

    :param collection_id: `str` of collection id

    :returns: `bool` of API collection removal result
    """

    api_backend = None
    api_config = None

    collection_data = load_config().get_collection_data(collection_id)

    if config:
        api_config = load_config()
        if api_config.has_collection(collection_id):
            api_config.delete_collection(collection_id)

    if backend:
        api_backend = load_backend()
        if api_backend.has_collection(collection_data):
            api_backend.delete_collection(collection_data)

    if api_backend is not None and api_backend.has_collection(collection_data):
        LOGGER.error(f'Unable to remove collection backend for {collection_id}')
        return False

    if api_config is not None and api_config.has_collection(collection_data):
        LOGGER.error(f'Unable to remove collection for {collection_id}')
        return False

    delete_collection_item('discovery-metadata', collection_id)

    return True


def upsert_collection_item(collection_id: str, item: dict) -> str:
    """
    Add or update a collection item

    :param collection_id: name of collection
    :param item: `dict` of GeoJSON item data

    :returns: `str` identifier of added item
    """
    backend = load_backend()
    backend.upsert_collection_items(collection_id, [item])

    return True


def delete_collection_item(collection_id: str, item_id: str) -> str:
    """
    Delete an item from a collection

    :param collection_id: name of collection
    :param item_id: `str` of item identifier

    :returns: `str` identifier of added item
    """
    backend = load_backend()
    backend.delete_collection_item(collection_id, item_id)


def delete_collections_by_retention(days: int) -> None:
    """
    Delete collections by retention date

    :param days: `int` of number of days

    :returns: `None`
    """
    backend = load_backend()
    backend.delete_collections_by_retention(days)


@click.group()
def api():
    """API management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, verbosity):
    """Add collection items to API backend"""

    api_config = load_config()
    if not api_config.has_collection(''):
        click.echo('API not ready')
    else:
        click.echo('API ready')


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def add_collection(ctx, filepath, verbosity):
    """Delete collection from api backend"""

    if not setup_collection(meta=filepath.read()):
        click.echo('Unable to add collection')
    else:
        click.echo('Collection added')


@click.command()
@click.pass_context
@click.argument('collection')
@cli_helpers.OPTION_VERBOSITY
def delete_collection(ctx, collection, verbosity):
    """Delete collection from api backend"""

    if not remove_collection(collection):
        click.echo('Unable to delete collection')
    else:
        click.echo('Collection deleted')


api.add_command(setup)
api.add_command(add_collection)
api.add_command(delete_collection)
