from typing import Tuple

from flask import Flask
from flask import request

from auth import is_authorized, is_resource_open, is_key_valid

app = Flask(__name__)


def get_response(code: int, description: str) -> Tuple[dict, int]:
    return {
        'code': code,
        'description': description
    }, code


@app.route('/authorize')
def authorize():
    resource = request.args.get('url')
    api_key = request.headers.get('x-wis2box-api-key')

    if resource is None:
        return get_response(400, 'Missing parameter')

    # check if resource passed exists in auth list
    # if no, it's open, return
    if is_resource_open(resource):
        return get_response(200, 'Resource is open')

    # if yes, check that api key exists
    # if no, return 401
    if api_key is None:
        return get_response(400, 'Missing API key')

    # check that API key is valid/registered
    if not is_key_valid(api_key):
        return get_response(400, 'Invalid API key')

    # check that API key can access the resource
    if is_authorized(api_key, resource):
        return get_response(200, 'Authorized')
    else:
        return get_response(401, 'Unauthorized')


if __name__ == '__main__':
    app.run()
