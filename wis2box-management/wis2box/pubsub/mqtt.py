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

from time import sleep
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
        self.test_status = 'unknown'
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

        LOGGER.debug(f'Publishing to broker {self.broker}')
        LOGGER.debug(f'Topic: {topic}')
        LOGGER.debug(f'Message: {message}')

        self.conn.loop_start()
        result = self.conn.publish(topic, message, qos)
        self.conn.loop_stop()

        # TODO: investigate implication
        # result.wait_for_publish()

        if result.is_published:
            return True
        else:
            msg = f'Publishing error code: {result[1]}'
            LOGGER.warning(msg)
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

    def test(self, topic='wis2box/test', message='test') -> bool:
        """
        Test the connection to the broker

        :returns: `bool` of test result
        """

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                LOGGER.debug(f'Test: Connected to broker {self.broker}')
                client.subscribe(topic, qos=1)
                LOGGER.debug(f'Test: Subscribed to topic {topic}')
            else:
                msg = f'Test: Failed to connect to MQTT-broker: {mqtt_client.connack_string(rc)}' # noqa
                LOGGER.error(msg)
        
        def on_message(client, userdata, message):
            LOGGER.debug(f'Test: Received message {message.payload.decode()}')
            self.test_status = 'success'

        self.conn.on_connect = on_connect
        self.conn.on_message = on_message
    
        self.conn.loop_start()
        sleep(0.1)
        self.conn.publish(topic, message, qos=1)
        sleep(0.1)
        self.conn.loop_stop()

        return self.test_status == 'success'

    def __repr__(self):
        return '<MQTTPubSubClient>'
