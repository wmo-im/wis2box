#!/usr/bin/env python3
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

import argparse
import glob
import http.client
import json
import os
import subprocess
from urllib.parse import urlparse

if subprocess.call(['docker', 'compose'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) > 0:
    DOCKER_COMPOSE_COMMAND = 'docker-compose'
else:
    DOCKER_COMPOSE_COMMAND = 'docker compose'

DOCKER_COMPOSE_ARGS = """
    --file docker-compose.yml
    --file docker-compose.override.yml
    --file docker-compose.monitoring.yml
    --env-file wis2box.env
    --project-name wis2box_project
    """

GITHUB_RELEASE_REPO = 'wmo-im/wis2box-release'

LOCAL_BUILD_IMAGES = ['wis2box-broker', 'wis2box-management', 'wis2box-mqtt-metrics-collector']

parser = argparse.ArgumentParser(
    description='manage a composition of docker containers to implement a WIS2-in-a-box',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
    '--ssl',
    dest='ssl',
    action='store_true',
    help='run wis2box with SSL enabled')

parser.add_argument(
    '--simulate',
    dest='simulate',
    action='store_true',
    help='simulate execution by printing action rather than executing')

commands = [
    'build',
    'config',
    'down',
    'execute',
    'lint',
    'logs',
    'login',
    'prune',
    'restart',
    'start',
    'start-dev',
    'status',
    'stop',
    'up',
    'update',
]

parser.add_argument('command',
                    choices=commands,
                    help="""
    - config: validate and view Docker configuration
    - build [containers]: build all services
    - start [containers]: start system
    - start-dev [containers]: start system in local development mode
    - login [container]: login to the container (default: wis2box-management)
    - login-root [container]: login to the container as root
    - stop: stop [container] system
    - update: update Docker images
    - prune: cleanup dangling containers and images
    - restart [containers]: restart one or all containers
    - status [containers|-a]: view status of wis2box containers
    - lint: run PEP8 checks against local Python code
    """)

parser.add_argument('args', nargs=argparse.REMAINDER)

args = parser.parse_args()


def split(value: str) -> list:
    """
    Splits string and returns as list

    :param value: required, string. bash command.

    :returns: list. List of separated arguments.
    """
    return value.split()


def find_files(path: str, extension: str) -> list:
    """
    Walks directory path collecting all files of a given extention.

    :param path: `str` of directory path
    :param extension: `str` of file extension

    :returns: `list` of Python filepaths
    """

    file_list = []
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            if name.endswith(extension):
                file_list.append(os.path.join(root, name))

    return file_list


def run(cmd, silence_stderr=False) -> None:

    if not silence_stderr:
        subprocess.run(cmd)
    else:
        subprocess.run(cmd, stderr=subprocess.DEVNULL)

    return None


def fetch_data_from_url(url: str, headers: dict = {}) -> bytes:
    """
    Fetch data from a given URL.

    :param url: required, string. URL to fetch data from.
    :param headers: optional, dict. Headers to send with the request.

    :returns: bytes. The response data.
    """

    parsed_url = urlparse(url)
    full_path = parsed_url.path
    if parsed_url.query:  # Include query string if it exists
        full_path += '?' + parsed_url.query
    try:
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        conn.request("GET", full_path, headers=headers)
        response = conn.getresponse()
        # Follow redirect if status is 301 or 302
        if response.status in (301, 302):
            location = response.getheader('Location')
            if location:
                conn.close()
                return fetch_data_from_url(location, headers)
        elif response.status != 200:
            print(f"Error fetching URL: {response.status}")
            exit(1)
        return response.read()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        exit(1)

def get_resolved_version() -> str:
    """
    Determine the latest matching release tag from the wis2box-release repository.

    :return: The latest release tag or an error message if not found.
    """

    # check if we running in a local build environment
    if os.path.exists('.git') and os.path.isdir('wis2box-management'):
        print('wis2box-management directory exists, assuming local build')
        return 'LOCAL_BUILD'
    # otherwise we are in a release environment and VERSION.txt should exist
    if not os.path.exists('VERSION.txt'):
        print('VERSION.txt file does not exist')
        exit(1)
    with open('VERSION.txt') as f:
        base_version = f.readline().strip()
    
    if base_version == 'LOCAL_BUILD':
        return base_version
    # otherwise, fetch the latest release tag from GITHUB_RELEASE_REPO
    url = f'https://api.github.com/repos/{GITHUB_RELEASE_REPO}/releases'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'wis2box'
    }

    options = []
    data = fetch_data_from_url(url, headers)
    releases = json.loads(data.decode('utf-8'))
    for release in releases:
        if base_version in release['tag_name']:
            options.append(release['tag_name'])

    if options:
        # Sort options by the patch version (assuming format vX.Y.Z)
        def extract_patch_version(tag):
            try:
                # Split the version string by dots after removing the 'v' prefix
                parts = tag.lstrip('v').split('.')
                # Return the patch version as an integer (last part)
                return int(parts[2]) if len(parts) > 2 else 0
            except (ValueError, IndexError):
                # malformed version string are sorted last
                return -1
        options.sort(key=extract_patch_version, reverse=True)
        return options[0]
    else:
        print(f'No matching versions found for VERSION.txt={base_version}')
        exit(1)


def remove_old_docker_images() -> None:
    """
    Remove any image in docker-compose.images-*.yml.bak
    that is not in docker-compose.images-*.yml

    :return: None.
    """

    old_images = []
    new_images = []
    
    docker_image_files_old = glob.glob('docker-compose.images-*.yml.bak')
    for file_ in docker_image_files_old:
        with open(file_) as f:
            for line in f:
                if 'image:' in line:
                    old_images.append(line.split(':', 1)[1].strip())

    docker_image_files_new = glob.glob('docker-compose.images-*.yml')
    for file_ in docker_image_files_new:
        with open(file_) as f:
            for line in f:
                if 'image:' in line:
                    new_images.append(line.split(':', 1)[1].strip())

    for image in old_images:
        if image not in new_images:
            print(f'Removing {image}')
            subprocess.run(['docker', 'rmi', image], stderr=subprocess.DEVNULL)
    
    # ask user to remove the old docker-compose.images-*.yml.bak files
    for file_ in docker_image_files_old:
        query = f'Remove {file_} ? (y/n)'
        print(query)
        response = input()
        while response not in ['y', 'n']:
            print(query)
            response = input()
        if response == 'y':
            os.remove(file_)

def build_local_images() -> None:
    for image in LOCAL_BUILD_IMAGES:
        print(f'Building {image}')
        run(split(f'docker build -t {image} ./{image}'))

    image_file = glob.glob('docker-compose.images-*.yml')[0]
    # overwrite the image tag with the local image
    with open(image_file) as f:
        data = f.readlines()
    with open(image_file, 'w') as f:
        for line in data:
            if 'image: ' in line:
                image = line.split(':', 1)[1].strip()
                image_name = image.split(':')[0].split('/')[-1]
                if image_name in LOCAL_BUILD_IMAGES:
                    line = f'    image: {image_name}\n'
            f.write(line)

def update_images_yml() -> str:
    """

    Update the docker-compose.images-*.yml file to the latest release tag.

    :return: The latest release tag or an error message if not found.
    """
    
    # get the latest release tag
    version = get_resolved_version()
    if version == 'LOCAL_BUILD':
        url_host = 'raw.githubusercontent.com'
        url_path = f'/{GITHUB_RELEASE_REPO}/refs/heads/main/docker-compose.images.yml'
    else:
        url_host = 'github.com'
        url_path = f'/{GITHUB_RELEASE_REPO}/releases/download/{version}/docker-compose.images.yml'

    current_version = 'Undefined'
    # find currently used version of docker-compose.images-*.yml
    for file_ in os.listdir('.'):
        if file_.startswith('docker-compose.images-') and file_.endswith('.yml'):
            current_version = file_.split('images-')[1].split('.yml')[0]

    if current_version == version:
        print(f'Current version={version}, no update of images file required')
        # docker pull the images to ensure they are up to date
        with open(f'docker-compose.images-{version}.yml') as f:
            for line in f:
                if 'image:' in line:
                    image = line.split(':', 1)[1].strip()
                    if image in LOCAL_BUILD_IMAGES:
                        continue
                    print(f'Pulling {image}')
                    run(split(f'docker pull {image}'))
        return
    
    if version not in ['LOCAL_BUILD', 'Undefined']:
        # ask the user if they want to update the docker-compose.images-*.yml file
        print(f'Current version={current_version}, latest version={version}')
        query = f'Would you like to update ? (y/n/exit)'
        print(query)
        response = input()
        while response not in ['y', 'n', 'exit']:
            print(query)
            response = input()
        if response == 'n':
            return
        if response == 'exit':
            exit(0)
        if response == 'y':
            print(f'Updating wis2box to version {version}')
    
    # download the file and store as docker-compose.images-{version}.yml
    data = fetch_data_from_url(f'https://{url_host}{url_path}')
    with open(f'docker-compose.images-{version}.yml', 'wb') as f:
        f.write(data)
                     
    # rename any other docker-compose.images-*.yml file to .bak
    image_files = glob.glob('docker-compose.images-*.yml')
    for file_ in image_files:
        if file_ != f'docker-compose.images-{version}.yml':
            os.rename(file_, file_ + '.bak')
    
def make(args) -> None:
    """
    Serves as pseudo Makefile using Python subprocesses.

    :param command: required, string. Make command.

    :returns: None.
    """

    if not os.path.exists('wis2box.env'):
        print("ERROR: wis2box.env file does not exist.  Please create one manually or by running `python3 wis2box-create-config.py`")
        exit(1)
    # check if WIS2BOX_SSL_KEY and WIS2BOX_SSL_CERT are set
    ssl_key = None
    ssl_cert = None
    with open('wis2box.env') as f:
        for line in f:
            if 'WIS2BOX_SSL_KEY' in line:
                ssl_key = line.split('=')[1].strip()
            if 'WIS2BOX_SSL_CERT' in line:
                ssl_cert = line.split('=')[1].strip()

    if not glob.glob('docker-compose.images-*.yml'):
        print("No docker-compose.images-*.yml files found, creating one")
        update_images_yml()
        # update docker_compose_args with the latest docker-compose.images-*.yml file
        docker_image_file = glob.glob('docker-compose.images-*.yml')[0]
        docker_compose_args = DOCKER_COMPOSE_ARGS + f' --file {docker_image_file}'

    docker_image_file = glob.glob('docker-compose.images-*.yml')[0]
    docker_compose_args = DOCKER_COMPOSE_ARGS + f' --file {docker_image_file}'
    if args.ssl or (ssl_key and ssl_cert):
        docker_compose_args +=" --file docker-compose.ssl.yml"
    if args.ssl and not (ssl_key and ssl_cert):
        print("ERROR: SSL is enabled but WIS2BOX_SSL_KEY and WIS2BOX_SSL_CERT are not set in wis2box.env")
        exit(1)
    # if you selected a bunch of them, default to all
    containers = "" if not args.args else ' '.join(args.args)

    # if there can be only one, default to wisbox
    container = "wis2box-management" if not args.args else ' '.join(args.args)

    if args.command == "config":
        run(split(f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} config'))
    elif args.command == "build":
        build_local_images()
    elif args.command in ["up", "start", "start-dev"]:
        # if no docker-compose.images-*.yml files exist, run get_images()
        run(split(
            'docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions'),
            silence_stderr=True)
        run(split('docker plugin enable loki'), silence_stderr=True)
        if containers:
            run(split(f"{DOCKER_COMPOSE_COMMAND} {docker_compose_args} start {containers}"))
        else:
            if args.command == 'start-dev':
                run(split(f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} --file docker-compose.dev.yml up -d'))
            else:
                run(split(f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} up -d'))
                remove_old_docker_images()
    elif args.command == "execute":
        run(['docker', 'exec', '-i', 'wis2box-management', 'sh', '-c', containers])
    elif args.command == "login":
        run(split(f'docker exec -it {container} /bin/bash'))
    elif args.command == "login-root":
        run(split(f'docker exec -u -0 -it {container} /bin/bash'))
    elif args.command == "logs":
        run(split(
            f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} logs --follow {containers}'))
    elif args.command in ["stop", "down"]:
        if containers:
            run(split(f"{DOCKER_COMPOSE_COMMAND} {docker_compose_args} {containers}"))
        else:
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} down --remove-orphans {containers}'))
    elif args.command == "update":
        update_images_yml()
        # update docker_compose_args with the latest docker-compose.images-*.yml file
        docker_image_file = glob.glob('docker-compose.images-*.yml')[0]
        docker_compose_args = DOCKER_COMPOSE_ARGS + f' --file {docker_image_file}'
        # if the argument "--restart" is passed, restart all containers and clean old images
        if "--restart" in args.args:
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} down --remove-orphans'))
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} up -d'))
            remove_old_docker_images()
    elif args.command == "prune":
        run(split('docker builder prune -f'))
        run(split('docker container prune -f'))
        run( split('docker volume prune -f'))
        _ = run(split('docker images --filter dangling=true -q --no-trunc'))
        run(split(f'docker rmi {_}'))
        _ = run(split('docker ps -a -q'))
        run(split(f'docker rm {_}'))
    elif args.command == "restart":
        if containers:
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} stop {containers}'))
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} start {containers}'))
        else:
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} down --remove-orphans'))
            run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} up -d'))
    elif args.command == "status":
        run(split(
            f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} ps {containers}'))
    elif args.command == "lint":
        files = find_files(".", '.py')
        run(('python3', '-m', 'flake8', *files))


if __name__ == "__main__":
    make(args)
