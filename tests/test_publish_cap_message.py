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

import base64
import json

import paho.mqtt.publish as publish

BROKER_USERNAME = 'wis2box'
BROKER_PASSWORD = 'wis2box'
BROKER_HOST = 'localhost'
BROKER_PORT = '1883'

filename = 'tests/data/CAP/sc_example.xml'

# create a message containing the CAP alert in
#  the data field as base64 encoded bytes
with open(filename, 'rb') as file:
    data = base64.b64encode(file.read()).decode()

msg = {
    'metadata_id': 'urn:wmo:md:int_wmo_test:cap',
    'data': data,
    'filename': filename.split('/')[-1]
}
# publish notification on internal broker
private_auth = {
    'username': BROKER_USERNAME,
    'password': BROKER_PASSWORD
}
publish.single(topic='wis2box/cap/publication',
               payload=json.dumps(msg),
               qos=1,
               retain=False,
               hostname=BROKER_HOST,
               port=int(BROKER_PORT),
               auth=private_auth)
