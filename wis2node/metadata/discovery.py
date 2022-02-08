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
import logging

from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema

from wis2node import cli_helpers
from wis2node.api.backend import load_backend
from wis2node.api.config import load_config
from wis2node.env import API_URL, MQP_URL
from wis2node.metadata.base import BaseMetadata

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

        LOGGER.debug('Adding distribution links')
        oafeat_link = {
            'url': f"{API_URL}/collections/{identifier}",
            'type': 'OAFeat',
            'name': identifier,
            'description': identifier,
            'function': 'collection'
        }

        mqp_link = {
            'url': MQP_URL,
            'type': 'MQTT',
            'name': identifier,
            'description': identifier,
            'function': 'collection'
        }

        md['distribution'] = {
            'oafeat': oafeat_link,
            'mqtt': mqp_link
        }

        LOGGER.debug('Generating OARec discovery metadata')
        record = OGCAPIRecordOutputSchema().write(md, stringify=False)

        anytext_bag = [
            md['identification']['title']['en'],
            md['identification']['abstract']['en']
        ]

        for k, v in md['identification']['keywords'].items():
            anytext_bag.extend(v['keywords']['en'])

        record['properties']['_metadata-anytext'] = ' '.join(anytext_bag)

        LOGGER.debug('Adding canonical link')
        canonical_link = {
            'url': f"{API_URL}/collections/discovery-metadata/{identifier}",
            'type': 'OARec',
            'name': identifier,
            'description': identifier,
            'function': 'canonical'
        }
        record['links'].append(canonical_link)

        return record


def publish_collection() -> bool:
    """
    Publish discovery metadata collection

    :returns: `bool` of publish result
    """

    LOGGER.debug('Adding to API configuration')

    collection = {
        'id': 'discovery-metadata',
        'type': 'record',
        'title': 'Discovery metadata',
        'description': 'Discovery metadata',
        'keywords': ['wmo', 'wis 2.0'],
        'links': ['https://example.org'],
        'bbox': [-180, -90, 180, 90],
        'id_field': 'identifier',
        'time_field': 'recordCreated',
        'title_field': 'title',
    }

    api_config = load_config()
    api_config.add_collection(collection)

    return True


@click.group('discovery')
def discovery2():
    """Discovery metadata management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    click.echo(f'Publishing discovery metadata from {filepath.name}')
    try:
        dm = DiscoveryMetadata()
        record = dm.parse_record(filepath.read())
        record = dm.generate(record)
        backend = load_backend()
        backend.upsert_collection_items('discovery-metadata', [record])
        publish_collection()
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument('identifier')
@cli_helpers.OPTION_VERBOSITY
def unpublish(ctx, identifier, verbosity):
    """Deletes a discovery metadata record from the catalogue"""

    click.echo('Unpublishing discovery metadata {identifier}')
    backend = load_backend()
    backend.delete_collection_item('discovery-metadata', identifier)


discovery2.add_command(publish)
discovery2.add_command(unpublish)
