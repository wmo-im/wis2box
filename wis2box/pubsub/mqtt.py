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
from typing import Any, Callable

from paho.mqtt import client as mqtt_client

from wis2box.pubsub.base import BasePubSubClient

LOGGER = logging.getLogger(__name__)


class MQTTPubSubClient(BasePubSubClient):
    """MQTT PubSub client"""
    def __init__(self, broker: str) -> None:
        """
        PubSub initializer

        :param broker: `str` of broker RFC1738 URL

        :returns: `None`
        """

        super().__init__(broker)
        self.type = 'mqtt'
        self._port = self.broker_url.port

        self.client_id = f'wis2box-mqtt-{random.randint(0, 1000)}'
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

        self.conn.connect(self.broker_url.hostname, self._port)
        LOGGER.debug('Connected to broker')

    def pub(self, topic: str, message: str) -> bool:
        """
        Publish a message to a broker/topic

        :param topic: `str` of topic
        :param message: `str` of message

        :returns: `bool` of publish result
        """

        LOGGER.debug(f'Publishing to broker {self.broker}')
        LOGGER.debug(f'Topic: {topic}')
        LOGGER.debug(f'Message: {message}')

        result = self.conn.publish(topic, message)

        result.wait_for_publish()

        if result.is_published:
            return True
        else:
            msg = 'Publishing error code: {result[1]}'
            LOGGER.warning(msg)
            return False

    def sub(self, topic: str) -> None:
        """
        Subscribe to a broker/topic

        :param topic: `str` of topic

        :returns: `None`
        """
        def on_connect(client, userdata, flags, rc):
            client.subscribe(topic)

        LOGGER.debug(f'Subscribing to broker {self.broker}')
        self.conn.on_connect = on_connect
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
