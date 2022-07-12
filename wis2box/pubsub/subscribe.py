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

import logging

import click

from wis2box import cli_helpers
from wis2box.env import BROKER
from wis2box.handler import Handler
from wis2box.plugin import load_plugin, PLUGINS

LOGGER = logging.getLogger(__name__)


def on_message_handler(client, userdata, msg):
    print(msg)
    #filepath = json.loads(msg.payload)['filepath']
    #handler = Handler(filepath)


@click.command()
@click.pass_context
@click.option('--broker', '-b', help='URL to broker')
@click.option('--topic', '-t', help='topic to subscribe to')
@cli_helpers.OPTION_VERBOSITY
def subscribe(ctx, broker, topic, verbosity):
    """Subscribe to a broker/topic"""
    click.echo(f'Subscribing to broker {broker}, topic {topic}')

    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': BROKER
    }

    broker = load_plugin('pubsub', defs)

    broker.bind('on_message', on_message_handler)

    broker.sub(topic)
