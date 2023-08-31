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
from collections import OrderedDict
import csv
import json
import logging
from typing import Iterator, Union

from owslib.ogcapi.features import Features
from pygeometa.schemas.wmo_wigos import WMOWIGOSOutputSchema
from pyoscar import OSCARClient

from wis2box import cli_helpers
from wis2box.api import (
    delete_collection_item, setup_collection, upsert_collection_item
)
from wis2box.env import (DATADIR, DOCKER_API_URL,
                         BROKER_HOST, BROKER_USERNAME, BROKER_PASSWORD,
                         BROKER_PORT)
from wis2box.metadata.base import BaseMetadata
from wis2box.util import get_typed_value

from wis2box.plugin import load_plugin, PLUGINS

LOGGER = logging.getLogger(__name__)

STATION_METADATA = DATADIR / 'metadata' / 'station'
STATIONS = STATION_METADATA / 'station_list.csv'

WMO_RAS = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI'
}

if not STATIONS.exists():
    msg = f'Please create a station metadata file in {STATION_METADATA}'
    LOGGER.error(msg)
    raise RuntimeError(msg)


def get_wmo_ra_roman(ra: str) -> str:
    """
    Helper function to derive a WMO Regional Association roman numeral from
    an integer.

    :param ra: `str` of WMO RA

    :returns: `str` of WMO RA as roman numeral
    """

    if ra in WMO_RAS.values():
        return ra
    if ra.isdigit():
        try:
            return WMO_RAS[int(ra)]
        except KeyError:
            LOGGER.debug(f'Invalid region: {ra}')
            return None
    else:
        return None


def gcm() -> dict:
    """
    Gets collection metadata for API provisioning

    :returns: `dict` of collection metadata
    """

    return {
        'id': 'stations',
        'title': 'Stations',
        'description': 'Stations',
        'keywords': ['wmo', 'wis 2.0'],
        'links': ['https://oscar.wmo.int/surface'],
        'bbox': [-180, -90, 180, 90],
        'id_field': 'wigos_station_identifier',
        'title_field': 'wigos_station_identifier'
    }


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
                if link['rel'] == 'canonical':
                    yield link
    except RuntimeError:
        LOGGER.warning('discovery-metadata collection has not been created')
        yield {}


def check_station_datasets(wigos_station_identifier: str) -> Iterator[dict]:
    """
    Filter datasets for topics with observations from station

    :param wigos_station_identifier: `string` of station WIGOS id

    :returns: `list`, of link relations to collections from a station
    """

    oaf = Features(DOCKER_API_URL)

    for topic in load_datasets():
        if not topic:
            continue

        try:
            obs = oaf.collection_items(
                topic['title'],
                wigos_station_identifier=wigos_station_identifier
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

    setup_collection(meta=gcm())

    oscar_baseurl = 'https://oscar.wmo.int/surface/#/search/station/stationReportDetails'  # noqa

    LOGGER.debug(f'Publishing station list from {STATIONS}')
    station_list = []
    with STATIONS.open() as fh:
        reader = csv.DictReader(fh)

        for row in reader:
            wigos_station_identifier = row['wigos_station_identifier']
            station_list.append(wigos_station_identifier)
            topics = list(check_station_datasets(wigos_station_identifier))
            topic = None if len(topics) == 0 else topics[0]['title']

            LOGGER.debug('Verifying station coordinate types')
            for pc in ['longitude', 'latitude', 'elevation']:
                value = get_typed_value(row[pc])
                if not isinstance(value, (int, float)):
                    msg = f'Invalid station {pc} value: {value}'
                    LOGGER.error(msg)
                    raise RuntimeError(msg)

            feature = {
                'id': wigos_station_identifier,
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        get_typed_value(row['longitude']),
                        get_typed_value(row['latitude'])
                    ]
                },
                'properties': {
                   'name': row['station_name'],
                   'wigos_station_identifier': wigos_station_identifier,
                   'facility_type': row['facility_type'],
                   'territory_name': row['territory_name'],
                   'wmo_region': get_wmo_ra_roman(row['wmo_region']),
                   'url': f"{oscar_baseurl}/{wigos_station_identifier}",
                   'topic': topic,
                   # TODO: update with real-time status as per https://codes.wmo.int/wmdr/_ReportingStatus  # noqa
                   'status': 'operational'
                },
                'links': topics
            }

            station_elevation = get_typed_value(row['elevation'])

            if isinstance(station_elevation, (float, int)):
                LOGGER.debug('Adding z value to geometry')
                feature['geometry']['coordinates'].append(station_elevation)

            LOGGER.debug('Updating backend')
            try:
                delete_collection_item('stations', feature['id'])
            except RuntimeError as err:
                LOGGER.debug(f'Station does not exist: {err}')
            upsert_collection_item('stations', feature)

    LOGGER.info(f'Updated station list: {station_list}')
    # inform mqtt-metrics-collector
    notify_msg = {
        'station_list': station_list
    }
    # load plugin for local broker
    defs_local = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': f'mqtt://{BROKER_USERNAME}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}', # noqa
        'client_type': 'station-publisher'
    }
    local_broker = load_plugin('pubsub', defs_local)
    local_broker.pub('wis2box/stations', json.dumps(notify_msg), qos=0)


def get_valid_wsi(wsi: str = '', tsi: str = '') -> Union[str, None]:
    """
    Validates and returns WSI

    :param wsi: WIGOS Station identifier
    :param tsi: Traditional Station identifier

    :returns: `str`, of valid wsi or `None`
    """

    LOGGER.info(f'Validating WIGOS Station Identifier: {wsi}')
    with STATIONS.open(newline='') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if wsi == row['wigos_station_identifier'] or \
               (tsi == row['traditional_station_identifier'] and tsi != ''):
                return row['wigos_station_identifier']

    return None


def get_geometry(wsi: str = '') -> Union[dict, None]:
    """
    Validates geometry

    :param wsi: `str` WIGOS Station identifier

    :returns: `dict`, of station geometry or `None`
    """

    LOGGER.info(f'Validating WIGOS Station Identifier: {wsi}')
    with STATIONS.open(newline='') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if wsi == row['wigos_station_identifier']:
                LOGGER.debug('Found matching WSI')
                feature = {
                    'type': 'Point',
                    'coordinates': [
                        get_typed_value(row['longitude']),
                        get_typed_value(row['latitude'])
                    ]
                }

                station_elevation = get_typed_value(row['elevation'])

                if isinstance(station_elevation, (float, int)):
                    LOGGER.debug('Adding z value to geometry')
                    feature['coordinates'].append(station_elevation)

                return feature

    LOGGER.debug('No matching WSI')
    return None


@click.command()
@click.pass_context
@click.option('--wigos-station-identifier', '-wsi',
              help='WIGOS station identifier')
@cli_helpers.OPTION_VERBOSITY
def get(ctx, wigos_station_identifier, verbosity):
    """Publishes collection of stations to API config and backend"""

    client = OSCARClient(env='prod')

    station = client.get_station_report(wigos_station_identifier)

    results = OrderedDict({
        'station_name': station['name'],
        'wigos_station_identifier': wigos_station_identifier,
        'traditional_station_identifier': None,
        'facility_type': station['typeName'],
        'latitude': station['locations'][0]['latitude'],
        'longitude': station['locations'][0]['longitude'],
        'elevation': station['locations'][0].get('elevation'),
        'territory_name': station['territories'][0]['territoryName'],
        'wmo_region': WMO_RAS[station['wmoRaId']]
    })

    if '0-2000' in station['wigosIds'][0]['wid']:
        results['traditional_station_identifier'] = station['wigosIds'][0]['wid'].split('-')[-1]  # noqa

    for v in ['station_name', 'territory_name']:
        if ',' in results[v]:
            results[v] = f'"{results[v]}"'

    line = ','.join([(str(results[k]) if results[k] is not None else '') for k, v in results.items()])  # noqa

    click.echo(line)


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def publish_collection(ctx, verbosity):
    """Publishes collection of stations to API config and backend"""

    publish_station_collection()
    click.echo('Done')


station.add_command(get)
station.add_command(publish_collection)
