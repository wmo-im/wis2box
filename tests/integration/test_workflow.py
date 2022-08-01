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


# integration tests assume that the workflow in
# .github/workflows/tests-docker.yml has been executed

import csv
from pathlib import Path

from requests import Session, codes

DATADIR = Path('.').parent.absolute() / 'tests/data'

URL = 'http://localhost:8999'
API_URL = f'{URL}/oapi'
SESSION = Session()


def test_metadata_station_cache():
    """Test station metadata caching"""

    with (DATADIR / 'metadata/station/station_list.csv').open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            wsi = row['wigos_station_identifier']
            path = DATADIR / 'metadata' / 'station' / f'{wsi}.json'
            assert path.exists()


def test_metadata_station_publish():
    """Test discovery metadata publishing"""

    r = SESSION.get(f'{API_URL}/collections/stations/items')

    assert r.status_code == codes.ok

    stations = r.json()

    assert len(stations['features']) == 7
    assert stations['numberReturned'] == 7
    assert stations['numberMatched'] == 7


def test_metadata_discovery_publish():
    """Test discovery metadata publishing"""

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items').json()
    assert r['numberMatched'] == 3

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items/data.core.observations-surface-land.mw.FWCL.landFixed').json()  # noqa

    assert r['id'] == 'data.core.observations-surface-land.mw.FWCL.landFixed'
    assert r['properties']['title'] == 'Surface weather observations (hourly)'

    assert len(r['links']) == 7

    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [32.6881653175, -16.8012997372],
            [32.6881653175, -9.23059905359],
            [35.7719047381, -9.23059905359],
            [35.7719047381, -16.8012997372],
            [32.6881653175, -16.8012997372]
        ]]
    }

    assert r['geometry'] == geometry

    params = {
        'q': 'temperature'
    }

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items',
                    params=params).json()

    assert r['numberMatched'] == 3


def test_data_ingest():
    """Test data ingest/process publish"""

    item = '2021-07-07/wis/data/core/observations-surface-land/mw/FWCL/landFixed/WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500-82.geojson'  # noqa

    r = SESSION.get(f'{URL}/data/{item}')  # noqa
    assert r.status_code == codes.ok

    item_waf = r.json()

    assert item_waf['reportId'] == 'WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500'
    assert item_waf['properties']['resultTime'] == '2021-07-07T14:55:00Z'  # noqa


    item_api_url = f'{API_URL}/collections/data.core.observations-surface-land.mw.FWCL.landFixed/items/{item_waf["id"]}'  # noqa

    item_api = SESSION.get(item_api_url).json()

    # make minor adjustments to payload to normalize API additions
    item_api.pop('links')
    item_waf['properties']['id'] = item_waf['id']

    assert item_waf == item_api


def test_data_api():
    """Test data API collection queries"""

    url = f'{API_URL}/collections/data.core.observations-surface-land.mw.FWCL.landFixed/items'  # noqa

    # filter by WIGOS station identifier
    params = {
        'wigos_station_identifier': '0-454-2-AWSLOBI'
    }

    r = SESSION.get(url, params=params).json()

    assert r['numberMatched'] == 17

    # filter by datetime (instant)
    params = {
        'datetime': '2021-07-08'
    }

    r = SESSION.get(url, params=params).json()

    assert r['numberMatched'] == 99

    # filter by datetime (since)
    params = {
        'datetime': '2021-07-08/..'
    }

    r = SESSION.get(url, params=params).json()

    assert r['numberMatched'] == 218

    # filter by datetime (before)
    params = {
        'datetime': '../2022-01-01'
    }

    r = SESSION.get(url, params=params).json()

    assert r['numberMatched'] == 385

    # filter by datetime (since year)
    params = {
        'datetime': '../2022'
    }

    r = SESSION.get(url, params=params).json()

    assert r['numberMatched'] == 385

    # filter by bbox
    bbox = [35.2, -16, 36, -15]
    params = {
        'bbox': ','.join(list(map(str, bbox)))
    }

    r = SESSION.get(url, params=params).json()

    assert r['numberMatched'] == 283


def test_message_api():
    """Test message API collection queries"""

    url = f'{API_URL}/collections/messages/items'
    r = SESSION.get(url).json()

    assert r['numberMatched'] == 45

    msg = r['features'][0]
    assert msg['geometry'] is not None

    props = msg['properties']
    assert props['integrity']['method'] == 'sha512'

    link_rel = msg['links'][0]

    assert link_rel['type'] == 'application/x-bufr'

    r = SESSION.get(link_rel['href'])

    assert r.status_code == codes.ok

    assert str(r.headers['Content-Length']) == str(props['content']['length'])

    assert b'BUFR' in r.content
