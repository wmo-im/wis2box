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
import os
from pathlib import Path

from wis2node import cli_helpers

LOGGER = logging.getLogger(__name__)

PROCESSING_PLUGINS = {}

try:
    DATADIR = Path(os.environ.get('WIS2NODE_DATADIR', None))
    DATADIR_INCOMING = Path(os.environ.get('WIS2NODE_DATADIR_INCOMING', None))
    DATADIR_OUTGOING = Path(os.environ.get('WIS2NODE_DATADIR_OUTGOING', None))
    DATADIR_PUBLIC = Path(os.environ.get('WIS2NODE_DATADIR_PUBLIC', None))
except TypeError:
    msg = 'Configuration filepaths do not exist!'
    LOGGER.error(msg)
    raise EnvironmentError(msg)

CATALOGUE_BACKEND = os.environ.get('WIS2NODE_CATALOGUE_BACKEND', None)
OSCAR_API_TOKEN = os.environ.get('WIS2NODE_OSCAR_API_TOKEN', None)
OGC_API_URL = os.environ.get('WIS2NODE_OGC_API_URL', None)

if None in [
    DATADIR,
    DATADIR_INCOMING,
    DATADIR_OUTGOING,
    DATADIR_PUBLIC,
    CATALOGUE_BACKEND,
    OSCAR_API_TOKEN,
    OGC_API_URL
]:
    msg = 'Environment variables not set!'
    LOGGER.error(msg)
    raise EnvironmentError(msg)


LOGGER.debug('Loading processing plugins')

for key, value in os.environ.items():
    if key.startswith('WIS2NODE_PROCESSING_PLUGIN'):
        PROCESSING_PLUGINS[key] = value


@click.group()
def environment():
    """Environment management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def create(ctx, verbosity):
    """Creates baseline data/metadata directory structure"""

    click.echo(f'Creating baseline directory structure in {DATADIR}')
    DATADIR.mkdir(parents=True, exist_ok=True)
    DATADIR_INCOMING.mkdir(parents=True, exist_ok=True)
    DATADIR_OUTGOING.mkdir(parents=True, exist_ok=True)
    DATADIR_PUBLIC.mkdir(parents=True, exist_ok=True)
    (DATADIR / 'cache').mkdir(parents=True, exist_ok=True)
    (DATADIR / 'config').mkdir(parents=True, exist_ok=True)
    (DATADIR / 'metadata' / 'discovery').mkdir(parents=True, exist_ok=True)
    (DATADIR / 'metadata' / 'station').mkdir(parents=True, exist_ok=True)


environment.add_command(create)
