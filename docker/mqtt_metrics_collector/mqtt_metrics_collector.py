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

import os
import logging

import paho.mqtt.client as mqtt
import random

from urllib.parse import urlparse

import sys

from prometheus_client import start_http_server, Counter

# de-register default-collectors
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

__version__ = '0.5.0'

REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# remove python-gargage-collectior metrics
REGISTRY.unregister(
    REGISTRY._names_to_collectors['python_gc_objects_uncollectable_total'])


WIS2BOX_LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
# gotta log to stdout so docker logs sees the python-logs
logging.basicConfig(stream=sys.stdout)
# create our own logger using same log-level as wis2box
logger = logging.getLogger('mqtt_metrics_collector')
logger.setLevel(WIS2BOX_LOGGING_LOGLEVEL)

INTERRUPT = False


def sub_connect(client, userdata, flags, rc, properties=None):
    """
    function executed 'on_connect' for paho.mqtt.client
    subscribes to origin/#

    :param client: client-object associated to 'on_connect'
    :param userdata: userdata
    :param flags: flags
    :param rc: return-code received 'on_connect'
    :param properties: properties

    :returns: `None`
    """

    logger.info(f"on connection to subscribe: {mqtt.connack_string(rc)}")
    for s in ["origin/#"]:
        client.subscribe(s, qos=1)


mqtt_msg_counter = Counter('mqtt_msg_count',
                           'Nr of messages seen on MQTT')
mqtt_msg_topic_counter = Counter('mqtt_msg_count_topic',
                                 'Nr of messages seen on MQTT, by topic',
                                 ["topic"])


def sub_mqtt_metrics(client, userdata, msg):
    """
    function executed 'on_message' for paho.mqtt.client
    updates counters for each new message received

    :param client: client-object associated to 'on_message'
    :param userdata: MQTT-userdata
    :param msg: MQTT-message-object received by subscriber

    :returns: `None`
    """
    # m = json.loads(msg.payload.decode('utf-8'))
    logger.info(f"Received message on topic ={msg.topic}")
    mqtt_msg_topic_counter.labels(msg.topic).inc(1)
    mqtt_msg_counter.inc(1)


def gather_mqtt_metrics():
    """
    setup mqtt-client to monitor metrics from broker on this box

    :returns: `None`
    """
    # explicitly set the counter to 0 at the start
    mqtt_msg_counter.inc(0)

    broker_url = urlparse(os.environ.get('WIS2BOX_BROKER_PUBLIC', ''))

    # generate a random clientId for the mqtt-session
    r = random.Random()
    client_id = f"mqtt_metrics_collector_{r.randint(1,1000):04d}"
    try:
        logger.info("setup connection")
        logger.info(f"host={broker_url.hostname}, user={broker_url.username}")
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        client.on_connect = sub_connect
        client.on_message = sub_mqtt_metrics
        client.username_pw_set(broker_url.username, broker_url.password)
        _port = broker_url.port
        if _port is None:
            if broker_url.scheme == 'mqtts':
                _port = 8883
            else:
                _port = 1883
        if broker_url.scheme == 'mqtts':
            client.tls_set(tls_version=2)
        client.connect(broker_url.hostname, _port)
        client.loop_forever()
    except Exception as e:
        logger.error(f"Failed to setup MQTT-client with error: {e}")


def main():
    start_http_server(8001)
    gather_mqtt_metrics()


if __name__ == '__main__':
    main()
