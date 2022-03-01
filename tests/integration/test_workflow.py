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
import json
from pathlib import Path

import requests

DATADIR = Path('.').parent.absolute() / 'tests/data'

URL = 'http://localhost:8999'
API_URL = f'{URL}/pygeoapi'


def test_data_setup():
    """Test data setup"""

    path = DATADIR / 'incoming/data/core/observations-surface-land/mw/FWCL/landFixed'  # noqa
    assert path.exists()


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

    r = requests.get(f'{API_URL}/collections/stations/items').json()

    assert r['numberMatched'] == 19


def test_metadata_discovery_publish():
    """Test discovery metadata publishing"""

    r = requests.get(f'{API_URL}/collections/discovery-metadata/items').json()
    assert r['numberMatched'] == 1

    r = requests.get(f'{API_URL}/collections/discovery-metadata/items/data.core.observations-surface-land.mw.FWCL.landFixed').json()  # noqa

    assert r['id'] == 'data.core.observations-surface-land.mw.FWCL.landFixed'
    assert r['properties']['title'] == 'Surface weather observations (hourly)'

#    assert len(r['properties']['associations']) == 2

    spatial_extent = [
        32.6881653175,
        -16.8012997372,
        35.7719047381,
        -9.23059905359
    ]

    assert r['properties']['extent']['spatial']['bbox'][0] == spatial_extent

    params = {
        'q': 'temperature'
    }

    r = requests.get(f'{API_URL}/collections/discovery-metadata/items',
                     params=params).json()

    assert r['numberMatched'] == 1


def test_data_ingest():
    """Test data ingest/process publish"""

    item = '2021-07-07/wis/data/core/observations-surface-land/mw/FWCL/landFixed/WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500.geojson'  # noqa

    r = requests.get(f'{URL}/data/{item}')  # noqa
    assert r.status_code == 200

    item_waf = r.json()

    assert item_waf['id'] == 'WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500'
    assert item_waf['properties']['phenomenonTime'] == '2021-07-07T14:55:00+00:00'  # noqa

    item_datadir_public = DATADIR / 'data' / 'public' / item
    assert item_datadir_public.exists()

    with item_datadir_public.open() as fh:
        assert item_waf == json.load(fh)

    item_api_url = f'{API_URL}/collections/data.core.observations-surface-land.mw.FWCL.landFixed/items/WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500'  # noqa

    item_api = requests.get(item_api_url).json()

    # make minor adjustments to payload to normalize API additions
    item_api.pop('links')
    item_waf['properties']['id'] = item_waf['properties']['identifier']

    assert item_waf == item_api


def test_data_api():
    """Test data API collection queries"""

    url = f'{API_URL}/collections/data.core.observations-surface-land.mw.FWCL.landFixed/items'  # noqa

    # filter by WIGOS station identifier
    params = {
        'wigos_station_identifier': '0-454-2-AWSCHINGALE'
    }

    r = requests.get(url, params=params).json()

    assert r['numberMatched'] == 469

    # filter by datetime (instant)
    params = {
        'datetime': '2021-07-08'
    }

    r = requests.get(url, params=params).json()

    assert r['numberMatched'] == 6

    # filter by datetime (since)
    params = {
        'datetime': '2021-07-08/..'
    }

    r = requests.get(url, params=params).json()

    assert r['numberMatched'] == 6433

    # filter by datetime (before)
    params = {
        'datetime': '../2022-01-01'
    }

    r = requests.get(url, params=params).json()

    assert r['numberMatched'] == 16

    # filter by datetime (since year)
    params = {
        'datetime': '2022/..'
    }

    r = requests.get(url, params=params).json()

    assert r['numberMatched'] == 6427

    # filter by bbox
    params = {
        'bbox': '35.2,-16,36,-15'
    }

    r = requests.get(url, params=params).json()

    assert r['numberMatched'] == 512
