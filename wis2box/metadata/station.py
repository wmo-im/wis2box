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
from typing import Iterator

from owslib.ogcapi.features import Features
from pygeometa.schemas.wmo_wigos import WMOWIGOSOutputSchema

from wis2box import cli_helpers
from wis2box.api.backend import load_backend
from wis2box.api.config import load_config
from wis2box.env import DATADIR, DOCKER_API_URL
from wis2box.metadata.base import BaseMetadata
from wis2box.metadata.oscar import get_station_report, upload_station_metadata

LOGGER = logging.getLogger(__name__)
STATION_METADATA = DATADIR / 'metadata' / 'station'


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


def load_datasets() -> Iterator[dict]:
    """
    Load datasets from oapi

    :returns: `list`, of link relations for all datasets
    """
    oaf = Features(DOCKER_API_URL)

    try:
        dm = oaf.collection_items('discovery-metadata')
        for topic in dm['features']:
            for link in topic['links']:
                if link['type'] == 'OAFeat':
                    yield link
    except RuntimeError:
        LOGGER.warning('discovery-metadata collection has not been created')
        yield {}


def check_station_datasets(wigos_id: str) -> Iterator[dict]:
    """
    Filter datasets for topics with observations from station

    :param datasets: `list` of datasets
    :param wigos_id: `string` of station WIGOS id


    :returns: `list`, of link relations to collections from a station
    """

    oaf = Features(DOCKER_API_URL)

    for topic in load_datasets():
        if not topic:
            continue

        try:
            obs = oaf.collection_items(
                topic['title'], wigos_station_identifier=wigos_id
            )
        except RuntimeError as err:
            LOGGER.warning(f'Warning from topic {topic["title"]}: {err}')
            continue

        if obs['numberMatched'] > 0:
            topic['type'] = 'application/json'
            yield topic


def publish_station_collection() -> None:
    """
    Publishes station collection to API config and backend

    :returns: `None`
    """

    backend = load_backend()
    LOGGER.debug('Deleting existing station collection')
    try:
        backend.delete_collection('stations')
    except RuntimeError as err:
        LOGGER.warning(err)

    oscar_baseurl = 'https://oscar.wmo.int/surface/#/search/station/stationReportDetails'  # noqa

    for f in STATION_METADATA.glob('*.json'):
        LOGGER.debug(f'Adding station metadata from {f.name}')
        with f.open() as fh:
            d = json.load(fh)
            wigos_id = d['wigosIds'][0]['wid']
            topics = list(check_station_datasets(wigos_id))
            topic = None if len(topics) == 0 else topics[0]['title']
            feature = {
                'id': d['id'],
                'type': 'Feature',
                'geometry': get_geometry(wigos_id),
                'properties': {
                    'wigos_id': wigos_id,
                    'name': d['name'],
                    'url': f"{oscar_baseurl}/{wigos_id}",
                    'topic': topic,
                    # TODO: update with real-time status as per https://codes.wmo.int/wmdr/_ReportingStatus  # noqa
                    'status': 'operational'
                },
                'links': topics
            }

        LOGGER.debug('Publishing to backend')
        backend.upsert_collection_items('stations', [feature])

    click.echo('Adding to API configuration')
    meta = {
        'id': 'stations',
        'title': 'Stations',
        'description': 'Stations',
        'keywords': ['wmo', 'wis 2.0'],
        'links': ['https://oscar.wmo.int/surface'],
        'bbox': [-180, -90, 180, 90],
        'id_field': 'wigos_id',
        'title_field': 'wigos_id',
    }

    api_config = load_config()
    collection = api_config.prepare_collection(meta)
    api_config.add_collection('stations', collection)

    return


def validate_wsi(wsi: str) -> bool:
    """
    Validates and caches WSI from WMO OSCAR/Surface

    :param wsi: `str` WIGOS Station identifier

    :returns: `bool`, of wsi validity
    """
    stations = STATION_METADATA / 'station_list.csv'

    if stations.exists() is False:
        with stations.open('w', newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(['station_name', 'wigos_station_identifier'])

    LOGGER.info(f'Validating WIGOS Station Identifier: {wsi}')
    with stations.open(newline='') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if wsi == row['wigos_station_identifier']:
                return True

    LOGGER.debug('Validating WSI with OSCAR/Surface')
    try:
        station_report = get_station_report(wsi)
        station_name = station_report['name']
    except RuntimeError:
        LOGGER.warning(f'Station not found: {wsi}')
        return False

    LOGGER.debug('WSI valid, caching...')
    with stations.open('a', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow([station_name, wsi])

    filename = STATION_METADATA / f'{wsi}.json'
    LOGGER.debug(f'Caching station report to {filename}')
    with filename.open('w') as fh:
        json.dump(station_report, fh)

    return True


def get_geometry(wsi: str) -> dict:
    """
    Validates and caches station geometry from WMO OSCAR/Surface

    :param wsi: `str` WIGOS Station identifier

    :returns: `dict`, of station geometr
    """
    geom = {
        'type': 'Point',
        'coordinates': [],
    }
    if validate_wsi(wsi) is False:
        return geom

    filename = STATION_METADATA / f'{wsi}.json'

    if filename.exists():
        with filename.open() as fh:
            station_report = json.load(fh)
    else:
        LOGGER.debug(f'Caching station report to {filename}')
        station_report = get_station_report(wsi)
        with filename.open('w') as fh:
            json.dump(station_report, fh)

    geom['coordinates'] = [
        station_report['locations'][0]['longitude'],
        station_report['locations'][0]['latitude'],
        station_report['locations'][0]['elevation'],
    ]

    return geom


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

        filename = STATION_METADATA / f'{wsi}.json'
        LOGGER.debug(f'Writing file to {filename}')
        with filename.open('w') as fh:
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
@cli_helpers.OPTION_VERBOSITY
@cli_helpers.ARGUMENT_FILEPATH
def sync(ctx, filepath, verbosity):
    ctx.invoke(cache, filepath=filepath, verbosity=verbosity)
    ctx.invoke(publish_collection, verbosity=verbosity)


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
station.add_command(sync)
