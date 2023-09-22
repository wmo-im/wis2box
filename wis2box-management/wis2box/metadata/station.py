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
import io

import click
from collections import OrderedDict
import csv
from iso3166 import countries
import json
import logging
from typing import Iterator, Tuple, Union

from owslib.ogcapi.features import Features
from pygeometa.schemas.wmo_wigos import WMOWIGOSOutputSchema
from pyoscar import OSCARClient

from wis2box import cli_helpers
from wis2box.api import (
    delete_collection_item, setup_collection, upsert_collection_item
)
from wis2box.env import (DATADIR, API_BACKEND_URL, DOCKER_API_URL,
                         BROKER_HOST, BROKER_USERNAME, BROKER_PASSWORD,
                         BROKER_PORT)
from wis2box.metadata.base import BaseMetadata
from wis2box.util import get_typed_value

from elasticsearch import Elasticsearch
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

WMDR_RAS = {
    'africa': 'I',
    'asia': 'II',
    'southAmerica': 'III',
    'northCentralAmericaCaribbean': 'IV',
    'southWestPacific': 'V',
    'europe': 'VI'
}


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


def load_stations(wsi='') -> dict:
    """Load stations from API

    param wsi: `str` of WIGOS Station Identifier

    :returns: `dict` of stations
    """

    stations = {}

    try:
        es = Elasticsearch(API_BACKEND_URL)
        nbatch = 500
        res = es.search(index="stations", query={"match_all": {}}, size=nbatch) # noqa
        if len(res['hits']['hits']) == 0:
            LOGGER.debug('No stations found')
            return stations
        for hit in res['hits']['hits']:
            stations[hit['_source']['id']] = hit['_source']
        while len(res['hits']['hits']) > 0:
            res = es.search(index="stations", query={"match_all": {}}, size=nbatch, from_=len(stations)) # noqa
            for hit in res['hits']['hits']:
                stations[hit['_source']['id']] = hit['_source']
    except Exception as err:
        LOGGER.error(f'Failed to load stations from backend: {err}')

    LOGGER.info(f"Loaded {len(stations.keys())} stations from backend")

    return stations


def get_stations_csv(wsi='') -> str:
    """Load stations into csv-string

    param wsi: `str` of WIGOS Station Identifier

    :returns: csv_string: csv string with station data
    """

    LOGGER.info('Loading stations into csv-string')

    stations = load_stations(wsi)

    csv_output = []
    for station in stations.values():
        wsi = station['properties']['wigos_station_identifier']
        if '-' in wsi and len(wsi.split("-")) == 4:
            tsi = wsi.split("-")[3]
        barometer_height = None
        if 'barometer_height' in station['properties']:
            barometer_height = station['properties']['barometer_height']
        else:
            barometer_height = station['geometry']['coordinates'][2] + 1.25
        obj = {
            'station_name': station['properties']['name'],
            'wigos_station_identifier': wsi,
            'traditional_station_identifier': tsi,
            'facility_type': station['properties']['facility_type'],
            'latitude': station['geometry']['coordinates'][1],
            'longitude': station['geometry']['coordinates'][0],
            'elevation': station['geometry']['coordinates'][2],
            'barometer_height': barometer_height,
            'territory_name': station['properties']['territory_name'],
            'wmo_region': station['properties']['wmo_region']
        }
        csv_output.append(obj)

    string_buffer = io.StringIO()
    csv_writer = csv.DictWriter(string_buffer, fieldnames=csv_output[0].keys())  # noqa
    csv_writer.writeheader()
    csv_writer.writerows(csv_output)
    csv_string = string_buffer.getvalue()
    string_buffer.close()
    return csv_string


def load_datasets() -> Iterator[Tuple[dict, str]]:
    """
    Load datasets from oapi

    :returns: `list`, of link relations and topics for all datasets
    """
    oaf = Features(DOCKER_API_URL)

    try:
        dm = oaf.collection_items('discovery-metadata')
        for topic in dm['features']:
            for link in topic['links']:
                if link['rel'] == 'canonical':
                    yield link, topic['properties']['wmo:topicHierarchy']
    except RuntimeError:
        LOGGER.warning('discovery-metadata collection has not been created')
        yield {}, None


def check_station_datasets(wigos_station_identifier: str) -> Iterator[dict]:
    """
    Filter datasets for topics with observations from station

    :param wigos_station_identifier: `string` of station WIGOS id

    :returns: `list`, of link relations to collections from a station
    """

    oaf = Features(DOCKER_API_URL)

    for topic, topic2 in load_datasets():
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
            topic['topic'] = topic2.replace('origin/a/wis2/', '')
            yield topic


def publish_station_collection() -> None:
    """
    Publishes station collection to API config and backend

    :returns: `None`
    """

    if not STATIONS.exists():
        msg = f'Please create a station metadata file in {STATION_METADATA}'
        LOGGER.error(msg)
        raise RuntimeError(msg)

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

            try:
                barometer_height = float(row['barometer_height'])
            except ValueError:
                barometer_height = None

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
                   'traditional_station_identifier': row['traditional_station_identifier'],  # noqa
                   'barometer_height': barometer_height,
                   'facility_type': row['facility_type'],
                   'territory_name': row['territory_name'],
                   'wmo_region': get_wmo_ra_roman(row['wmo_region']),
                   'url': f"{oscar_baseurl}/{wigos_station_identifier}",
                   'topic': topic,
                   'topics': [x['topic'] for x in topics],
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
    stations = load_stations(wsi)

    if wsi in stations:
        return wsi

    return None


def get_geometry(wsi: str = '') -> Union[dict, None]:
    """
    Validates geometry

    :param wsi: `str` WIGOS Station identifier

    :returns: `dict`, of station geometry or `None`
    """

    stations = load_stations(wsi)
    if wsi in stations:
        return stations[wsi]['geometry']

    LOGGER.debug('No matching WSI')
    return None


@click.command()
@click.pass_context
@click.argument('wsi')
@cli_helpers.OPTION_VERBOSITY
def get(ctx, wsi, verbosity):
    """Queries OSCAR/Surface for station information"""

    client = OSCARClient(env='prod')

    try:
        station = client.get_station_report(wsi, format_='XML', summary=True)
    except RuntimeError as err:
        raise click.ClickException(err)

    results = OrderedDict({
        'station_name': station['station_name'],
        'wigos_station_identifier': station['wigos_station_identifier'],
        'traditional_station_identifier': None,
        'facility_type': station['facility_type'],
        'latitude': station.get('latitude', ''),
        'longitude': station.get('longitude', ''),
        'elevation': station.get('elevation'),
        'barometer_height': station['barometer_height'],
        'territory_name': station.get('territory_name', '')
    })

    if results['territory_name'] not in [None, '']:
        try:
            results['territory_name'] = countries.get(
               results['territory_name']).name
        except KeyError:
            results['territory_name'] = ''

    try:
        results['wmo_region'] = WMO_RAS[station['wmo_region']]
    except KeyError:
        try:
            results['wmo_region'] = WMDR_RAS[station['wmo_region']]
        except KeyError:
            results['wmo_region'] = ''

    if station['wigos_station_identifier'].startswith('0-20000'):
        results['traditional_station_identifier'] = station['wigos_station_identifier'].split('-')[-1]  # noqa

    for v in ['station_name', 'territory_name']:
        if ',' in results[v]:
            results[v] = f'"{results[v]}"'

    line = ','.join([(str(results[k]) if results[k] is not None else '') for k, v in results.items()])  # noqa

    click.echo(line)


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, verbosity):
    """Initializes metadata repository"""

    click.echo('Setting up station metadata repository')
    setup_collection(meta=gcm())


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def publish_collection(ctx, verbosity):
    """Publishes collection of stations to API config and backend"""

    publish_station_collection()
    click.echo('Done')


station.add_command(get)
station.add_command(publish_collection)
station.add_command(setup)
