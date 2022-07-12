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

from datetime import datetime
import logging
from pathlib import Path

from urllib.parse import urlparse

import click

import random

import json

import paho.mqtt.client as mqtt

from wis2box import cli_helpers
from wis2box.handler import Handler
from wis2box.env import BROKER

TOPIC_BASE = 'xlocal/v03'

LOGGER = logging.getLogger(__name__)


class NotMQTTException(Exception):
    """Raised when schema provided by broker-url is not mqtt or mqtts"""
    pass


def sub_connect(client, userdata, flags, rc, properties=None):
    """
    function executed 'on_connect' for paho.mqtt.client
    subscribes to topic contain information from storage-layer

    :param client: client-object associated to 'on_connect'
    :param userdata: userdata
    :param flags: flags
    :param rc: return-code received 'on_connect'
    :param properties: properties

    :returns: `None`
    """

    LOGGER.info(f"on connection to subscribe: {mqtt.connack_string(rc)}")
    client.subscribe('wis2box-storage/#', qos=1)


def sub_on_message(client, userdata, msg):
    """
    function executed 'on_message' for paho.mqtt.client
    to be used on message published by storage-layer
    run handler on filepath

    :param client: client-object associated to 'on_message'
    :param userdata: MQTT-userdata
    :param msg: MQTT-message-object received by subscriber

    :returns: `None`
    """
    LOGGER.info(f"Received message on topic={msg.topic}")
    msg_payload = json.loads(msg.payload.decode('utf-8'))
    LOGGER.debug(f"MSG-payload: {msg_payload}")
    
    filepath = None
    if 'EventName' in msg_payload and msg_payload['EventName'] == 's3:ObjectCreated:Put':
        from wis2box.env import STORAGE_SOURCE
        filepath = STORAGE_SOURCE+'/'+msg_payload['Key']
    elif 'relPath' in msg_payload:
        filepath = msg_payload['relPath']
    else:
        LOGGER.warning('message ayload could not be parsed')

    try:
        LOGGER.info(f'Processing {filepath}')
        handler = Handler(filepath)
        if handler.handle():
            LOGGER.info('Data processed')
            for filepath_out in handler.plugin.files():
                LOGGER.info(f'Public filepath: {filepath_out}')
    except ValueError as err:
        msg = f'handle() error: {err}'
        LOGGER.error(msg)
    except Exception as err:
        msg = f'handle() error: {err}'
        raise err


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def watch(ctx, verbosity):
    """ wis2box data watch
        starts mqtt_client subscribed to minio-events
    """
    click.echo("Starting wis2box-subscriber")
    # check if BROKER is an MQTT-connection-string before starting
    broker_url = urlparse(BROKER)
    mqtt_port = 1883
    if broker_url.scheme == 'mqtts':
        mqtt_port = 8883
    elif broker_url.scheme != 'mqtt':
        raise NotMQTTException
    # create random client-id for this subscriber
    rand_int = random.Random().randint(1, 1000)
    client_id = f"wisbox-subscriber-{rand_int:04d}"
    mqtt_client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
    mqtt_client.on_connect = sub_connect
    mqtt_client.on_message = sub_on_message
    mqtt_client.username_pw_set(broker_url.username, broker_url.password)
    mqtt_client.connect(broker_url.hostname, mqtt_port)
    # loop_forever run until interrupted by user
    mqtt_client.loop_forever()
