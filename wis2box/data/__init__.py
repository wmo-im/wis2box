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

from datetime import datetime
import json
import logging
from pathlib import Path
import shutil

import click

from wis2box import cli_helpers
from wis2box.data.auth import auth
from wis2box.api.backend import load_backend
from wis2box.env import (DATADIR_ARCHIVE, DATADIR_INCOMING, DATADIR_PUBLIC,
                         DATA_RETENTION_DAYS)
from wis2box.handler import Handler
from wis2box.topic_hierarchy import validate_and_load
from wis2box.util import json_serial, older_than, walk_path

LOGGER = logging.getLogger(__name__)


def archive_data(source_directory: Path, target_directory: Path) -> None:
    """
    Move data into archive directory based on today's date (YYYY-MM-DD)

    :param source_directory: `Path` of directory to archive
    :param target_directory: base `Path` of archive directory

    :returns: `None`
    """

    if not target_directory.exists():
        msg = f'Directory {target_directory} does not exist'
        LOGGER.error(msg)
        raise FileNotFoundError(msg)

    today_dir = DATADIR_ARCHIVE / datetime.now().date().strftime('%Y-%m-%d')
    LOGGER.debug(f'Archive directory {today_dir}')

    for file_or_dir in source_directory.glob('*'):
        LOGGER.debug(f'Moving {file_or_dir} to {today_dir}')
        shutil.move(file_or_dir, today_dir / file_or_dir.name)

    return


def clean_data(directory: Path, days: int) -> None:
    """
    Remove data older than n days from public directory and API indexes')

    :param directory: directory `Path`
    :param days: Number of days of data to keep

    :returns: `None`
    """

    LOGGER.debug(f'Cleaning directory {directory}')
    dirs = [d for d in directory.iterdir() if d.is_dir()]

    for dir_ in dirs:
        LOGGER.debug(f'Directory {dir_}')
        if older_than(dir_.name, days):
            LOGGER.debug(f'Directory {dir_} is older than {days} days')
            shutil.rmtree(dir_)

    LOGGER.debug('Cleaning API indexes')
    backend = load_backend()
    backend.delete_collections_by_retention(days)

    return


def setup_dirs(topic_hierarchy: str) -> dict:
    """
    Setup data directories

    :param topic_hierarchy: `str` of topic hierarchy path

    :returns: `dict` of directories created
    """

    _, plugin = validate_and_load(topic_hierarchy)

    LOGGER.debug('Setting up directories')
    plugin.setup_dirs()

    return plugin.directories


def show_info(topic_hierarchy: str) -> dict:
    """
    Display data properties

    :param topic_hierarchy: `str` of topic hierarchy path

    :returns: `None`
    """

    th, plugin = validate_and_load(topic_hierarchy)

    LOGGER.debug('Getting directories')
    return {
        'topic_hierarchy': th.dotpath,
        'directories': plugin.directories
     }


@click.group()
def data():
    """Data workflow"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def archive(ctx, verbosity):
    """Move data from incoming to Archive directory"""

    click.echo(f'Archiving data from {DATADIR_INCOMING} to {DATADIR_ARCHIVE}')
    archive_data(DATADIR_INCOMING, DATADIR_ARCHIVE)


@click.command()
@click.pass_context
@click.option('--days', '-d', help='Number of days of data to keep')
@cli_helpers.OPTION_VERBOSITY
def clean(ctx, days, verbosity):
    """Clean data directories and API indexes"""

    if days is not None:
        days_ = days
    else:
        days_ = DATA_RETENTION_DAYS

    if days_ is None or days_ < 0:
        click.echo('No data retention set. Skipping')
    else:
        click.echo(f'Deleting data older than {days_} day(s)')
        clean_data(DATADIR_PUBLIC, days_)


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def info(ctx, topic_hierarchy, verbosity):
    """Display data properties"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    result = show_info(topic_hierarchy)
    click.echo(json.dumps(result, default=json_serial, indent=4))


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, topic_hierarchy, verbosity):
    """Setup data directories"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    result = setup_dirs(topic_hierarchy)
    click.echo('Directories created:')
    click.echo(json.dumps(result, default=json_serial, indent=4))


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
        _ = handler.handle()
    click.echo("Done")


data.add_command(archive)
data.add_command(auth)
data.add_command(clean)
data.add_command(info)
data.add_command(ingest)
data.add_command(setup)
