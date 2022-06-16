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
import json

import paho.mqtt.client as mqtt
import random

import sys
import time

from prometheus_client import start_http_server, Gauge, Counter

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


def sub_connect(client, userdata, flags, rc, properties=None):
    """
    function executed 'on_connect' for paho.mqtt.client
    subscribes to xpublic/#

    :param client: client-object associated to 'on_connect'
    :param userdata: userdata
    :param flags: flags
    :param rc: return-code received 'on_connect'
    :param properties: properties

    :returns: `None`
    """

    logger.info(f"received connack_string : {mqtt.connack_string(rc)}")
    for s in ["xpublic/#"]:
        client.subscribe(s, qos=1)


mqtt_msg_array = []


def sub_mqtt_metrics(client, userdata, msg):
    """
    function executed 'on_message' for paho.mqtt.client
    updates gauges for each new message received

    :param client: client-object associated to 'on_message'
    :param userdata: MQTT-userdata
    :param msg: MQTT-message-object received by subscriber

    :returns: `None`
    """
    logger.info(f"Received message on topic ={msg.topic}")
    global mqtt_msg_array
    # update msg-array
    msg_payload = json.loads(msg.payload.decode('utf-8'))
    rel_path = msg_payload['relPath']
    logger.info(f"rel_path={rel_path}")
    file_type = rel_path.split('.')[-1]
    topic_date = rel_path.split('/')[0].replace('-', '')
    wigos_id = ''
    if 'WIGOS_' in rel_path and topic_date in rel_path:
        wigos_id = rel_path.split('WIGOS_')[1].split('_'+topic_date)[0]
    if 'bufr' in file_type:
        mqtt_msg_array.append({'msg_time': time.time(),
                               'topic': msg.topic,
                               'wigos_id': wigos_id})


def gather_mqtt_metrics():
    """
    setup mqtt-client to monitor metrics from broker on this box

    :returns: `None`
    """
    # parse username and password out of the WIS2BOX_BROKER variable
    BROKER = os.environ.get('WIS2BOX_BROKER')

    # generate a random clientId for the mqtt-session
    r = random.Random()
    client_id = f"mqtt_metrics_collector_{r.randint(1,1000):04d}"
    logger.info(BROKER)
    try:
        broker_arr = BROKER.replace('mqtt://', '').split(':')
        logger.info(f"{broker_arr[0]}")
        mqtt_username = broker_arr[0]
        mqtt_pwd = str(broker_arr[1]).split('@')[0]
        mqtt_host = str(broker_arr[1]).split('@')[1]
        logger.info("setup connection")
        logger.info(f"host={mqtt_host}, user={mqtt_username}")
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        client.on_connect = sub_connect
        client.on_message = sub_mqtt_metrics
        client.username_pw_set(mqtt_username, mqtt_pwd)
        client.connect(mqtt_host)
        loop_forever = True
        # use a Gauge to measure number of messages per hour
        mqtt_msg_count_ph = Gauge(
            'mqtt_msg_per_hour',
            'Msg for bufr4 on xpublic per hour')
        # intialize gauge at 0
        mqtt_msg_count_ph.set(0)
        # Counter to measure total number of messages
        mqtt_msg_count_total = Counter(
            'mqtt_msg_total',
            'Msg for bufr4 on xpublic total')
        # Counter to measure total messages per wigos-id
        mqtt_msg_count_wsi_total = Counter(
            'mqtt_msg_wsi_total',
            'Msg for bufr4 on xpublic total, by WIGOS-ID',
            ["wigos_id"])
        global mqtt_msg_array
        mqtt_msg_array = []
        mqtt_msg_lasthour_array = []
        sleep_secs = 30
        while loop_forever:
            # start loop
            client.loop_start()
            # sleep while we collect messages
            logger.debug(f"Sleep for {sleep_secs} seconds ")
            time.sleep(sleep_secs)
            # take snapshot of messages in mqtt_msg_array
            mqtt_msg_snapshot = mqtt_msg_array[:]
            # reset array to receive new messages
            mqtt_msg_array = []
            logger.info(
                f"len(mqtt_msg_snapshot)={len(mqtt_msg_snapshot)}")
            # get reference time to prune messages dated more than 1 hour ago
            past = time.time() - 1*60*60  # 1 hour
            # prune old messages
            mqtt_msg_lasthour_array = [
                m for m in mqtt_msg_lasthour_array if m['msg_time'] >= past
            ]
            for msg in mqtt_msg_snapshot:
                # add msg of snapshot into lasthour_array
                mqtt_msg_lasthour_array.append(msg)
                # update counter per wigos_id
                mqtt_msg_count_wsi_total.labels(msg['wigos_id']).inc(1)
                # update total counter
                mqtt_msg_count_total.inc(1)
            # set per-hour gauge using length of lasthour_array
            mqtt_msg_count_ph.set(len(mqtt_msg_lasthour_array))
            # stop loop
            client.loop_stop()

    except Exception as e:
        logger.error(f"gather_mqtt_metrics() threw error: {e}")


def main():
    start_http_server(8001)
    gather_mqtt_metrics()


if __name__ == '__main__':
    main()
