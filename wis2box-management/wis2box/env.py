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

from wis2box import cli_helpers
from wis2box.log import setup_logger
from wis2box.plugin import load_plugin
from wis2box.plugin import PLUGINS

LOGGER = logging.getLogger(__name__)

try:
    DATADIR = Path(os.environ.get('WIS2BOX_DATADIR'))
    DATADIR_CONFIG = DATADIR / 'config'
except (OSError, TypeError):
    msg = 'Configuration filepaths do not exist!'
    LOGGER.error(msg)
    raise EnvironmentError(msg)

API_TYPE = os.environ.get('WIS2BOX_API_TYPE')
API_URL = os.environ.get('WIS2BOX_API_URL')
API_BACKEND_TYPE = os.environ.get('WIS2BOX_API_BACKEND_TYPE')
API_BACKEND_URL = os.environ.get('WIS2BOX_API_BACKEND_URL').rstrip('/')
DOCKER_API_URL = os.environ.get('WIS2BOX_DOCKER_API_URL')
AUTH_URL = os.environ.get('WIS2BOX_AUTH_URL')
URL = os.environ.get('WIS2BOX_URL')

BROKER_USERNAME = os.environ.get('WIS2BOX_BROKER_USERNAME')
BROKER_PASSWORD = os.environ.get('WIS2BOX_BROKER_PASSWORD')
BROKER_HOST = os.environ.get('WIS2BOX_BROKER_HOST')
BROKER_PORT = os.environ.get('WIS2BOX_BROKER_PORT')
BROKER_PUBLIC = os.environ.get('WIS2BOX_BROKER_PUBLIC')

STORAGE_TYPE = os.environ.get('WIS2BOX_STORAGE_TYPE')
STORAGE_SOURCE = os.environ.get('WIS2BOX_STORAGE_SOURCE')
STORAGE_USERNAME = os.environ.get('WIS2BOX_STORAGE_USERNAME')
STORAGE_PASSWORD = os.environ.get('WIS2BOX_STORAGE_PASSWORD')
STORAGE_INCOMING = os.environ.get('WIS2BOX_STORAGE_INCOMING')
STORAGE_ARCHIVE = os.environ.get('WIS2BOX_STORAGE_ARCHIVE')
STORAGE_PUBLIC = os.environ.get('WIS2BOX_STORAGE_PUBLIC')

try:
    STORAGE_DATA_RETENTION_DAYS = int(os.environ.get('WIS2BOX_STORAGE_DATA_RETENTION_DAYS')) # noqa
except TypeError:
    STORAGE_DATA_RETENTION_DAYS = None

LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL', 'ERROR')
LOGFILE = os.environ.get('WIS2BOX_LOGGING_LOGFILE', 'stdout')

missing_environment_variables = []

required_environment_variables = [
    DATADIR,
    DOCKER_API_URL,
    API_TYPE,
    BROKER_HOST,
    BROKER_PORT,
    BROKER_USERNAME,
    BROKER_PASSWORD,
    BROKER_PUBLIC,
    URL,
    STORAGE_TYPE,
    STORAGE_SOURCE,
    STORAGE_USERNAME,
    STORAGE_PASSWORD,
    STORAGE_INCOMING,
    STORAGE_PUBLIC
]

for rev in required_environment_variables:
    if rev is None:
        envvar_name = [k for k, v in locals().items() if v is rev][0]
        LOGGER.warning(f'Missing environment variable {envvar_name}')
        missing_environment_variables.append(envvar_name)

if missing_environment_variables:
    msg = f'Environment variables not set! = {missing_environment_variables}'
    LOGGER.error(msg)
    raise EnvironmentError(msg)


@click.group()
def environment():
    """Environment management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def create(ctx, verbosity):
    """Creates baseline data/metadata directory structure"""

    click.echo(f'Setting up logging (loglevel={LOGLEVEL}, logfile={LOGFILE})')
    setup_logger(LOGLEVEL, LOGFILE)

    click.echo('Setting up storage')
    storage_defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    storages = {
        STORAGE_INCOMING: 'private',
        STORAGE_ARCHIVE: 'private',
        STORAGE_PUBLIC: 'readonly'
    }
    for key, value in storages.items():
        storage_defs['name'] = key
        storage_defs['policy'] = value
        storage = load_plugin('storage', storage_defs)
        storage.setup()

    # TODO: abstract into wis2box.storage.fs.FileSystemStorage
    click.echo(f'Creating baseline directory structure in {DATADIR}')
    DATADIR.mkdir(parents=True, exist_ok=True)
    # DATADIR_ARCHIVE.mkdir(parents=True, exist_ok=True)
    # DATADIR_CONFIG.mkdir(parents=True, exist_ok=True)
    # (DATADIR / 'cache').mkdir(parents=True, exist_ok=True)
    (DATADIR / 'metadata' / 'discovery').mkdir(parents=True, exist_ok=True)
    (DATADIR / 'metadata' / 'station').mkdir(parents=True, exist_ok=True)


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def show(ctx, verbosity):
    """Displays wis2box environment variables"""

    for key, value in os.environ.items():
        if key.startswith('WIS2BOX'):
            click.echo(f'{key} => {value}')


environment.add_command(create)
environment.add_command(show)
