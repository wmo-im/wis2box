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

from flask import Flask
from flask import request
import re
from typing import Tuple

from wis2box.auth import is_token_authorized, is_resource_open

app = Flask(__name__)


def get_response(code: int, description: str) -> Tuple[dict, int]:
    return {
        'code': code,
        'description': description
    }, code


def extract_topic(url: str) -> str:
    pattern = r'(?!^.*\/)(([a-z]{4})([\/.]{1})([a-z]{4})([\/.]{1})([a-z-]+)([\/.]{1})([a-z]{2})([\/.]{1})([A-Z]{4})([\/.]{1})([a-zA-Z]*))' # noqa
    prog = re.compile(pattern)
    match = prog.search(url)
    return match[0] if match else ''


@app.route('/authorize')
def authorize():
    request_uri = request.headers.get('X-Original-URI')
    request_ = request.from_values(request_uri)
    resource = extract_topic(request_uri)
    api_key = request.headers.get('x-wis2box-api-key') or request_.args.get('token')

    if resource is None:
        return get_response(403, 'Missing parameter')

    # check if resource passed exists in auth list
    # if no, it's open, return
    if is_resource_open(resource):
        return get_response(200, 'Resource is open')

    # if yes, check that api key exists
    # if no, return 401
    if api_key is None:
        return get_response(401, 'Missing API key')

    # check that API key can access the resource
    if is_token_authorized(api_key, resource):
        return get_response(200, 'Authorized')
    else:
        return get_response(401, 'Unauthorized')


if __name__ == '__main__':
    app.run()
