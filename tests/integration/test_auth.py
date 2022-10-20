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

from pathlib import Path

from requests import Session

DATADIR = Path('.').parent.absolute() / 'tests/data'

URL = 'http://localhost:8999'
API_URL = f'{URL}/oapi'
TOPIC = 'ita.roma_met_centre.data.core.weather.surface-based-observations.SYNOP'  # noqa
SESSION = Session()


def test_auth():
    """Test wis2box auth"""

    url = f'{API_URL}/collections/{TOPIC}/items'  # noqa

    r = SESSION.get(url)
    assert r.status_code == 401

    r = SESSION.get(f'{url}?token=test_token')
    assert r.status_code == 200

    headers = {'Authorization': 'Bearer test_token'}
    r = SESSION.get(url, headers=headers)
    assert r.status_code == 200
