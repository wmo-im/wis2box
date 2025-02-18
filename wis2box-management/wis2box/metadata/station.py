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
from iso3166 import countries
import io
import json
import logging
from pathlib import Path
from typing import Iterator, Tuple, Union

from elasticsearch import Elasticsearch
from owslib.ogcapi.features import Features
from owslib.ogcapi.records import Records
from pygeometa.schemas.wmo_wigos import WMOWIGOSOutputSchema
from pyoscar import OSCARClient

from wis2box import cli_helpers
from wis2box.api import (
    delete_collection_item, setup_collection, upsert_collection_item
)
from wis2box.env import (API_BACKEND_URL, DOCKER_API_URL,
                         BROKER_HOST, BROKER_USERNAME, BROKER_PASSWORD,
                         BROKER_PORT)
from wis2box.metadata.base import BaseMetadata
from wis2box.plugin import load_plugin, PLUGINS
from wis2box.util import get_typed_value


LOGGER = logging.getLogger(__name__)

WMDR_CODELISTS = Path('/home/wis2box/wmdr-codelists')


def get_wmdr_codelists() -> dict:
    """
    Helper function to cast WMDR codelists into object lookups

    :returns: `dict` of lookups
    """

    LOGGER.debug('Checking properties against WMDR code lists')

    codelists = {}

    column2codelists = {
        'facility_type': 'FacilityType',
        'territory_name': 'TerritoryName',
        'wmo_region': 'WMORegion'
    }

    for key, value in column2codelists.items():
        codelist_filename = WMDR_CODELISTS / f'{value}.csv'
        codelists[key] = []
        with codelist_filename.open() as fh:
            reader = csv.reader(fh)
            next(reader)
            for row in reader:
                codelists[key].append(row[4])

    return codelists


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


def load_stations() -> dict:
    """Load stations from API

    :returns: `dict` of stations
    """

    stations = {}

    try:
        es = Elasticsearch(API_BACKEND_URL)
        nbatch = 500  # TODO: make configurable
        res = es.search(index='stations', query={'match_all': {}}, size=nbatch)
        if len(res['hits']['hits']) == 0:
            LOGGER.debug('No stations found')
            return stations
        for hit in res['hits']['hits']:
            stations[hit['_source']['id']] = hit['_source']
        while len(res['hits']['hits']) > 0:
            res = es.search(
                index='stations', query={'match_all': {}},
                size=nbatch, from_=len(stations)) # noqa

            for hit in res['hits']['hits']:
                stations[hit['_source']['id']] = hit['_source']

    except Exception as err:
        LOGGER.error(f'Failed to load stations from backend: {err}')

    LOGGER.info(f'Loaded {len(stations.keys())} stations from backend')

    return stations


def get_stations_csv(wsi: str = '') -> str:
    """Load stations into csv-string

    param wsi: `str` of WIGOS Station Identifier

    :returns: `str` of CSV with station data
    """

    LOGGER.info('Loading stations into csv-string')

    csv_output = []
    stations = load_stations()

    for station in stations.values():
        wsi = station['properties']['wigos_station_identifier']
        if '-' in wsi and len(wsi.split('-')) == 4:
            tsi = wsi.split('-')[3]

        barometer_height = station['properties'].get('barometer_height', '')

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
    csv_writer = csv.DictWriter(string_buffer, fieldnames=csv_output[0].keys())
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

    oar = Records(DOCKER_API_URL)

    try:
        dm = oar.collection_items('discovery-metadata')
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


def add_topic_hierarchy(new_topic: str, territory_name: str = None,
                        wsi: str = None) -> None:
    """
    Adds topic hierarchy to topic

    :param topic: `str` of topic
    :param territory_name: `str` of territory_name, defaults to None
    :param wsi: `str` of WIGOS Station Identifier, defaults to None

    :returns: `None`
    """

    valid_topics = [topic for link, topic in load_datasets()]
    if new_topic not in valid_topics:
        msg = (f'ERROR: Invalid topic: {new_topic}\n'
               'Valid topics:\n'
               '\n'.join(valid_topics))
        LOGGER.error(msg)
        return

    stations = load_stations()
    for feature in stations.values():
        if wsi != 'any' and feature['properties']['wigos_station_identifier'] != wsi:  # noqa
            continue
        if territory_name != 'any' and feature['properties']['territory_name'] != territory_name:  # noqa
            continue

        topics = feature['properties'].get('topics', [])
        # remove topics not in valid_topics
        topics = [x for x in topics if x in valid_topics]
        # add new_topic if not already in topics
        if new_topic not in topics:
            topics.append(new_topic)
            feature['properties']['topics'] = topics
        # update the feature
        LOGGER.info(f'Updating station {feature["properties"]["wigos_station_identifier"]}')  # noqa
        try:
            delete_collection_item('stations', feature['id'])
        except RuntimeError as err:
            LOGGER.debug(f'Station does not exist: {err}')
        upsert_collection_item('stations', feature)


def publish_from_csv(path: Path, new_topic: str = None) -> None:
    """
    Publishes station collection to API config and backend from csv

    :param path: `Path` to station list CSV (default is `None`)
    :param topic: `str` of topic hierarchy (default is `None`)

    :returns: `None`
    """

    if not path.exists():
        msg = f'Station file {path} does not exist'
        LOGGER.error(msg)
        raise RuntimeError(msg)

    valid_topics = [topic for link, topic in load_datasets()]
    stations = load_stations()

    if new_topic is not None:
        if new_topic not in valid_topics:
            LOGGER.error(f'Invalid topic: {new_topic}')
            msg = 'Invalid topic, valid topics are:\n'
            msg += '\n'.join(valid_topics)
            click.echo(msg)
            return

    oscar_baseurl = 'https://oscar.wmo.int/surface/#/search/station/stationReportDetails'  # noqa

    LOGGER.debug(f'Publishing station list from {path}')
    station_list = []
    with path.open() as fh:
        # checking if file is in standard utf-8
        try:
            _ = fh.readlines()
        except UnicodeDecodeError as err:
            msg = f'Invalid utf-8 in station metadata file: {err}'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        fh.seek(0)

        reader = csv.DictReader(fh)

        for row in reader:
            wigos_station_identifier = row['wigos_station_identifier']
            station_list.append(wigos_station_identifier)

            topics = []
            topic2 = ''
            # check if station already exists, if so, get topics
            if wigos_station_identifier in stations:
                feature = stations[wigos_station_identifier]
                topics = feature['properties'].get('topics', [])
            # add new_topic if not already in topics
            if new_topic is not None:
                topic2 = new_topic
                if new_topic not in topics:
                    topics.append(new_topic)
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
                   'wmo_region': row['wmo_region'],
                   'url': f"{oscar_baseurl}/{wigos_station_identifier}",
                   'topic': topic2,
                   'topics': topics,
                   # TODO: update with real-time status as per https://codes.wmo.int/wmdr/_ReportingStatus  # noqa
                   'status': 'operational'
                }
            }

            LOGGER.debug('Checking properties against WMDR code lists')
            for key, values in get_wmdr_codelists().items():
                column_value = feature['properties'][key]
                if column_value not in values:
                    msg = f'Invalid value {column_value}'
                    raise RuntimeError(msg)

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

    LOGGER.info(f'Validating wsi={wsi}, tsi={tsi}')
    stations = load_stations()

    if wsi in stations:
        return wsi
    else:
        for station in stations.values():
            if station['properties']['traditional_station_identifier'] == tsi:
                return station['properties']['wigos_station_identifier']

    return None


def get_geometry(wsi: str = '') -> Union[dict, None]:
    """
    Validates geometry

    :param wsi: `str` WIGOS Station identifier

    :returns: `dict`, of station geometry or `None`
    """

    stations = load_stations()
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
        'wigos_station_identifier': wsi,
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
               results['territory_name']).alpha3
        except KeyError:
            results['territory_name'] = ''

    try:
        results['wmo_region'] = station['wmo_region']
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
@cli_helpers.OPTION_PATH
@cli_helpers.OPTION_TOPIC_HIERARCHY
@cli_helpers.OPTION_VERBOSITY
def publish_collection(ctx, path, topic_hierarchy, verbosity):
    """Publish from station_list.csv"""
    click.echo(f'Publishing stations from {path}')
    if topic_hierarchy is not None:
        click.echo(f'associate stations to topic={topic_hierarchy}')
    publish_from_csv(path, topic_hierarchy)

    click.echo('Done')


# add command to add topic hierarchy to stations
@click.command()
@click.pass_context
@click.argument('topic')
@click.option('--territory-name', '-t', default="any", help='Territory Name')
@click.option('--wsi', '-w', default="any", help='WIGOS Station Identifier')
@cli_helpers.OPTION_VERBOSITY
def add_topic(ctx, topic, territory_name, wsi, verbosity):
    """Adds topic to station metadata"""

    add_topic_hierarchy(topic, territory_name, wsi)
    click.echo('Done')


station.add_command(get)
station.add_command(publish_collection)
station.add_command(setup)
station.add_command(add_topic)
