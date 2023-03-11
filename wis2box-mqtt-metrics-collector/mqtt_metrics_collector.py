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

import requests

import paho.mqtt.client as mqtt
import random

import sys
import json

from prometheus_client import start_http_server, Counter, Gauge

# de-register default-collectors
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

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

notify_total = Counter('wis2box_notify_total',
                       'Total notifications sent by wis2box')
notify_wsi_total = Counter('wis2box_notify_wsi_total',
                                 'Total notifications sent by wis2box, by WSI', # noqa
                                 ["WSI"])

failure_total = Counter('wis2box_failure_total',
                        'Total failed actions reported by wis2box')
failure_descr_wsi_total = Counter('wis2box_failure_descr_wsi_total',
                                    'Total failed actions sent by wis2box, by description and WSI', # noqa
                                    ["description", "WSI"])
failure_wsi_total = Counter('wis2box_failure_wsi_total',
                                    'Total failed actions sent by wis2box, by WSI', # noqa
                                    ["WSI"])

storage_incoming_total = Counter('wis2box_storage_incoming_total',
                                 'Total storage notifications received on incoming') # noqa
storage_public_total = Counter('wis2box_storage_public_total',
                               'Total storage notifications received on public') # noqa

broker_msg_sent = Gauge('wis2box_broker_msg_sent',
                        '$SYS/messages/sent')
broker_msg_received = Gauge('wis2box_broker_msg_received',
                            '$SYS/messages/received')
broker_msg_stored = Gauge('wis2box_broker_msg_stored',
                          '$SYS/messages/stored')
broker_msg_dropped = Gauge('wis2box_broker_msg_dropped',
                           '$SYS/messages/dropped')

station_wsi = Gauge('wis2box_stations_wsi',
                    'wis2box configured stations by WSI',
                    ["WSI"])


def update_stations_gauge(station_list):
    station_wsi._metrics.clear()
    for station in station_list:
        station_wsi.labels(station).set(1)
        notify_wsi_total.labels(station).inc(0)
        failure_wsi_total.labels(station).inc(0)


def init_stations_gauge():
    station_list = []
    # read currently configured stations from wis2box-api
    url = 'http://wis2box-api:80/oapi/collections/stations/items?f=json'
    res = requests.get(url)
    try:
        json_data = json.loads(res.content)
        if 'description' in json_data:
            if json_data['description'] == 'Collection not found':
                logger.error("No stations configured yet")
                station_list.append('none') # placeholder to init series
            else:
                logger.error(json_data['description'])
        else:
            for item in json_data["features"]:
                station_list.append(item['id'])
    except Exception as err:
        logger.error(f'Failed to update stations-gauge: {err}')
    update_stations_gauge(station_list)


def sub_connect(client, userdata, flags, rc, properties=None):
    """
    function executed 'on_connect' for paho.mqtt.client

    :param client: client-object associated to 'on_connect'
    :param userdata: userdata
    :param flags: flags
    :param rc: return-code received 'on_connect'
    :param properties: properties

    :returns: `None`
    """

    logger.info(f"on connection to subscribe: {mqtt.connack_string(rc)}")
    for s in ["wis2box/#", "wis2box-storage/#", '$SYS/broker/messages/#']:
        print(f'subscribe to: {s}')
        client.subscribe(s, qos=0)


def sub_mqtt_metrics(client, userdata, msg):
    """
    function executed 'on_message' for paho.mqtt.client
    updates counters for each new message received

    :param client: client-object associated to 'on_message'
    :param userdata: MQTT-userdata
    :param msg: MQTT-message-object received by subscriber

    :returns: `None`
    """

    logger.debug(f"Received message on topic={msg.topic}")

    if str(msg.topic).startswith('$SYS/broker/messages/sent'):
        broker_msg_sent.set(msg.payload)
    elif str(msg.topic).startswith('$SYS/broker/messages/received'):
        broker_msg_received.set(msg.payload)
    elif str(msg.topic).startswith('$SYS/broker/messages/stored'):
        broker_msg_received.set(msg.payload)
    elif str(msg.topic).startswith('$SYS/broker/messages/dropped'):
        broker_msg_received.set(msg.payload)

    if str(msg.topic).startswith('$SYS'):
        return

    m = json.loads(msg.payload.decode('utf-8'))
    if str(msg.topic).startswith('wis2box/stations'):
        update_stations_gauge(m['station_list'])
    elif str(msg.topic).startswith('wis2box/notifications'):
        notify_wsi_total.labels(
            m['wigos_station_identifier']).inc(1)
        notify_total.inc(1)
    elif str(msg.topic).startswith('wis2box/failure'):
        descr = m['description']
        wsi = 'none'
        if 'wigos_station_identifier' in m:
            wsi = m['wigos_station_identifier']
        failure_descr_wsi_total.labels(descr, wsi).inc(1)
        failure_wsi_total.labels(wsi).inc(1)
        failure_total.inc(1)
    elif str(msg.topic).startswith('wis2box-storage'):
        if str(m["Key"]).startswith('wis2box-incoming'):
            storage_incoming_total.inc(1)
        if str(m["Key"]).startswith('wis2box-public'):
            storage_public_total.inc(1)


def gather_mqtt_metrics():
    """
    setup mqtt-client to monitor metrics from broker on this box

    :returns: `None`
    """

    # connect to the internal broker
    broker_host = os.environ.get('WIS2BOX_BROKER_HOST', '')
    broker_username = os.environ.get('WIS2BOX_BROKER_USERNAME', '')
    broker_password = os.environ.get('WIS2BOX_BROKER_PASSWORD', '')
    broker_port = int(os.environ.get('WIS2BOX_BROKER_PORT', '1883'))

    # generate a random clientId for the mqtt-session
    r = random.Random()
    client_id = f"mqtt_metrics_collector_{r.randint(1,1000):04d}"
    try:
        logger.info("setup connection")
        logger.info(f"host={broker_host}, user={broker_username}")
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        client.on_connect = sub_connect
        client.on_message = sub_mqtt_metrics
        client.username_pw_set(broker_username, broker_password)
        client.connect(broker_host, broker_port)
        client.loop_forever()
    except Exception as err:
        logger.error(f"Failed to setup MQTT-client with error: {err}")


def main():
    start_http_server(8001)
    init_stations_gauge()
    gather_mqtt_metrics()


if __name__ == '__main__':
    main()
