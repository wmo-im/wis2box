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
import os

from pathlib import Path

from pywis_pubsub.validation import validate_message
from requests import Session, codes

DATADIR = Path('.').parent.absolute() / 'tests/data'
print(f"{DATADIR}")
URL = 'http://localhost'
API_URL = f'{URL}/oapi'
ID = 'urn:wmo:md:mw-mw_met_centre:surface-weather-observations'
SESSION = Session()
SESSION.hooks = {
   'response': lambda r, *args, **kwargs: r.raise_for_status()
}


def test_wis2downloader():
    """Test if the wis2downloader has downloaded
    the expected number of files in the download directory"""

    DOWNLOAD_DIR = DATADIR / 'downloads'

    topic_nfiles_dict = {
        'origin/a/wis2/mw-mw_met_centre/data/core/weather/surface-based-observations/synop': 23, # noqa
        'origin/a/wis2/dz-alger_met_centre/data/core/weather/surface-based-observations/synop': 28, # noqa
        'origin/a/wis2/cn-cma/data/core/weather/prediction/forecast/medium-range/probabilistic/global': 10, # noqa
        'origin/a/wis2/ro-rnimh/data/core/weather/surface-based-observations/synop': 49, # noqa
        'origin/a/wis2/cd-brazza_met_centre/data/core/weather/surface-based-observations/synop': 14, # noqa
        'origin/a/wis2/int-wmo-test/data/core/weather/surface-based-observations/buoy': 2, # noqa
        'origin/a/wis2/int-wmo-test/data/core/weather/surface-based-observations/wind_profiler': 1, # noqa
        'origin/a/wis2/int-wmo-test/data/core/weather/surface-based-observations/ship': 5, # noqa
        'origin/a/wis2/it-roma_met_centre/data/core/weather/surface-based-observations/synop': 31 # noqa
    }

    topic_nfiles_dict_found = {}
    for key in topic_nfiles_dict.keys():
        topic_nfiles_dict_found[key] = 0

    # count the number of files received in the download directory
    # over all subdirectories
    total_files = 0
    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        total_files += len(files)
        for key in topic_nfiles_dict.keys():
            if key in root:
                topic_nfiles_dict_found[key] += len(files)

    # check if the number of files downloaded for each topic
    # matches the expected number
    for key in topic_nfiles_dict.keys():
        assert topic_nfiles_dict[key] == topic_nfiles_dict_found[key]


def test_metadata_station_cache():
    """Test station metadata caching"""

    wmo_regions = [
        'africa',
        'antarctica',
        'asia',
        'europe',
        'inapplicable',
        'northCentralAmericaCaribbean',
        'southAmerica',
        'southWestPacific',
        'unknown'
    ]

    with (DATADIR / 'metadata/station/station_list.csv').open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            wsi = row['wigos_station_identifier']
            r = SESSION.get(f'{API_URL}/collections/stations/items/{wsi}')

            assert r.status_code == codes.ok

            station = r.json()

            assert station['properties']['wigos_station_identifier'] == wsi
            assert station['properties']['wmo_region'] in wmo_regions


def test_metadata_station_publish():
    """Test station metadata publishing"""

    r = SESSION.get(f'{API_URL}/collections/stations/items')

    assert r.status_code == codes.ok

    stations = r.json()

    assert stations['numberReturned'] == 103
    assert stations['numberMatched'] == 103


def test_metadata_discovery_publish():
    """Test discovery metadata publishing"""

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items').json()
    assert r['numberMatched'] == 9

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items/{ID}').json()  # noqa

    assert r['id'] == ID
    assert r['properties']['title'] == 'Surface weather observations from Malawi' # noqa

    assert len(r['links']) == 9

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

    mqtt_link = [d for d in r['links'] if d['href'].startswith('mqtt')][0]

    assert 'everyone:everyone' in mqtt_link['href']
    assert mqtt_link['channel'] == 'origin/a/wis2/mw-mw_met_centre/data/core/weather/surface-based-observations/synop'  # noqa

    params = {
        'q': 'temperature'
    }

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items',
                    params=params).json()

    assert r['numberMatched'] == 8

    # test access of discovery metadata from notification message

    centre_ids = [
        'mw-mw_met_centre',
        'it-roma_met_centre',
        'dz-alger_met_centre',
        'ro-rnimh',
        'cd-brazza_met_centre',
        'int-wmo-test'
    ]

    for centre_id in centre_ids:
        params = {
            'q': f'{centre_id} AND metadata'
        }

        r = SESSION.get(f'{API_URL}/collections/messages/items',
                        params=params).json()

        assert r['numberMatched'] >= 1

        feature = r['features'][0]
        assert feature['properties']['data_id'].startswith(centre_id)

        link = feature['links'][0]

        assert link['type'] == 'application/geo+json'
        assert link['href'].endswith('json')

        r = SESSION.get(link['href'])
        assert r.headers['Content-Type'] == 'application/geo+json'

        r = r.json()
        assert r['conformsTo'][0] == 'http://wis.wmo.int/spec/wcmp/2/conf/core'


def test_data_ingest():
    """Test data ingest/process publish"""

    item_api_url = f'{API_URL}/collections/{ID}/items/WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500-82'  # noqa

    item_api = SESSION.get(item_api_url).json()

    assert item_api['reportId'] == 'WIGOS_0-454-2-AWSNAMITAMBO_20210707T145500'
    assert item_api['properties']['resultTime'] == '2021-07-07T14:55:00Z'  # noqa
    item_source = f'2021-07-07/wis/{ID}/{item_api["reportId"]}.bufr4' # noqa
    r = SESSION.get(f'{URL}/data/{item_source}')  # noqa
    assert r.status_code == codes.ok


def test_data_api():
    """Test data API collection queries"""

    url = f'{API_URL}/collections/{ID}/items'

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

    # check messages with "q=AWSBALAKA" contains link with rel='update'
    url = f'{API_URL}/collections/messages/items?q=AWSBALAKA&limit=2'  # noqa
    r = SESSION.get(url).json()
    # get links from 2nd message
    links = r['features'][1]['links']

    # check link contains rel='update'
    assert any(link['rel'] == 'update' for link in links)

    # test messages per test dataset
    counts = {
        'mw-mw_met_centre': 25,
        'it-roma_met_centre': 33,
        'dz-alger_met_centre': 29,
        'ro-rnimh': 50,
        'cd-brazza_met_centre': 15,
        'int-wmo-test': 11,
        'cn-cma': 11
    }
    for key, value in counts.items():
        url = f'{API_URL}/collections/messages/items?sortby=-datetime&q={key}&limit=1'  # noqa
        r = SESSION.get(url).json()
        assert r['numberMatched'] == value

    url = f'{API_URL}/collections/messages/items?sortby=-datetime'
    r = SESSION.get(url).json()

    # should match sum of counts above
    assert r['numberMatched'] == sum(counts.values())

    # we want to find a particular message with data ID
    target_data_id = "cd-brazza_met_centre:surface-weather-observations/WIGOS_0-20000-0-64406_20230803T090000" # noqa

    msg = None
    for feature in r['features']:
        if feature['properties']['data_id'] == target_data_id:
            msg = feature
            break

    assert msg is not None

    is_valid, _ = validate_message(msg)
    assert is_valid

    assert msg['geometry'] is not None

    props = msg['properties']
    assert props['datetime'] == '2023-08-03T09:00:00Z'
    assert props['wigos_station_identifier'] == '0-20000-0-64406'
    assert props['integrity']['method'] == 'sha512'
    assert not props['data_id'].startswith('wis2')
    assert not props['data_id'].startswith('origin/a/wis2')
    assert props['data_id'].startswith('cd')
    assert props['content']['size'] == 253
    assert props['content']['encoding'] == 'base64'
    assert props['content']['value'] is not None
    assert 'gts' in props
    assert props['gts']['ttaaii'] == 'SICG20'
    assert props['gts']['cccc'] == 'FCBB'

    link_rel = msg['links'][0]

    assert link_rel['type'] == 'application/x-bufr'

    r = SESSION.get(link_rel['href'])

    assert r.status_code == codes.ok

    assert str(r.headers['Content-Length']) == str(link_rel['length'])

    assert b'BUFR' in r.content
