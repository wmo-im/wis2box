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

import click

from wis2box import cli_helpers
from wis2box.api.backend import load_backend
from wis2box.api.config import load_config
from wis2box.handler import Handler
from wis2box.pubsub.message import generate_collection_metadata as gcm
import wis2box.metadata.discovery as discovery_
from wis2box.topic_hierarchy import validate_and_load
from wis2box.util import walk_path

LOGGER = logging.getLogger(__name__)


def generate_collection_metadata(mcf: dict) -> dict:
    """
    Generate collection metadata from metadata control file

    :param mcf: `dict` of MCF file

    :returns: `dict` of API collection metadata
    """

    LOGGER.debug('Parsing discovery metadata')

    dm = discovery_.DiscoveryMetadata()
    record = dm.parse_record(mcf)
    generated = dm.generate(record)

    LOGGER.debug('Creating collection configuration')

    bbox = [
        generated['geometry']['coordinates'][0][0][0],
        generated['geometry']['coordinates'][0][0][1],
        generated['geometry']['coordinates'][0][2][0],
        generated['geometry']['coordinates'][0][2][1],
    ]

    kw = record['identification']['keywords']

    keywords = set([k for k in kw.values() for k in kw])

    return {
        'id': generated['id'],
        'type': 'collection',
        'title': generated['properties']['title'],
        'description': generated['properties']['description'],
        'keywords': list(keywords),
        'bbox': bbox,
        'links': generated['links'],
        'id_field': 'id',
        'time_field': 'resultTime',
        'title_field': 'id'
    }


@click.group()
def api():
    """API management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, verbosity):
    """Add collection items to API backend"""

    click.echo('Generating collection metadata for messages')
    meta = gcm()

    backend = load_backend()
    backend.add_collection('messages')

    click.echo('Adding to API configuration')
    api_config = load_config()
    collection = api_config.prepare_collection(meta)
    api_config.add_collection('messages', collection)

    click.echo("Done")


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

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    th, _ = validate_and_load(topic_hierarchy)
    name = th.dotpath

    click.echo('Generating collection metadata')
    meta = generate_collection_metadata(filepath.read())

    click.echo(f'Adding collection: {topic_hierarchy}')
    backend = load_backend()
    backend.add_collection(name)

    click.echo('Adding to API configuration')
    api_config = load_config()
    collection = api_config.prepare_collection(meta)
    api_config.add_collection(name, collection)

    click.echo("Done")


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def delete_collection(ctx, topic_hierarchy, verbosity):
    """Delete collection from api backend"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    click.echo(f'Deleting collection: {topic_hierarchy}')

    th, _ = validate_and_load(topic_hierarchy)
    name = th.dotpath

    backend = load_backend()
    backend.delete_collection(name)

    click.echo('Removing from API configuration')
    api_config = load_config()
    api_config.delete_collection(name)

    click.echo('Done')


api.add_command(add_collection_items)
api.add_command(add_collection)
api.add_command(delete_collection)
api.add_command(setup)
