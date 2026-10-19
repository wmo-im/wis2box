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

import json
import os
import logging
from queue import Queue
import random
import sys
from threading import Thread
import time

import paho.mqtt.client as mqtt
from prometheus_client import (Counter, Gauge, PROCESS_COLLECTOR,
                               PLATFORM_COLLECTOR, REGISTRY,
                               start_http_server)
import requests

message_buffer = []

REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# remove python-gargage-collectior metrics
REGISTRY.unregister(
    REGISTRY._names_to_collectors['python_gc_objects_uncollectable_total'])

WIS2BOX_LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
# gotta log to stdout so docker logs sees the python-logs
logging.basicConfig(stream=sys.stdout)
# create our own LOGGER using same log-level as wis2box

LOGGER = logging.getLogger('mqtt_metrics_collector')
LOGGER.setLevel(WIS2BOX_LOGGING_LOGLEVEL)

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


class MetricsCollector:
    def __init__(self):
        """
        Initializes a message queue for thread-safe message handling.
        """
        self.message_queue = Queue()
        self.running = True

    def update_stations_gauge(self, station_list):
        """
        function to update the stations-gauge

        :param station_list: list of stations

        :returns: `None`
        """

        print(f"update stations-gauge with: {station_list}")

        station_wsi._metrics.clear()
        for station in station_list:
            station_wsi.labels(station).set(1)
            notify_wsi_total.labels(station).inc(0)
            failure_wsi_total.labels(station).inc(0)

    def init_stations_gauge(self):
        """
        function to initialize the stations-gauge

        :returns: `None`
        """

        station_list = []
        url = 'http://wis2box-api:80/oapi/collections/stations/items?f=json'
        station_list_found = False
        while station_list_found is False:
            try:
                res = requests.get(url)
                json_data = json.loads(res.content)
                if 'description' in json_data:
                    if json_data['description'] == 'Collection not found':
                        LOGGER.warning("Station collection not (yet) found in wis2box-api, sleep and try again") # noqa
                        time.sleep(1)
                    else:
                        msg = f' wis2box-api returned unexpected response: {json_data}' # noqa
                        raise Exception(msg)
                else:
                    station_list_found = True
                    station_list = [item['id'] for item in json_data["features"]] # noqa
            except Exception as err:
                msg = f'Failed to get stations from wis2box-api, with error: {err}' # noqa
                raise Exception(msg)
        self.update_stations_gauge(station_list)

    def sub_connect(self, client, userdata, flags, reason_code, properties):
        """
        function executed 'on_connect' for paho.mqtt.client

        :param client: client-object associated to 'on_connect'
        :param userdata: userdata
        :param flags: flags
        :param reason_code: return-code received 'on_connect'
        :param properties: properties

        :returns: `None`
        """

        msg = f"on connection to subscribe: {mqtt.connack_string(reason_code)}"
        LOGGER.info(msg)
        for s in ["wis2box/#", '$SYS/broker/messages/#']:
            client.subscribe(s, qos=1)

    def sub_mqtt_metrics(self, client, userdata, msg):
        """
        function executed 'on_message' for paho.mqtt.client
        updates counters for each new message received

        :param client: client-object associated to 'on_message'
        :param userdata: MQTT-userdata
        :param msg: MQTT-message-object received by subscriber

        :returns: `None`
        """

        LOGGER.debug(f"Received message on topic={msg.topic}")

        if msg.topic.startswith('$SYS/broker/messages/'):
            if msg.topic.endswith('/sent'):
                broker_msg_sent.set(float(msg.payload))
            elif msg.topic.endswith('/received'):
                broker_msg_received.set(float(msg.payload))
            elif msg.topic.endswith('/stored'):
                broker_msg_stored.set(float(msg.payload))
            elif msg.topic.endswith('/dropped'):
                broker_msg_dropped.set(float(msg.payload))
        else:
            self.message_queue.put((msg.topic, msg.payload))

    def process_buffered_messages(self):
        """
        Processes buffered messages in a separate thread.
        """
        while self.running:
            topic, payload = self.message_queue.get()
            try:
                m = json.loads(payload.decode('utf-8'))
                if topic.startswith('wis2box/stations'):
                    self.update_stations_gauge(m['station_list'])
                elif topic.startswith('wis2box/notifications'):
                    wsi = m['properties'].get('wigos_station_identifier', 'none') # noqa
                    if (wsi,) not in notify_wsi_total._metrics:
                        LOGGER.warning(f"New station detected: {wsi}, init metrics") # noqa
                        station_wsi.labels(wsi).set(1)
                        notify_wsi_total.labels(wsi).inc(0)
                        failure_wsi_total.labels(wsi).inc(0)
                        # give prometheus time to register the new metric
                        time.sleep(5)
                    station_wsi.labels(wsi).set(1)
                    notify_wsi_total.labels(wsi).inc(1)
                    failure_wsi_total.labels(wsi).inc(0)
                    notify_total.inc(1)
                elif topic.startswith('wis2box/failure'):
                    wsi = m.get('wigos_station_identifier', 'none')
                    notify_wsi_total.labels(wsi).inc(0)
                    failure_wsi_total.labels(wsi).inc(1)
                    failure_total.inc(1)
                elif topic.startswith('wis2box/storage'):
                    if str(m["Key"]).startswith('wis2box-incoming'):
                        storage_incoming_total.inc(1)
                    if str(m["Key"]).startswith('wis2box-public'):
                        storage_public_total.inc(1)
            except Exception as e:
                logging.error(f"Error processing message: {e}")

    def gather_mqtt_metrics(self):
        """
        setup mqtt-client to monitor metrics from broker on this box

        :returns: `None`
        """

        broker_host = os.environ.get('WIS2BOX_BROKER_HOST', '')
        broker_username = os.environ.get('WIS2BOX_BROKER_USERNAME', '')
        broker_password = os.environ.get('WIS2BOX_BROKER_PASSWORD', '')
        broker_port = int(os.environ.get('WIS2BOX_BROKER_PORT', '1883'))

        r = random.Random()
        client_id = f"mqtt_metrics_collector_{r.randint(1, 1000):04d}"
        try:
            LOGGER.info(f"setup connection: host={broker_host}, user={broker_username}") # noqa
            client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id, protocol=mqtt.MQTTv5)

            client.on_connect = self.sub_connect
            client.on_message = self.sub_mqtt_metrics
            client.username_pw_set(broker_username, broker_password)
            client.connect(broker_host, broker_port)
            print("Connected to broker, start MQTT-loop")
            client.loop_start()  # Start MQTT loop in background
        except Exception as err:
            LOGGER.error(f"Failed to setup MQTT-client with error: {err}")

    def start(self):
        """
        Starts the metrics collection by initializing components and threads.
        """
        self.init_stations_gauge()
        Thread(target=self.process_buffered_messages, daemon=True).start()
        self.gather_mqtt_metrics()


def main():
    """
    Entry point for the script.
    """
    start_http_server(8001)
    collector = MetricsCollector()
    collector.start()
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
