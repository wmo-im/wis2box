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

import click

from wis2node import cli_helpers
from wis2node.env import API_CONFIG
from wis2node.handler import Handler
from wis2node.api.backend import load_backend
import wis2node.metadata.discovery as discovery
from wis2node.topic_hierarchy import validate_and_load
from wis2node.util import walk_path, yaml_load, yaml_dump

LOGGER = logging.getLogger(__name__)


def generate_collection_metadata(mcf: dict) -> dict:
    """
    Generate collection metadata from metadata control file

    :param mcf: `dict` of MCF file

    :returns: `dict` of API collection metadata
    """

    LOGGER.debug('Parsing discovery metadata')

    dm = discovery.DiscoveryMetadata()
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
        'links': parsed['associations'],
        'providers': []
    }


@click.group()
def api():
    """API management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_PATH
@click.option('--recursive', '-r', is_flag=True, default=False,
              help='Process directory recursively')
@cli_helpers.OPTION_VERBOSITY
def add_collection_items(ctx, topic_hierarchy, path, recursive, verbosity):
    """Add collection items to API backend"""

    click.echo('Loading Backend')
    backend = load_backend()

    click.echo(f'Adding GeoJSON files to collection: {topic_hierarchy}')
    for file_to_process in walk_path(path, '.*.geojson$', recursive):

        click.echo(f'Adding {file_to_process}')

        handler = Handler(file_to_process, topic_hierarchy)
        handler.publish(backend)

    click.echo('Done')


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def add_collection(ctx, filepath, topic_hierarchy, verbosity):
    """Add collection index to API backend"""

    th, _ = validate_and_load(topic_hierarchy)
    index_name = th.dotpath

    click.echo('Generating collection metadata')
    collection = generate_collection_metadata(filepath.read())

    click.echo(f'Adding collection: {topic_hierarchy}')
    backend = load_backend()
    provider_def = backend.add_collection(index_name)
    collection['providers'].append(provider_def)

    click.echo('Adding to pygeoapi configuration')
    with API_CONFIG.open() as fh:
        config = yaml_load(fh)

    config['resources'][index_name] = collection

    with API_CONFIG.open("w") as fh:
        yaml_dump(fh, config)

    click.echo("Done")


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def delete_collection(ctx, topic_hierarchy, verbosity):
    """Delete collection from api backend"""

    click.echo(f'Deleting collection: {topic_hierarchy}')

    th, _ = validate_and_load(topic_hierarchy)
    index_name = th.dotpath

    backend = load_backend()
    backend.delete_collection(index_name)

    click.echo('Removing from API configuration')
    with API_CONFIG.open() as fh:
        config = yaml_load(fh)

    config['resources'].pop(index_name)

    with API_CONFIG.open() as fh:
        yaml_dump(fh, config)

    click.echo('Done')


api.add_command(add_collection_items)
api.add_command(add_collection)
api.add_command(delete_collection)
