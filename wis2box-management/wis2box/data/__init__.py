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

from datetime import datetime, timedelta, timezone
import logging
from typing import Union

import click

from wis2box import cli_helpers
from wis2box.api import (setup_collection, remove_collection,
                         delete_collections_by_retention,
                         reindex_collection)
from wis2box.data_mappings import get_data_mappings
from wis2box.env import (STORAGE_SOURCE, STORAGE_ARCHIVE, STORAGE_PUBLIC,
                         STORAGE_DATA_RETENTION_DAYS, STORAGE_INCOMING)
from wis2box.handler import Handler
from wis2box.metadata.discovery import DiscoveryMetadata
from wis2box.storage import put_data, move_data, list_content, delete_data
from wis2box.util import older_than, walk_path

LOGGER = logging.getLogger(__name__)


def archive_data(source_path: str, archive_path: str) -> None:
    """
    Archive data based on today's date (YYYY-MM-DD)

    :param source_path: `str` of base storage-path for source
    :param arcive_path: `str` of base storage-path for archive

    :returns: `None`
    """

    today_dir = f"{archive_path}/{datetime.now().date().strftime('%Y-%m-%d')}"
    LOGGER.debug(f'Archive directory={today_dir}')
    datetime_now = datetime.now(timezone.utc)
    LOGGER.debug(f'datetime_now={datetime_now}')
    for obj in list_content(source_path):
        storage_path = obj['fullpath']
        archive_path = f"{today_dir}/{obj['filename']}"
        LOGGER.debug(f"filename={obj['filename']}")
        LOGGER.debug(f"last_modified={obj['last_modified']}")
        if obj['last_modified'] < datetime_now - timedelta(hours=1):
            LOGGER.debug(f'Moving {storage_path} to {archive_path}')
            move_data(storage_path, archive_path)
        else:
            LOGGER.debug(f"{storage_path} created less than 1 h ago, skip")


def clean_data(source_path: str, days: int) -> None:
    """
    Remove data older than n days from source_path and API indexes')

    :param source_path: `str` of base storage-path to be cleaned
    :param days: Number of days of data to keep

    :returns: `None`
    """

    LOGGER.debug(f'Clean files in {source_path} older than {days} day(s)')
    for obj in list_content(source_path):
        if obj['basedir'] == 'metadata':
            LOGGER.debug('Skipping metadata')
            continue
        storage_path = obj['fullpath']
        if older_than(obj['basedir'], days):
            LOGGER.debug(f"{obj['basedir']} is older than {days} days")
            LOGGER.debug(f'Deleting {storage_path}')
            delete_data(storage_path)
        else:
            LOGGER.debug(f"{obj['basedir']} less than {days} days old")

    LOGGER.debug('Cleaning API indexes')
    delete_collections_by_retention(days)


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
        'title': f'bufr2geojson output ({generated["id"]})',
        'description': f'Output published by bufr2geojson for dataset with id={generated["id"]}', # noqa
        'keywords': generated['properties']['keywords'],
        'bbox': bbox,
        'links': generated['links'],
        'id_field': 'id',
        'time_field': 'observationTime',
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
@cli_helpers.OPTION_VERBOSITY
def archive(ctx, verbosity):
    """Move data from incoming storage to archive storage"""

    source_path = f'{STORAGE_SOURCE}/{STORAGE_INCOMING}'
    archive_path = f'{STORAGE_SOURCE}/{STORAGE_ARCHIVE}'

    click.echo(f'Archiving data from {source_path} to {archive_path}')
    archive_data(source_path, archive_path)


@click.command()
@click.pass_context
@click.option('--days', '-d', help='Number of days of data to keep', type=int)
@cli_helpers.OPTION_VERBOSITY
def clean(ctx, days, verbosity):
    """Clean data directories and API indexes"""

    if days is not None:
        days_ = days
    else:
        days_ = STORAGE_DATA_RETENTION_DAYS

    if days_ is None or days_ < 0:
        click.echo('No data retention set. Skipping')
    else:
        storage_path = f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}'
        click.echo(f'Deleting data > {days_} day(s) old from {storage_path}')
        clean_data(storage_path, days_)


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


data.add_command(archive)
data.add_command(clean)
data.add_command(ingest)
data.add_command(add_collection)
data.add_command(delete_collection)
data.add_command(add_collection_items)
data.add_command(reindex_collection_items)
