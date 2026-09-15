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
import json
import logging

from owslib.ogcapi.records import Features, Records

from wis2box import cli_helpers
from wis2box.env import DATADIR, DOCKER_API_URL
from wis2box.metadata.discovery import discovery_metadata
from wis2box.metadata.station import station
from wis2box.util import json_serial

LOGGER = logging.getLogger(__name__)


@click.group()
def metadata():
    """Metadata management"""
    pass


@click.command('export')
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def export_metadata(ctx, verbosity):
    """Export discovery and station metadata to metadata-export.json."""

    export_dir = DATADIR / 'export'
    export_dir.mkdir(parents=True, exist_ok=True)
    export_file = export_dir / 'metadata-export.json'

    try:
        oar = Records(DOCKER_API_URL)
        records = oar.collection_items('discovery-metadata', limit=1000)
    except Exception as err:
        raise click.ClickException(
            f'Could not retrieve discovery-metadata items: {err}'
        )

    discovery_items = []
    for record in records['features']:
        discovery_items.append(record)

    try:
        oaf = Features(DOCKER_API_URL)
        records = oaf.collection_items('stations', limit=1000)
    except Exception as err:
        raise click.ClickException(
            f'Could not retrieve stations items: {err}'
        )

    station_items = []
    for record in records['features']:
        station_items.append(record)

    payload = {
        'discovery-metadata': discovery_items,
        'stations': station_items
    }

    with open(export_file, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, default=json_serial)

    click.echo(f'Exported {len(discovery_items)} discovery-metadata items')
    click.echo(f'Exported {len(station_items)} stations items')
    click.echo(f'Wrote metadata export to {export_file}')


metadata.add_command(discovery_metadata)
metadata.add_command(station)
metadata.add_command(export_metadata)
