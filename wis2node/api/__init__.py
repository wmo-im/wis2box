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
from typing import Any, Tuple

import click

from wis2node import cli_helpers
from wis2node.env import (
    DATADIR_DATA_MAPPINGS, DATADIR_PUBLIC, API_CONFIG, API_BACKEND_HOST,
    API_BACKEND_PORT, API_BACKEND_USERNAME, API_BACKEND_PASSWORD
)
from wis2node.plugin import load_plugin
from wis2node.topic_hierarchy import TopicHierarchy
from wis2node.metadata.discovery import DiscoveryMetadata
from wis2node.util import walk_path, yaml_load, yaml_write

LOGGER = logging.getLogger(__name__)


def load_backend(topic_hierarchy: str,
                 fuzzy: bool = False) -> Tuple[TopicHierarchy, Any]:
    """
    Validate topic hierarchy and load data defs

    :param topic_hierarchy: `str` of topic hierarchy path
    :param fuzzy: `bool` of whether to do fuzzy matching of topic hierarchy
                  (e.g. "*foo.bar.baz*).
                  Defaults to `False` (i.e. "foo.bar.baz")

    :returns: tuple of `wis2node.topic_hierarchy.TopicHierarchy and
              plugin object
    """

    LOGGER.debug(f'Validating topic hierarchy: {topic_hierarchy}')

    th = TopicHierarchy(topic_hierarchy)

    if not th.is_valid():
        msg = 'Invalid topic hierarchy'
        LOGGER.error(msg)
        raise ValueError(msg)
    if th.dotpath not in DATADIR_DATA_MAPPINGS['api_backend'].keys():
        msg = 'Topic hierarchy not in data mappings'
        LOGGER.error(msg)
        raise ValueError(msg)

    LOGGER.debug('Loading plugin')

    defs = {
        'topic_hierarchy': topic_hierarchy,
        'codepath': DATADIR_DATA_MAPPINGS['api_backend'][th.dotpath],
        'host': API_BACKEND_HOST,
        'port': API_BACKEND_PORT,
        'username': API_BACKEND_USERNAME,
        'password': API_BACKEND_PASSWORD
    }

    plugin = load_plugin('api_backend', defs)

    return th, plugin


def generate_collection_metadata(mcf: dict) -> dict:
    """
    Generate metadata for collection from metadata control file

    :param mcf: `dict` of MCF file

    :returns: `dict` of API collection metadata
    """

    LOGGER.debug('Parsing discovery metadata')

    dm = DiscoveryMetadata()
    record = dm.parse_record(mcf)
    generated = dm.generate(record)
    parsed = json.loads(generated)

    LOGGER.debug('Creating collection configuration')

    return {
        'type': 'collection',
        'title': parsed['properties']['title'],
        'description': parsed['properties']['description'],
        'keywords': record['identification']['keywords'],
        'extents': parsed['properties']['extent'],
        'links': parsed['links'] + parsed['associations'],
        'providers': []
    }


def load_collection_items(topic_hierarchy: str) -> None:
    """
    Load collection items into collection

    :param topic_hierarchy: `str` of topic hierarchy path

    :returns: None
    """

    th, backend = load_backend(topic_hierarchy)

    regex = f'.*{th.dirpath}.*.geojson$'

    LOGGER.debug('Loading files matching: {}'.format(regex))

    for file in walk_path(DATADIR_PUBLIC, regex):

        with open(file) as fh:
            geojson = json.load(fh)
            backend.upsert_collection_items(th.collection_name, [geojson, ])


@click.group()
def api():
    """api management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def add_collections_items(ctx, topic_hierarchy, verbosity):
    """Add collection items to api backend"""

    click.echo(f'Adding geojson files for collection: {topic_hierarchy}')

    load_collection_items(topic_hierarchy)

    click.echo('Done')


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def add_collection(ctx, filepath, topic_hierarchy, verbosity):
    """Add collection index to api backend"""

    th, backend = load_backend(topic_hierarchy)
    click.echo('Generating collection metadata')
    collection = generate_collection_metadata(filepath.read())

    click.echo(f'Adding collection: {topic_hierarchy}')
    provider_def = backend.add_collection(th.collection_name)
    collection['providers'].append(provider_def)

    click.echo('Adding to pygeoapi configuration')
    with open(API_CONFIG) as fh:
        config = yaml_load(fh)

    config['resources'][th.collection_name] = collection

    with open(API_CONFIG, "w") as fh:
        yaml_write(fh, config)

    click.echo("Done")


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def delete_collection(ctx, topic_hierarchy, verbosity):
    """Delete collection from api backend"""

    click.echo(f'Deleting collection: {topic_hierarchy}')

    th, backend = load_backend(topic_hierarchy)

    backend.delete_collection(th.collection_name)

    click.echo('Removing from API configuration')
    with open(API_CONFIG) as fh:
        config = yaml_load(fh)

    config['resources'].pop(th.collection_name)

    with open(API_CONFIG) as fh:
        yaml_write(fh, config)

    click.echo('Done')


api.add_command(add_collections_items)
api.add_command(add_collection)
api.add_command(delete_collection)
