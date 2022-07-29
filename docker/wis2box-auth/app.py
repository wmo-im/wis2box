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

from flask import Flask, request
import logging
import os
import re
from typing import Tuple

from wis2box.auth import is_token_authorized, is_resource_open
from wis2box.env import LOGLEVEL, LOGFILE
from wis2box.log import setup_logger

LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
setup_logger(LOGLEVEL, LOGFILE)
app.secret_key = os.urandom(32)


def get_response(code: int, description: str) -> Tuple[dict, int]:
    """
    Generate wis2box-auth response

    :param code: `int` of HTTP response status
    :param description: `str` of response description

    :returns: `Tuple` of wis2box-auth response instance
    """

    return {
        'code': code,
        'description': description
    }, code


def extract_topic(uri: str) -> str:
    """
    Extract Topic Hierarchy from URI

    :param uri: `str` of requested URI

    :returns: `str` of API collection metadata
    """

    # TODO: Move away from regex matching for topic hierarchies.
    pattern = r'(data[\/.][a-z]{4,11}[\/.][a-z-]+[\/.][a-z]{2}[\/.][A-Z]*[\/.][a-zA-Z]+)'  # noqa
    prog = re.compile(pattern)
    match = prog.search(uri)
    return match[0] if match else None


@app.route('/authorize')
def authorize():
    api_key = None
    request_uri = request.headers.get('X-Original-URI')
    request_ = request.from_values(request_uri)

    LOGGER.debug('Extracting topic from request URI')
    resource = extract_topic(request_uri)

    LOGGER.debug('Extracting API token')
    auth_header = request.headers.get('Authorization')
    if request_.args.get('token'):
        api_key = request_.args.get('token')
    elif auth_header is not None and 'Bearer' in auth_header:
        api_key = auth_header.split()[-1].strip()

    # check if resource passed exists in auth list
    # if no, it's open, return
    if resource is None or is_resource_open(resource):
        return get_response(200, 'Resource is open')

    LOGGER.debug(f'Request for restricted resource: {resource}')
    # if yes, check that api key exists
    # if no, return 401
    if api_key is None:
        return get_response(401, 'Missing API key')

    # check that API key can access the resource
    if is_token_authorized(api_key, resource):
        LOGGER.debug('Access granted')
        return get_response(200, 'Authorized')
    else:
        LOGGER.debug('Access denied')
        return get_response(401, 'Unauthorized')


if __name__ == '__main__':
    app.run()
