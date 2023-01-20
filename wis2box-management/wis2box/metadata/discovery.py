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
import json
import logging

from pygeometa.schemas.wmo_wcmp2 import WMOWCMP2OutputSchema

from wis2box import cli_helpers
from wis2box.api import (setup_collection, upsert_collection_item,
                         delete_collection_item)
from wis2box.env import API_URL, BROKER_PUBLIC
from wis2box.metadata.base import BaseMetadata
from wis2box.plugin import load_plugin, PLUGINS
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

        LOGGER.debug('Adding topic hierarchy as keyword')
        topic_hierarchy_keywords = {
            'keywords': [mcf['wis2box']['topic_hierarchy']],
            'keywords_type': 'theme',
            'vocabulary': {
                'name': 'WMO Core Metadata profile topic hierarchy',
                'url': 'https://github.com/wmo-im/wis2-topic-hierarchy'
            }
        }

        md['identification']['keywords']['wis2'] = topic_hierarchy_keywords

        LOGGER.debug('Adding distribution links')
        oafeat_link = {
            'url': f"{API_URL}/collections/{identifier}",
            'type': 'OAFeat',
            'name': identifier,
            'description': identifier,
            'rel': 'collection'
        }

        mqp_link = {
            'url': remove_auth_from_url(BROKER_PUBLIC),
            'type': 'MQTT',
            'name': mcf['wis2box']['topic_hierarchy'],
            'description': mcf['wis2box']['topic_hierarchy'],
            'rel': 'data',
            'wmo_topic': mqtt_topic
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

        anytext_bag = [
            md['identification']['title'],
            md['identification']['abstract']
        ]

        for k, v in md['identification']['keywords'].items():
            anytext_bag.extend(v['keywords'])

        record['properties']['_metadata-anytext'] = ' '.join(anytext_bag)

        return record


def publish_broker_message(record, country: str, centre_id: str) -> bool:
    """
    Publish discovery metadata to broker

    :param record: `dict` of discovery metadata record
    :param country: ISO 3166 alpha 3
    :param centre_id: centre acronym

    :returns: `bool` of publish result
    """

    topic = f'origin/a/wis2/{country.lower()}/{centre_id.lower()}/metadata'  # noqa

    # load plugin for broker
    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': BROKER_PUBLIC,
        'client_type': 'publisher'
    }
    broker = load_plugin('pubsub', defs)

    broker.pub(topic, json.dumps(record, default=json_serial))
    LOGGER.info(f'Discovery metadata published to {topic}')


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
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    setup_collection(meta=gcm())

    click.echo(f'Publishing discovery metadata from {filepath.name}')
    try:
        dm = DiscoveryMetadata()
        record_mcf = dm.parse_record(filepath.read())
        record = dm.generate(record_mcf)
        publish_broker_message(record, record_mcf['wis2box']['country'],
                               record_mcf['wis2box']['centre_id'])
        upsert_collection_item('discovery-metadata', record)
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
    delete_collection_item('discovery-metadata', identifier)


discovery_metadata.add_command(publish)
discovery_metadata.add_command(unpublish)
