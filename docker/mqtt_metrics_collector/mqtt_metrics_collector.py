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

from prometheus_client import start_http_server, Counter

# de-register default-collectors
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# remove python-gargage-collectior metrics
REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_uncollectable_total'])
#REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])

import logging

from base64 import b64decode
import json
import paho.mqtt.client as mqtt
import random
import urllib
import urllib.request

import sys

WIS2BOX_LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
# gotta log to stdout so docker logs sees the python-logs
logging.basicConfig(stream=sys.stdout)
# create our own logger using same log-level as wis2box
logger = logging.getLogger('mqtt_metrics_collector')
logger.setLevel(WIS2BOX_LOGGING_LOGLEVEL)

INTERRUPT = False

def sub_connect(client, userdata, flags, rc, properties=None):
    logger.info("on connection to subscribe:", mqtt.connack_string(rc))
    for s in ["xpublic/#"]:
        client.subscribe(s, qos=1)

mqtt_msg_counter = Counter('mqtt_msg_count', 'Number of messages seen on MQTT')
mqtt_msg_by_topic_counter = Counter('mqtt_msg_count_by_topic', 'Number of messages seen on MQTT, by topic', ["topic"])

def sub_mqtt_metrics(client, userdata, msg):
    """
      subscribe and update MQTT metrics for each new message received
    """
    m = json.loads(msg.payload.decode('utf-8'))
    logger.info(f"Received message on topic ={msg.topic}")
    mqtt_msg_by_topic_counter.labels(msg.topic).inc(1)
    mqtt_msg_counter.inc(1)

def gather_mqtt_metrics():
    """
      setup mqtt-client to monitor metrics from broker on this box
    """
    # explicitly set the counter to 0 at the start
    mqtt_msg_counter.inc(0)

    # parse username and password out of the WIS2BOX_BROKER variable
    BROKER = os.environ.get('WIS2BOX_BROKER')
    
    # generate a random clientId for the mqtt-session
    r = random.Random()
    client_id = f"mqtt_metrics_collector_{r.randint(1,1000):04d}"
    logger.info(f"{BROKER}")
    try:
        broker_arr = BROKER.replace('mqtt://','').split(':')
        logger.info(f"{broker_arr[0]}")
        mqtt_username = broker_arr[0]
        mqtt_pwd = str( broker_arr[1] ).split('@')[0]
        mqtt_host = str( broker_arr[1] ).split('@')[1]
        logger.info(f"setup mqtt-client-connection mqtt_host={mqtt_host}, mqtt_username={mqtt_username}, mqtt_pwd={mqtt_pwd}, client_id={client_id} ")
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        client.on_connect = sub_connect
        client.on_message = sub_mqtt_metrics
        client.username_pw_set(mqtt_username, mqtt_pwd)
        client.connect(mqtt_host)
        client.loop_forever()
    except Exception as e:
        logger.error(f"Failed to setup MQTT-client with error: {e}")

def main():
    start_http_server(8001)
    gather_mqtt_metrics()

if __name__ == '__main__':
    main()

