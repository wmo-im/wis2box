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
from copy import deepcopy
from datetime import date, datetime
import json
import logging
import time
from urllib.parse import urlparse

from owslib.ogcapi.records import Records
from typing import Union

from pygeometa.schemas.wmo_wcmp2 import WMOWCMP2OutputSchema

from wis2box import cli_helpers
from wis2box.api import (delete_collection_item, remove_collection,
                         setup_collection, upsert_collection_item)
from wis2box.data_mappings import refresh_data_mappings
from wis2box.env import (API_URL, BROKER_PUBLIC, DOCKER_API_URL,
                         STORAGE_PUBLIC, STORAGE_SOURCE, URL)
from wis2box.metadata.base import BaseMetadata
from wis2box.plugin import load_plugin, PLUGINS
from wis2box.pubsub.message import WISNotificationMessage
from wis2box.storage import put_data, delete_data
from wis2box.util import json_serial

LOGGER = logging.getLogger(__name__)


class DiscoveryMetadata(BaseMetadata):
    def __init__(self):
        super().__init__()

    def generate(self, mcf: dict) -> str:
        """
        Generate OARec discovery metadata

        :param mcf: `dict` of MCF file

        :returns: `dict` of metadata representation
        """

        md = deepcopy(mcf)

        identifier = md['metadata']['identifier']

        local_topic = mcf['wis2box']['topic_hierarchy'].replace('.', '/')
        mqtt_topic = f'origin/a/wis2/{local_topic}'

        LOGGER.debug('Adding topic hierarchy')
        md['identification']['wmo_topic_hierarchy'] = local_topic
        LOGGER.debug('Adding revision date')
        md['identification']['dates']['revision'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')  # noqa

        LOGGER.debug('Checking temporal extents')
        if md['identification']['extents']['temporal'][0].get('begin', 'BEGIN_DATE') is None:  # noqa
            today = date.today().strftime('%Y-%m-%d')
            md['identification']['extents']['temporal'][0]['begin'] = today

        LOGGER.debug('Adding distribution links')
        oafeat_link, mqp_link, canonical_link = self.get_distribution_links(
            identifier, mqtt_topic, format_='mcf')

        md['distribution'] = {
            'oafeat': oafeat_link,
            'mqtt': mqp_link,
            'canonical': canonical_link
        }

        LOGGER.debug('Adding data policy')
        md['identification']['wmo_data_policy'] = mqtt_topic.split('/')[5]

        LOGGER.debug('Generating OARec discovery metadata')
        record = WMOWCMP2OutputSchema().write(md, stringify=False)
        record['properties']['wmo:topicHierarchy'] = mqtt_topic
        record['wis2box'] = mcf['wis2box']

        if record['properties']['contacts'][0].get('organization') is None:
            record['properties']['contacts'][0]['organization'] = record['properties']['contacts'][0].pop('name', "NOTSET")  # noqa

        try:
            phone = record['properties']['contacts'][0]['phones'][0]['value']
            if isinstance(phone, int):
                record['properties']['contacts'][0]['phones'][0]['value'] = f'+{phone}'  # noqa
            elif not phone.startswith('+'):
                LOGGER.debug('Casting phone to string')
                record['properties']['contacts'][0]['phones'][0]['value'] = f'+{phone}'  # noqa
        except KeyError:
            LOGGER.debug('No phone number defined')

        try:
            postalcode = record['properties']['contacts'][0]['addresses'][0]['postalcode']  # noqa
            if isinstance(postalcode, int):
                record['properties']['contacts'][0]['addresses'][0]['postalcode'] = f'{postalcode}'  # noqa
        except KeyError:
            LOGGER.debug('No postal code defined')
            pass

        return record

    def get_distribution_links(self, identifier: str, topic: str,
                               format_='mcf') -> list:
        """
        Generates distribution links

        :param identifier: `str` of metadata identifier
        :param topic: `str` of associated topic
        :param format_: `str` of format (`mcf` or `wcmp2`)

        :returns: `list` of distribution links
        """

        LOGGER.debug('Adding distribution links')
        oafeat_link = {
            'href': f"{API_URL}/collections/{identifier}?f=json",
            'type': 'application/json',
            'name': identifier,
            'description': identifier,
            'rel': 'collection'
        }

        mqp_link = {
            'href': get_broker_public_endpoint(),
            'type': 'application/json',
            'name': topic,
            'description': 'Notifications',
            'rel': 'items',
            'channel': topic
        }

        canonical_link = {
            'href': f"{API_URL}/collections/discovery-metadata/items/{identifier}",  # noqa
            'type': 'application/geo+json',
            'name': identifier,
            'description': identifier,
            'rel': 'canonical'
        }

        if format_ == 'mcf':
            for link in [oafeat_link, mqp_link, canonical_link]:
                link['url'] = link.pop('href')

        return oafeat_link, mqp_link, canonical_link


def publish_broker_message(record: dict, storage_path: str,
                           centre_id: str) -> str:
    """
    Publish discovery metadata to broker

    :param record: `dict` of discovery metadata record
    :param storage_path: `str` of storage path/object id
    :param centre_id: centre acronym

    :returns: `str` of WIS message
    """

    topic = f'origin/a/wis2/{centre_id.lower()}/metadata'  # noqa

    datetime_ = datetime.strptime(record['properties']['created'], '%Y-%m-%dT%H:%M:%SZ')  # noqa
    identifier = f"{centre_id.lower()}/metadata/{record['id']}"
    wis_message = WISNotificationMessage(identifier=identifier,
                                         metadata_id=None,
                                         filepath=storage_path,
                                         datetime_=datetime_,
                                         geometry=record['geometry']).dumps()

    # load plugin for plugin-broker
    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': BROKER_PUBLIC,
        'client_type': 'publisher'
    }
    broker = load_plugin('pubsub', defs)

    success = broker.pub(topic, wis_message)
    if not success:
        raise RuntimeError(f'Failed to publish message to {topic}')

    return wis_message


def gcm() -> dict:
    """
    Gets collection metadata for API provisioning

    :returns: `dict` of collection metadata
    """

    return {
        'id': 'discovery-metadata',
        'type': 'record',
        'title': 'Discovery metadata',
        'description': 'Discovery metadata',
        'keywords': ['wmo', 'wis 2.0'],
        'links': ['https://example.org'],
        'bbox': [-180, -90, 180, 90],
        'id_field': 'identifier',
        'time_field': 'created',
        'title_field': 'title'
    }


def publish_discovery_metadata(metadata: Union[dict, str]):
    """
    Inserts or updates discovery metadata to catalogue

    :param metadata: `str` of MCF or `dict` of WCMP2

    :returns: `bool` of publishing result
    """

    setup_collection(meta=gcm())

    LOGGER.debug('Publishing discovery metadata')
    try:
        new_links = []

        if isinstance(metadata, dict):
            LOGGER.info('Adding WCMP2 record from dictionary')
            record = metadata
            dm = DiscoveryMetadata()
            distribution_links = dm.get_distribution_links(
                record['id'], record['properties']['wmo:topicHierarchy'],
                format_='wcmp2')
            # update links, do not extend or we get duplicates
            record['links'] = distribution_links
            for link in record['links']:
                if 'description' in link:
                    link['title'] = link.pop('description')
                if 'url' in link:
                    link['href'] = link.pop('url')
        else:
            LOGGER.debug('Transforming MCF into WCMP2 record')
            dm = DiscoveryMetadata()
            record_mcf = dm.parse_record(metadata)
            record = dm.generate(record_mcf)

        if 'x-wmo' in record['id']:
            msg = 'Change x-wmo to wmo in metadata identifier'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        if 'data_mappings' not in record['wis2box']:
            msg = 'Missing wis2box.data_mappings definition'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        oar = Records(DOCKER_API_URL)
        try:
            LOGGER.debug('Checking if record / auth enabled')
            r = oar.collection_item('discovery-metadata', record['id']).json()
            if r['wis2box'].get('has_auth', False):
                record['wis2box']['has_auth'] = True
        except Exception:
            LOGGER.debug('No auth defined')

        LOGGER.debug('Publishing to API')
        upsert_collection_item('discovery-metadata', record)

        LOGGER.debug('Removing internal wis2box metadata')
        record.pop('wis2box')

        LOGGER.debug('Sanitizing links')
        if 'links' in record:
            old_links = record.pop('links')

        for ol in old_links:
            if API_URL not in ol['href']:
                new_links.append(ol)

        record['links'] = new_links

        LOGGER.debug('Saving to object storage')
        data_bytes = json.dumps(record,
                                default=json_serial).encode('utf-8')
        storage_path = f"{STORAGE_SOURCE}/{STORAGE_PUBLIC}/metadata/{record['id']}.json"  # noqa

        put_data(data_bytes, storage_path, 'application/geo+json')

        LOGGER.debug('Publishing message')
        centre_id = record['properties']['wmo:topicHierarchy'].split('/')[3]
        try:
            message = publish_broker_message(record, storage_path,
                                             centre_id)
        except Exception as err:
            msg = 'Failed to publish discovery metadata to public broker'
            LOGGER.error(msg)
            raise RuntimeError(msg) from err
        try:
            upsert_collection_item('messages', json.loads(message))
        except Exception as err:
            msg = f'Failed to publish message to API: {err}'
            LOGGER.error(msg)
            raise RuntimeError(msg) from err

    except Exception as err:
        LOGGER.warning(err)
        raise RuntimeError(err)

    return


def get_broker_public_endpoint() -> str:
    """
    Helper function to use WIS2BOX_URL to create a publically accessible
    broker endpoint
    """

    url_parsed = urlparse(URL)

    if url_parsed.scheme == 'https':
        scheme = 'mqtts'
        port = 8883
    else:
        scheme = 'mqtt'
        port = 1883

    return f'{scheme}://everyone:everyone@{url_parsed.hostname}:{port}'


@click.group('discovery')
def discovery_metadata():
    """Discovery metadata management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, verbosity):
    """Initializes metadata repository"""

    click.echo('Setting up discovery metadata repository')
    setup_collection(meta=gcm())


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def republish(ctx, verbosity):
    """Republish all published discovery metadata"""

    # read existing records
    oar = Records(DOCKER_API_URL)
    try:
        records = oar.collection_items('discovery-metadata')
        for record in records['features']:
            click.echo(f'Republishing {record["id"]}')
            try:
                publish_discovery_metadata(record)
            except Exception as err:
                raise click.ClickException(f'Failed to publish: {err}')
    except Exception as err:
        click.echo(f'Could not retrieve records: {err}')


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    click.echo(f'Publishing discovery metadata from {filepath.name}')
    try:
        publish_discovery_metadata(filepath.read())
    except Exception as err:
        raise click.ClickException(f'Failed to publish: {err}')
    refresh_data_mappings()
    time.sleep(1)
    refresh_data_mappings()
    click.echo('Discovery metadata published')


@click.command()
@click.pass_context
@click.argument('identifier')
@click.option('--force', '-f', default=False, is_flag=True,
              help='Force delete associated data from API')
@cli_helpers.OPTION_VERBOSITY
def unpublish(ctx, identifier, verbosity, force=False):
    """Deletes a discovery metadata record from the catalogue"""

    click.echo(f'Un-publishing discovery metadata {identifier}')
    try:
        delete_collection_item('discovery-metadata', identifier)
    except Exception:
        raise click.ClickException('Invalid metadata identifier')
    refresh_data_mappings()
    time.sleep(1)
    refresh_data_mappings()
    click.echo('Discovery metadata unpublished')

    if force:
        click.echo('Deleting associated data from the API')
        remove_collection(identifier)
        click.echo('Removing data from object storage')
        storage_path = f"{STORAGE_SOURCE}/{STORAGE_PUBLIC}/metadata/{identifier}.json" # noqa
        try:
            delete_data(storage_path)
        except Exception:
            raise click.ClickException('Failed to remove data from object storage') # noqa


discovery_metadata.add_command(publish)
discovery_metadata.add_command(setup)
discovery_metadata.add_command(unpublish)
discovery_metadata.add_command(republish)
