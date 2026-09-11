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

from pywis_pubsub.wnm.ets import WNMTestSuite
from requests import Session, codes

from time import sleep

DATADIR = Path('.').parent.absolute() / 'tests/data'

URL = 'http://localhost'
API_URL = f'{URL}/oapi'
ID = 'urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations'
SESSION = Session()
SESSION.hooks = {
   'response': lambda r, *args, **kwargs: r.raise_for_status()
}


def test_pywispubsub():
    """Test if pywis-pubsub has downloaded
    the expected number of files in the download directory"""

    DOWNLOAD_DIR = DATADIR / 'downloads'

    topic_nfiles_dict = {
        'mw-mw_met_centre-test:surface-weather-observations': 23, # noqa
        'dz-meteoalgerie:surface-weather-observations': 28, # noqa
        #'cn-cma:grapes-geps-global': 10, # pywis-pubsub does not download when cache=false # noqa
        'ro-rnimh-test:synoptic-weather-observations': 49, # noqa
        'cg-met:surface-weather-observations': 0, # noqa
        'int-wmo-test:surface-weather-observations:drifting-buoys': 2, # noqa
        'int-wmo-test:surface-weather-observations:wind-profile': 1, # noqa
        'int-wmo-test:surface-weather-observations:ship': 6, # noqa
        'it-meteoam:surface-weather-observations': 31, # noqa
        'int-wmo-test:cap': 1, # noqa
        'org-daycli-test:surface-climate-observations:daily': 30 # noqa
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
            sleep(0.2)  # avoid hitting the rate limit of 10 requests/s
            assert r.status_code == codes.ok

            station = r.json()

            assert station['properties']['wigos_station_identifier'] == wsi
            assert station['properties']['wmo_region'] in wmo_regions


def test_metadata_station_publish():
    """Test station metadata publishing"""

    r = SESSION.get(f'{API_URL}/collections/stations/items')

    assert r.status_code == codes.ok

    stations = r.json()

    assert stations['numberReturned'] == 105
    assert stations['numberMatched'] == 105


def test_metadata_discovery_publish():
    """Test discovery metadata publishing"""

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items').json()
    assert r['numberMatched'] == 12

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
    assert mqtt_link['channel'] == 'origin/a/wis2/mw-mw_met_centre-test/data/core/weather/surface-based-observations/synop'  # noqa

    params = {
        'q': 'temperature'
    }

    r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items',
                    params=params).json()
    assert r['numberMatched'] == 9

    # test access of discovery metadata from notification message

    centre_ids = [
        'ca-eccc-msc-test',
        'mw-mw_met_centre-test',
        'it-meteoam',
        'dz-meteoalgerie',
        'ro-rnimh-test',
        'cg-met',
        'int-wmo-test',
        'org-daycli-test'
    ]

    for centre_id in centre_ids:
        params = {
            'q': f'{centre_id} +metadata'
        }

        r = SESSION.get(f'{API_URL}/collections/messages/items',
                        params=params).json()
        sleep(0.2)  # avoid hitting the rate limit of 10 requests/s

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

        id_ = 'urn:wmo:md:cg-met:surface-weather-observations'
        r = SESSION.get(f'{API_URL}/collections/discovery-metadata/items/{id_}').json()  # noqa
        sleep(0.2)  # avoid hitting the rate limit of 10 requests/s

        assert 'has_auth' in r['wis2box']
        assert r['wis2box']['has_auth']

        # test object storage publication
        r = SESSION.get(f'{URL}/data/metadata/{ID}.json').json()
        sleep(0.2)  # avoid hitting the rate limit of 10 requests/s
        assert 'wis2box' not in r
        assert 'wmo:topicHierarchy' not in r['properties']


def test_data_ingest():
    """Test data ingest/process publish"""

    item_api_url = f'{API_URL}/collections/{ID}/items/0-454-2-AWSNAMITAMBO-202107071455-15'  # noqa

    item_api = SESSION.get(item_api_url).json()

    assert item_api['properties']['reportId'] == '0-454-2-AWSNAMITAMBO-202107071455' # noqa
    assert item_api['properties']['reportTime'] == '2021-07-07T14:55:00Z'  # noqa
    assert item_api['properties']['wigos_station_identifier'] == '0-454-2-AWSNAMITAMBO'  # noqa
    assert item_api['properties']['name'] == 'global_solar_radiation_integrated_over_period_specified' # noqa
    assert item_api['properties']['value'] == 0.0
    assert item_api['properties']['units'] == 'J m-2'
    assert item_api['properties']['phenomenonTime'] == '2021-07-06T14:55:00Z/2021-07-07T14:55:00Z'  # noqa


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

    # check message with q=grapes-geps-global has properties cache=false
    url = f'{API_URL}/collections/messages/items?q=cn-cma:grapes-geps-global&limit=1'  # noqa
    r = SESSION.get(url).json()
    props = r['features'][0]['properties']
    assert 'cache' in props
    assert not props['cache']

    # check link contains rel='update'
    assert any(link['rel'] == 'update' for link in links)

    # test messages per test dataset
    counts = {
        'unpublish': 2,
        'ca-eccc-msc': 1,
        'mw-mw_met_centre': 25,
        'it-meteoam:surface': 32,  # excludes metadata
        'dz-meteoalgerie:surface': 28,  # excludes metadata
        'ro-rnimh': 50,
        'cg-met:surface': 14,  # excludes metadata
        'int-wmo': 14,
        'cn-cma:grapes': 10,  # excludes metadata
        'org-daycli': 31
    }
    for key, value in counts.items():
        url = f'{API_URL}/collections/messages/items?sortby=-datetime&q={key}&limit=1'  # noqa
        r = SESSION.get(url).json()
        sleep(0.2)  # avoid hitting the rate limit of 10 requests/s
        assert r['numberMatched'] == value

    url = f'{API_URL}/collections/messages/items?sortby=-datetime'
    r = SESSION.get(url).json()

    # should match sum of counts above + 4 metadata-messages
    assert r['numberMatched'] == sum(counts.values()) + 4

    # we want to find a particular message with data ID for core data
    target_data_id = 'mw-mw_met_centre-test:surface-weather-observations/WIGOS_0-454-2-AWSLOBI_20211111T125500'  # noqa

    msg = None
    for feature in r['features']:
        if feature['properties']['data_id'] == target_data_id:
            msg = feature
            break

    assert msg is not None

    ts = WNMTestSuite(msg)
    ts.run_tests()
    assert ts.raise_for_status() is None

    assert msg['geometry'] is not None

    props = msg['properties']
    assert props['datetime'] == '2021-11-11T12:55:00Z'
    assert props['wigos_station_identifier'] == '0-454-2-AWSLOBI'
    assert props['integrity']['method'] == 'sha512'
    assert not props['data_id'].startswith(('origin/a/wis2', 'wis2'))
    assert props['data_id'].startswith('mw')
    assert props['content']['size'] == 247
    assert props['content']['encoding'] == 'base64'
    assert props['content']['value'] is not None

    link_rel = msg['links'][0]

    assert link_rel['type'] == 'application/bufr'

    r = SESSION.get(link_rel['href'])

    assert r.status_code == codes.ok

    assert str(r.headers['Content-Length']) == str(link_rel['length'])

    assert b'BUFR' in r.content

    # we want to find a particular message with data ID for recommended data
    url = f'{API_URL}/collections/messages/items?sortby=-datetime&q=cg-met:surface'  # noqa
    r = SESSION.get(url).json()

    target_data_id = "cg-met:surface-weather-observations/WIGOS_0-20000-0-64406_20230803T090000" # noqa

    msg = None
    for feature in r['features']:
        if feature['properties']['data_id'] == target_data_id:
            msg = feature
            break

    assert msg is not None

    ts = WNMTestSuite(msg)
    ts.run_tests()
    assert ts.raise_for_status() is None

    assert msg['geometry'] is not None

    props = msg['properties']
    assert props['datetime'] == '2023-08-03T09:00:00Z'
    assert props['wigos_station_identifier'] == '0-20000-0-64406'
    assert props['integrity']['method'] == 'sha512'
    assert not props['data_id'].startswith(('origin/a/wis2', 'wis2'))
    assert props['data_id'].startswith('cg')
    assert 'content' not in props
    assert 'gts' in props
    assert props['gts']['ttaaii'] == 'SICG20'
    assert props['gts']['cccc'] == 'FCBB'

    link_rel = msg['links'][0]

    assert link_rel['type'] == 'application/bufr'
    assert link_rel['security']['default']['type'] == 'http'
    assert link_rel['security']['default']['scheme'] == 'bearer'
