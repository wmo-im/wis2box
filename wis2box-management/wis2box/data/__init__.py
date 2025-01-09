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
from datetime import datetime, timedelta, timezone
from typing import Union

import click

from wis2box import cli_helpers
from wis2box.api import (setup_collection, remove_collection,
                         reindex_collection)
from wis2box.data_mappings import get_data_mappings
from wis2box.env import (STORAGE_SOURCE, STORAGE_PUBLIC, STORAGE_INCOMING,
                         STORAGE_DATA_RETENTION_DAYS)
from wis2box.handler import Handler
from wis2box.metadata.discovery import DiscoveryMetadata
from wis2box.storage import put_data, list_content, delete_data
from wis2box.util import walk_path

LOGGER = logging.getLogger(__name__)


def clean_data(source_path: str, days: int) -> None:
    """
    Remove data older than n days from source_path and API indexes')

    :param source_path: `str` of base storage-path to be cleaned
    :param days: Number of days of data to keep

    :returns: `None`
    """

    before = datetime.now(timezone.utc) - timedelta(days=days)
    LOGGER.info(f'Deleting data older than {before} from {source_path}')
    nfiles_deleted = 0
    for obj in list_content(source_path):
        if obj['basedir'] == 'metadata':
            LOGGER.debug('Skipping metadata')
            continue
        # don't delete files in the base-directory
        if obj['basedir'] == '' or obj['basedir'] == obj['filename']:
            continue
        storage_path = obj['fullpath']
        LOGGER.debug(f"filename={obj['filename']}")
        LOGGER.debug(f"last_modified={obj['last_modified']}")
        if obj['last_modified'] < before:
            LOGGER.debug(f"Deleting {storage_path}")
            delete_data(storage_path)
            nfiles_deleted += 1
    LOGGER.info(f'Deleted {nfiles_deleted} files from {source_path}')


def gcm(mcf: Union[dict, str]) -> dict:
    """
    Generate collection metadata from metadata control file

    :param mcf: `dict` of MCF file

    :returns: `dict` of API collection metadata
    """

    LOGGER.debug('Parsing discovery metadata')

    if 'conformsTo' in mcf:
        generated = mcf
    else:
        dm = DiscoveryMetadata()
        record = dm.parse_record(mcf)
        generated = dm.generate(record)

    LOGGER.debug('Creating collection configuration')

    bbox = [
        generated['geometry']['coordinates'][0][0][0],
        generated['geometry']['coordinates'][0][0][1],
        generated['geometry']['coordinates'][0][2][0],
        generated['geometry']['coordinates'][0][2][1]
    ]

    return {
        'id': generated['id'],
        'type': 'feature',
        'topic_hierarchy': generated['properties']['wmo:topicHierarchy'].replace('origin/a/wis2/', '').replace('/', '.'),  # noqa: E501
        'title': f'Observations in json format for {generated["id"]}',
        'description': f'Observations in json format for {generated["id"]}', # noqa
        'keywords': generated['properties']['keywords'],
        'bbox': bbox,
        'links': generated['links'],
        'id_field': 'id',
        'time_field': 'reportTime',
        'title_field': 'id'
    }


def add_collection_data(metadata: str):
    """
    Add collection index to API backend

    :param metadata: `str` of MCF

    :returns: None
    """

    meta = gcm(metadata)
    LOGGER.info(f'Adding data-collection for {meta["id"]}')
    setup_collection(meta=meta)

    return


@click.group()
def data():
    """Data workflow"""
    pass


@click.command()
@click.pass_context
@click.option('--days', '-d', help='Number of days of data to keep', type=int)
@cli_helpers.OPTION_VERBOSITY
def clean(ctx, days, verbosity):
    """Clean data from storage older than X days"""

    if days is not None:
        click.echo(f'Using data retention days: {days}')
        days_ = days
    else:
        click.echo(f'Using default data retention days: {STORAGE_DATA_RETENTION_DAYS}') # noqa
        days_ = STORAGE_DATA_RETENTION_DAYS

    if days_ is None or days_ < 0:
        click.echo('No data retention set. Skipping')
    else:
        storage_path_public = f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}'
        click.echo(f'Deleting data > {days_} day(s) old from {storage_path_public}') # noqa
        clean_data(storage_path_public, days_)
        storage_path_incoming = f'{STORAGE_SOURCE}/{STORAGE_INCOMING}'
        click.echo(f'Deleting data > {days_} day(s) old from {storage_path_incoming}') # noqa
        clean_data(storage_path_incoming, days_)
        click.echo('Done')


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_METADATA_ID
@cli_helpers.OPTION_PATH
@cli_helpers.OPTION_RECURSIVE
@cli_helpers.OPTION_VERBOSITY
def ingest(ctx, topic_hierarchy, metadata_id, path, recursive, verbosity):
    """Ingest data file or directory"""

    # either topic_hierarchy or metadata_id must be provided
    if topic_hierarchy and metadata_id:
        raise click.ClickException('Only one of topic_hierarchy or metadata_id can be provided') # noqa

    if not topic_hierarchy and not metadata_id:
        raise click.ClickException('Please specify a metadata_id using the option --metadata-id') # noqa

    rfp = None
    if metadata_id:
        data_mappings = get_data_mappings()
        if metadata_id not in data_mappings:
            raise click.ClickException(f'metadata_id={metadata_id} not found in data mappings') # noqa
        rfp = metadata_id
    else:
        rfp = topic_hierarchy.replace('.', '/')

    for file_to_process in walk_path(path, '.*', recursive):
        click.echo(f'Processing {file_to_process}')
        path = f'{STORAGE_INCOMING}/{rfp}/{file_to_process.name}'

        with file_to_process.open('rb') as fh:
            data = fh.read()
            put_data(data, path)

    click.echo("Done")


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def add_collection(ctx, filepath, verbosity):
    """Add collection index to API backend"""

    add_collection_data(filepath.read())

    click.echo("Done")


@click.command()
@click.pass_context
@click.argument('collection')
@cli_helpers.OPTION_VERBOSITY
def delete_collection(ctx, collection, verbosity):
    """Delete collection from API backend"""

    click.echo(f'Deleting collection: {collection}')

    remove_collection(collection)

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument('collection_id_source')
@click.argument('collection_id_target')
def reindex_collection_items(ctx, collection_id_source, collection_id_target):
    """Reindex items from one collection to another"""

    reindex_collection(collection_id_source, collection_id_target)

    click.echo('Done')


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_PATH
@cli_helpers.OPTION_RECURSIVE
@cli_helpers.OPTION_VERBOSITY
def add_collection_items(ctx, topic_hierarchy, path, recursive, verbosity):
    """Add collection items to API backend"""

    data_mappings = get_data_mappings()
    click.echo(f'Adding GeoJSON files to collection: {topic_hierarchy}')
    for file_to_process in walk_path(path, '.*.geojson$', recursive):
        click.echo(f'Adding {file_to_process}')
        handler = Handler(filepath=file_to_process,
                          topic_hierarchy=topic_hierarchy,
                          data_mappings=data_mappings)
        handler.publish()

    click.echo('Done')


data.add_command(clean)
data.add_command(ingest)
data.add_command(add_collection)
data.add_command(delete_collection)
data.add_command(add_collection_items)
data.add_command(reindex_collection_items)
