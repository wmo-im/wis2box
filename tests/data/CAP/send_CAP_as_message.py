import base64
import json

import paho.mqtt.publish as publish

BROKER_USERNAME = 'cap_editor'
BROKER_PASSWORD = 'testing123'
BROKER_HOST = 'mosquitto'
BROKER_PORT = '1883'

filename = '/data/wis2box/CAP/example_20030618215700.xml'

# create a message containing the CAP alert in the data field as bade64 encoded bytes
data = base64.b64encode( open(filename, 'rb').read() ).decode()
msg = {
    'channel': 'int-wmo-test/data/core/weather/cap-alerts',
    'data': data,
    'filename': filename.split('/')[-1],
    '_meta': {
        'data_date': '2020-03-06T18:12:15.700'
    }
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