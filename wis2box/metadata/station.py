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
import csv
import json
import logging
from pathlib import Path

from owslib.ogcapi.features import Features
from pygeometa.schemas.wmo_wigos import WMOWIGOSOutputSchema

from wis2box import cli_helpers
from wis2box.api.backend import load_backend
from wis2box.api.config import load_config
from wis2box.env import DATADIR
from wis2box.metadata.base import BaseMetadata
from wis2box.metadata.oscar import get_station_report, upload_station_metadata

LOGGER = logging.getLogger(__name__)
API_URL = 'http://wis2box-api:80/oapi'


class StationMetadata(BaseMetadata):
    def __init__(self):
        super().__init__()

    def generate(mcf: dict) -> str:
        """
        Generate WIGOS station metadata

        :param mcf: `dict` of MCF file

        :returns: `str` of metadata representation
        """

        LOGGER.debug('Generating WIGOS station metadata')
        return WMOWIGOSOutputSchema().write(mcf)


@click.group()
def station():
    """Station metadata management"""
    pass


def load_topics():
    oaf = Features(API_URL)

    dm = oaf.collection_items('discovery-metadata')

    for topic in dm['features']:
        for link in topic['properties']['associations']:
            if link['type'] == 'OAFeat':
                yield link


def check_station_topics(topics, wigos_id):
    oaf = Features(API_URL)

    for topic in topics:
        obs = oaf.collection_items(
            topic['title'], wigos_station_identifier=wigos_id)
        if obs['numberMatched'] > 0:
            yield topic


def publish_station_collection() -> None:
    """
    Publishes station collection to API config and backend

    :returns: `None`
    """

    backend = load_backend()

    oscar_baseurl = 'https://oscar.wmo.int/surface/#/search/station/stationReportDetails'  # noqa

    station_metadata_files = Path(DATADIR) / 'metadata' / 'station'
    topics = load_topics()

    for f in station_metadata_files.glob('*.json'):
        with f.open() as fh:
            d = json.load(fh)
            wigos_id = d['wigosIds'][0]['wid']
            station_topics = check_station_topics(topics, wigos_id)
            feature = {
                'id': d['id'],
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        d['locations'][0]['longitude'],
                        d['locations'][0]['latitude'],
                        d['locations'][0]['elevation']
                    ]
                },
                'properties': {
                    'wigos_id': wigos_id,
                    'name': d['name'],
                    'url': f"{oscar_baseurl}/{wigos_id}",
                    'topics': list(station_topics),
                    # TODO: update with real-time status as per https://codes.wmo.int/wmdr/_ReportingStatus  # noqa
                    'status': 'operational'
                }
            }

        LOGGER.debug('Publishing to backend')
        backend.upsert_collection_items('stations', [feature])

    click.echo('Adding to API configuration')
    collection = {
        'id': 'stations',
        'title': 'Stations',
        'description': 'Stations',
        'keywords': ['wmo', 'wis 2.0'],
        'links': ['https://oscar.wmo.int/surface'],
        'bbox': [-180, -90, 180, 90],
        'id_field': 'wigos_id',
        'title_field': 'wigos_id'
    }

    api_config = load_config()
    api_config.add_collection(collection)

    return


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
@cli_helpers.ARGUMENT_FILEPATH
def cache(ctx, filepath, verbosity):
    """Caches local station metadata in with WMO OSCAR/Surface"""

    click.echo(f'Caching OSCAR/Surface metadata from in {filepath.name}')
    reader = csv.DictReader(filepath)

    for row in reader:
        wsi = row['wigos_station_identifier']
        click.echo(f"Caching station metadata for {wsi}")
        try:
            station_report = get_station_report(wsi)
        except RuntimeError:
            click.echo(f'Station not found: {wsi}')

        filename = f"{DATADIR}/metadata/station/{wsi}.json"
        LOGGER.debug(f'Writing file to {filename}')
        with open(filename, 'w') as fh:
            json.dump(station_report, fh)


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def publish_collection(ctx, verbosity):
    """Publishes collection of stations to API config and backend"""

    publish_station_collection()
    click.echo('Done')


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates station metadata to OSCAR/Surface"""

    click.echo(f'Publishing {filepath.name} to OSCAR/Surface')
    try:
        record = StationMetadata()
        station_metadata = record.parse_record(filepath.read())
        upload_station_metadata(record.generate(station_metadata))
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Done')


station.add_command(publish)
station.add_command(publish_collection)
station.add_command(cache)
