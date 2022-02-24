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

from base64 import b64decode
import json
import paho.mqtt.client as mqtt
import random
import urllib
import urllib.request

host = 'localhost'
user = 'wis2box'
password = 'wis2box'

r = random.Random()
clientId = f"{__name__}_{r.randint(1,1000):04d}"
messageCount = 0
messageCountMaximum = 5


def sub_connect(client, userdata, flags, rc, properties=None):
    print("on connection to subscribe:", mqtt.connack_string(rc))
    for s in ["xpublic/#"]:
        client.subscribe(s, qos=1)


def sub_message_content(client, userdata, msg):
    """
      print messages received.  Exit on count received.
    """
    global messageCount, messageCountMaximum

    m = json.loads(msg.payload.decode('utf-8'))
    print(f"message {messageCount} topic: {msg.topic} received: {m}")
    print(f"message {messageCount} data: {getData(m)}")
    messageCount += 1
    if messageCount > messageCountMaximum:
        client.disconnect()
        client.loop_stop()


def getData(m, sizeMaximum=1000):
    """
      given a message, return the data it refers to
    """
    if 'size' in m and m['size'] > sizeMaximum:
        return f" data too large {m['size']} bytes"
    elif 'content' in m:
        if m['content']['encoding'] == 'base64':
            return b64decode(m['content']['value'])
        else:
            return m['content']['value'].encode('utf-8')
    else:
        url = m['baseUrl'] + '/' + m['relPath']
        with urllib.request.urlopen(url) as response:
            return response.read()


client = mqtt.Client(client_id=clientId, protocol=mqtt.MQTTv5)
client.on_connect = sub_connect
client.on_message = sub_message_content
client.username_pw_set(user, password)
client.connect(host)

client.loop_forever()
