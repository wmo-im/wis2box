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
from wis2box.api import upsert_collection_item
from wis2box.env import HOST_DATADIR, DATADIR, DOCKER_API_URL
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

    dataset_items = []
    for record in records['features']:
        dataset_items.append(record)

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
        'discovery-metadata': dataset_items,
        'stations': station_items
    }

    with open(export_file, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, default=json_serial)

    click.echo(f'Exported {len(dataset_items)} discovery-metadata items')
    click.echo(f'Exported {len(station_items)} stations items')
    click.echo(f'Wrote metadata export to {export_file}')
    export_file_on_host = HOST_DATADIR / 'export' / 'metadata-export.json'
    click.echo(f'Available on docker-host at {export_file_on_host}')


@click.command('import')
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def import_metadata(ctx, filepath, verbosity):
    """Import discovery metadata and stations from JSON export."""

    try:
        payload = json.load(filepath)
    except Exception as err:
        raise click.ClickException(f'Could not read import file: {err}')

    if not isinstance(payload, dict):
        raise click.ClickException('Import file must contain a JSON object')

    dataset_items = payload.get('discovery-metadata', [])
    station_items = payload.get('stations', [])

    oar = Records(DOCKER_API_URL)
    oaf = Features(DOCKER_API_URL)

    dataset_prev_items = oar.collection_items('discovery-metadata').get(
        'features', []
    )
    station_prev_items = oaf.collection_items('stations').get('features', [])

    dataset_count = len(dataset_prev_items)
    station_count = len(station_prev_items)

    if dataset_count > 0 or station_count > 0:
        click.echo(
            'WARNING: Existing items found in collections. '
            f'datasets={dataset_count}, '
            f'stations={station_count}. '
            'Items with the same id will be overwritten.'
        )
        if not click.confirm('Do you want to continue? [y/N]', default=False):
            click.echo('Import cancelled.')
            return

    dataset_ids = {item.get('id') for item in dataset_prev_items}
    station_ids = {item.get('id') for item in station_prev_items}

    for item in dataset_items:
        identifier = item.get('id')
        if identifier is None:
            raise click.ClickException('Discovery metadata item missing id')

        if identifier in dataset_ids:
            click.echo(f'Overwriting discovery item with id={identifier}')
        else:
            click.echo(f'Adding new discovery item with id={identifier}')
        upsert_collection_item('discovery-metadata', item)

    for item in station_items:
        identifier = item.get('id')
        if identifier is None:
            raise click.ClickException('Station item missing id')

        if identifier in station_ids:
            click.echo(f'Overwriting station item with id={identifier}')
        else:
            click.echo(f'Adding new station item with id={identifier}')
        upsert_collection_item('stations', item)

    click.echo('Import complete.')


metadata.add_command(discovery_metadata)
metadata.add_command(station)
metadata.add_command(export_metadata)
metadata.add_command(import_metadata)
