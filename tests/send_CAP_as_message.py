import base64
import json

import paho.mqtt.publish as publish

BROKER_USERNAME = 'wis2box'
BROKER_PASSWORD = 'wis2box'
BROKER_HOST = 'localhost'
BROKER_PORT = '1883'

filename = 'tests/data/CAP/sc_example.xml'

# create a message containing the CAP alert in the data field as bade64 encoded bytes
data = base64.b64encode( open(filename, 'rb').read() ).decode()
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