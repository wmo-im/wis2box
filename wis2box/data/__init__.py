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

import click

from wis2box import cli_helpers
from wis2box.api.backend import load_backend
from wis2box.env import (STORAGE_SOURCE, STORAGE_ARCHIVE, STORAGE_PUBLIC,
                         STORAGE_DATA_RETENTION_DAYS, STORAGE_INCOMING)
from wis2box.handler import Handler
from wis2box.storage import put_data
from wis2box.util import older_than, walk_path

from wis2box.storage import move_data
from wis2box.storage import list_content
from wis2box.storage import delete_data

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
    for object in list_content(source_path):
        storage_path = object['fullpath']
        archive_path = f"{today_dir}/{object['filename']}"
        LOGGER.debug(f"filename={object['filename']}")
        LOGGER.debug(f"last_modified={object['last_modified']}")
        if object['last_modified'] < datetime_now - timedelta(hours=1):
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
    for object in list_content(source_path):
        storage_path = object['fullpath']
        if older_than(object['basedir'], days):
            LOGGER.debug(f"{object['basedir']} is older than {days} days")
            LOGGER.debug(f'Deleting {storage_path}')
            delete_data(storage_path)
        else:
            LOGGER.debug(f"{object['basedir']} less than {days} days old")

    LOGGER.debug('Cleaning API indexes')
    backend = load_backend()
    backend.delete_collections_by_retention(days)


@click.group()
def data():
    """Data workflow"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def archive(ctx, verbosity):
    """Move data from incoming storage to archive storage """

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
@cli_helpers.OPTION_PATH
@click.option('--recursive', '-r', is_flag=True, default=False,
              help='Process directory recursively')
@cli_helpers.OPTION_VERBOSITY
def ingest(ctx, topic_hierarchy, path, recursive, verbosity):
    """Ingest data file or directory"""

    for file_to_process in walk_path(path, '.*', recursive):
        click.echo(f'Processing {file_to_process}')
        handler = Handler(file_to_process, topic_hierarchy)
        rfp = handler.topic_hierarchy.dirpath
        path = f'{STORAGE_INCOMING}/{rfp}/{file_to_process.name}'

        with file_to_process.open('rb') as fh:
            data = fh.read()
            put_data(data, path)

    click.echo("Done")


data.add_command(archive)
data.add_command(clean)
data.add_command(ingest)
