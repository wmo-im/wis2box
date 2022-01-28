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
from wis2node.handler import Handler
from wis2node.topic_hierarchy import validate_and_load
from wis2node.util import json_serial

LOGGER = logging.getLogger(__name__)


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
    """data functions"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def info(ctx, topic_hierarchy, verbosity):
    """Display data properties"""

    result = show_info(topic_hierarchy)
    click.echo(json.dumps(result, default=json_serial, indent=4))


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, topic_hierarchy, verbosity):
    """Setup data directories"""

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

    if path.is_dir():
        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'
        files_to_process = [f for f in path.glob(pattern) if f.is_file()]
    else:
        files_to_process = [path]

    for file_to_process in files_to_process:
        click.echo(f'Processing {file_to_process}')
        handler = Handler(file_to_process, topic_hierarchy)
        _ = handler.handle()
    click.echo("Done")


data.add_command(info)
data.add_command(ingest)
data.add_command(setup)
