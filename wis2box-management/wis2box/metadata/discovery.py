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

from pygeometa.schemas.wmo_wcmp2 import WMOWCMP2OutputSchema

from wis2box import cli_helpers
from wis2box.api import (setup_collection, upsert_collection_item,
                         delete_collection_item)
from wis2box.data_mappings import DATADIR_DATA_MAPPINGS
from wis2box.env import API_URL, BROKER_PUBLIC, STORAGE_PUBLIC, STORAGE_SOURCE
from wis2box.metadata.base import BaseMetadata
from wis2box.plugin import load_plugin, PLUGINS
from wis2box.pubsub.message import WISNotificationMessage
from wis2box.storage import put_data
from wis2box.util import json_serial, remove_auth_from_url

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
        oafeat_link = {
            'url': f"{API_URL}/collections/{identifier}",
            'type': 'OAFeat',
            'name': identifier,
            'description': identifier,
            'rel': 'collection'
        }

        mqp_link = {
            'url': remove_auth_from_url(BROKER_PUBLIC, 'everyone:everyone'),
            'type': 'MQTT',
            'name': mcf['wis2box']['topic_hierarchy'],
            'description': mcf['wis2box']['topic_hierarchy'],
            'rel': 'data',
            'channel': mqtt_topic
        }

        canonical_link = {
            'url': f"{API_URL}/collections/discovery-metadata/items/{identifier}",  # noqa
            'type': 'OARec',
            'name': identifier,
            'description': identifier,
            'rel': 'canonical'
        }

        md['distribution'] = {
            'oafeat': oafeat_link,
            'mqtt': mqp_link,
            'canonical': canonical_link
        }

        LOGGER.debug('Adding data policy')
        md['identification']['wmo_data_policy'] = mqtt_topic.split('/')[6]

        LOGGER.debug('Generating OARec discovery metadata')
        record = WMOWCMP2OutputSchema().write(md, stringify=False)
        record['properties']['wmo:topicHierarchy'] = mqtt_topic
        record['properties']['contacts'][0]['organization'] = record['properties']['contacts'][0].pop('name')  # noqa

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
            LOGGER.debug('No phone number defined')
            pass

        return record


def publish_broker_message(record: dict, storage_path: str, country: str,
                           centre_id: str) -> str:
    """
    Publish discovery metadata to broker

    :param record: `dict` of discovery metadata record
    :param storage_path: `str` of storage path/object id
    :param country: ISO 3166 alpha 3
    :param centre_id: centre acronym

    :returns: `str` of WIS message
    """

    topic = f'origin/a/wis2/{country.lower()}/{centre_id.lower()}/metadata'  # noqa

    datetime_ = datetime.strptime(record['properties']['created'], '%Y-%m-%dT%H:%M:%SZ')  # noqa
    wis_message = WISNotificationMessage(record['id'], topic, storage_path,
                                         datetime_, record['geometry']).dumps()

    # load plugin for broker
    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': BROKER_PUBLIC,
        'client_type': 'publisher'
    }
    broker = load_plugin('pubsub', defs)

    broker.pub(topic, wis_message)
    LOGGER.info(f'Discovery metadata published to {topic}')

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
        'title_field': 'title',
    }


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
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    setup_collection(meta=gcm())

    click.echo(f'Publishing discovery metadata from {filepath.name}')
    try:
        dm = DiscoveryMetadata()
        record_mcf = dm.parse_record(filepath.read())

        if record_mcf['wis2box']['topic_hierarchy'] not in DATADIR_DATA_MAPPINGS['data']:  # noqa
            data_mappings_topics = '\n'.join(DATADIR_DATA_MAPPINGS['data'].keys())  # noqa
            msg = (f"topic_hierarchy={record_mcf['wis2box']['topic_hierarchy']} not found"  # noqa
                   f" in data-mappings:\n\n{data_mappings_topics}")
            raise click.ClickException(msg)

        record = dm.generate(record_mcf)

        data_bytes = json.dumps(record,
                                default=json_serial).encode('utf-8')
        storage_path = f"{STORAGE_SOURCE}/{STORAGE_PUBLIC}/metadata/{record['id']}.json"  # noqa

        put_data(data_bytes, storage_path)

        message = publish_broker_message(record, storage_path,
                                         record_mcf['wis2box']['country'],
                                         record_mcf['wis2box']['centre_id'])
        upsert_collection_item('discovery-metadata', record)
        upsert_collection_item('messages', json.loads(message))
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument('identifier')
@cli_helpers.OPTION_VERBOSITY
def unpublish(ctx, identifier, verbosity):
    """Deletes a discovery metadata record from the catalogue"""

    click.echo(f'Unpublishing discovery metadata {identifier}')
    try:
        delete_collection_item('discovery-metadata', identifier)
    except Exception:
        raise click.ClickException('Invalid metadata identifier')


discovery_metadata.add_command(publish)
discovery_metadata.add_command(setup)
discovery_metadata.add_command(unpublish)
