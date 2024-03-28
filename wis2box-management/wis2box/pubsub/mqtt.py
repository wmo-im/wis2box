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
import random
import time

from typing import Any, Callable

from paho.mqtt import client as mqtt_client

from wis2box.pubsub.base import BasePubSubClient

LOGGER = logging.getLogger(__name__)


class MQTTPubSubClient(BasePubSubClient):
    """MQTT Pub/Sub client"""
    def __init__(self, broker: str) -> None:
        """
        Pub/Sub initializer

        :param broker: `str` of broker RFC1738 URL

        :returns: `None`
        """

        super().__init__(broker)
        self.type = 'mqtt'
        self._port = self.broker_url.port
        self.client_id = f"wis2box-mqtt-{self.broker['client_type']}-{random.randint(0, 1000)}"  # noqa

        msg = f'Connecting to broker {self.broker} with id {self.client_id}'
        LOGGER.debug(msg)
        self.conn = mqtt_client.Client(self.client_id)

        self.conn.enable_logger(logger=LOGGER)

        if None not in [self.broker_url.password, self.broker_url.password]:
            self.conn.username_pw_set(
                self.broker_url.username,
                self.broker_url.password)

        if self._port is None:
            if self.broker_url.scheme == 'mqtts':
                self._port = 8883
            else:
                self._port = 1883
        if self.broker_url.scheme == 'mqtts':
            self.conn.tls_set(tls_version=2)

        self.conn.connect(self.broker_url.hostname, self._port)
        LOGGER.debug('Connection initiated')

    def pub(self, topic: str, message: str, qos: int = 1) -> bool:
        """
        Publish a message to a broker/topic

        :param topic: `str` of topic
        :param message: `str` of message

        :returns: `bool` of publish result
        """

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                LOGGER.debug('connected to broker')
            else:
                msg = 'Failed to connect to MQTT-broker:'
                LOGGER.error(f'{msg} {mqtt_client.connack_string(rc)}')
        self.conn.on_connect = on_connect
        # allow 10 attempts to connect
        attempts = 0
        while not self.conn.is_connected() and attempts < 10:
            self.conn.loop()
            time.sleep(1.)
            attempts += 1
        # publish message, if connected
        if self.conn.is_connected():
            self.conn.publish(topic, message, qos)
            return True
        else:
            LOGGER.error(f'{self.client_id} failed to publish message')
            return False

    def sub(self, topic: str) -> None:
        """
        Subscribe to a broker/topic

        :param topic: `str` of topic

        :returns: `None`
        """

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                LOGGER.debug(f'Connected to broker {self.broker}')
                LOGGER.debug(f'Subscribing to topic {topic} ')
                client.subscribe(topic, qos=1)
                LOGGER.debug(f'Subscribed to topic {topic}')
            else:
                msg = 'Failed to connect to MQTT-broker:'
                LOGGER.error(f'{msg} {mqtt_client.connack_string(rc)}')

        def on_disconnect(client, userdata, rc):
            LOGGER.debug(f'Disconnected from {self.broker}')

        LOGGER.debug(f'Subscribing to broker {self.broker}, topic {topic}')
        self.conn.on_connect = on_connect
        self.conn.on_disconnect = on_disconnect
        self.conn.loop_forever()

    def bind(self, event: str, function: Callable[..., Any]) -> None:
        """
        Binds an event to a function

        :param event: `str` of event name
        :param function: Python callable

        :returns: `None`
        """

        setattr(self.conn, event, function)

    def __repr__(self):
        return '<MQTTPubSubClient>'
