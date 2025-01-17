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
import os
import requests
import subprocess

from packaging.version import Version

if subprocess.call(['docker', 'compose'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) > 0:
    DOCKER_COMPOSE_COMMAND = 'docker-compose'
else:
    DOCKER_COMPOSE_COMMAND = 'docker compose'

DOCKER_COMPOSE_ARGS = f"""
    --file docker-compose.yml
    --file docker-compose.override.yml
    --file docker-compose.monitoring.yml
    --env-file wis2box.env
    --project-name wis2box_project
    """

# NOTE using maaikelimper/wis2box-release for demo purposes, should be wmo-im/wis2box-release
GITHUB_RELEASE_REPO = 'maaikelimper/wis2box-release'

parser = argparse.ArgumentParser(
    description='manage a compposition of docker containers to implement a wis 2 box',
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


def get_resolved_version() -> None:
    """
    Determine the latest matching release tag from the wis2box-release repository.

    :return: The latest release tag or an error message if not found.
    """

    # read the base version from wis2box.version
    if not os.path.exists('wis2box.version'):
        print('wis2box.version file does not exist')
        exit(1)

    base_version = None
    with open('wis2box.version', 'r') as f:
        base_version = f.readline().strip()

    if base_version == 'LOCAL_BUILD':
        return base_version

    url = f'https://api.github.com/repos/{GITHUB_RELEASE_REPO}/releases'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    options = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            releases = response.json()
            for release in releases:
                if base_version in release['tag_name']:
                    options.append(release['tag_name'])
        else:
            print(f'Error fetching latest release tag for {base_version}: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error fetching latest release tag for {base_version}: {e}')

    return None

def remove_old_docker_images() -> None:
    """
    Remove any image in docker-compose.images-*.yml.bak
    that is not in docker-compose.images-*.yml

    :return: None.
    """
    old_images = []
    new_images = []
    if os.path.exists('docker-compose.images-*.yml.bak'):
        with open('docker-compose.images-*.yml.bak', 'r') as f:
            for line in f:
                if 'image' in line:
                    old_images.append(line.split(':')[1].strip())
    if os.path.exists('docker-compose.images-*.yml'):
        with open('docker-compose.images-*.yml', 'r') as f:
            for line in f:
                if 'image' in line:
                    new_images.append(line.split(':')[1].strip())
    for image in old_images:
        if image not in new_images:
            run(split(f'docker rmi {image}'))

def update_images_yml() -> str:
    """

    Update the docker-compose.images-*.yml file to the latest release tag.

    :return: The latest release tag or an error message if not found.
    """
    
    # get the latest release tag
    version = get_resolved_version()
    if version == 'LOCAL_BUILD':
        # use the version of images in main branch
        url = f'https://raw.githubusercontent.com/{GITHUB_RELEASE_REPO}/refs/heads/main/docker-compose.images.yml'
    else:
        url = f'https://github.com/{GITHUB_RELEASE_REPO}/releases/download/{version}/docker-compose.images.yml'

    current_version = 'Undefined'
    # find currently used version of docker-compose.images-*.yml
    for file in os.listdir('.'):
        if file.startswith('docker-compose.images-') and file.endswith('.yml'):
            current_version = file.split('-')[2].split('.')[0]
            
    if current_version == version:
        print(f'Using latest version {version}, no update of images file required')
        return
    
    if version not in ['LOCAL_BUILD', '']:
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
    
    # download the file and store as docker-compose.images-{resolved_version}.yml
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f'docker-compose.images-{version}.yml', 'wb') as f:
                f.write(response.content)
        else:
            print(f'Error fetching docker-compose.images.yml: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error fetching docker-compose.images.yml: {e}')
        raise e
    
    # rename the current docker-compose.images-*.yml file
    if current_version != 'Undefined':
        os.rename(f'docker-compose.images-{current_version}.yml', f'docker-compose.images-{current_version}.yml.bak')

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
    with open('wis2box.env', 'r') as f:
        for line in f:
            if 'WIS2BOX_SSL_KEY' in line:
                ssl_key = line.split('=')[1].strip()
            if 'WIS2BOX_SSL_CERT' in line:
                ssl_cert = line.split('=')[1].strip()

    if not glob.glob('docker-compose.images-*.yml'):
        print("No docker-compose.images-*.yml files found, creating one")
        update_images_yml()

    docker_image_file = glob.glob('docker-compose.images-*.yml')[0]

    docker_compose_args = DOCKER_COMPOSE_ARGS + f' --file {docker_image_file}'
    print(docker_compose_args)
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
        run(split(
            f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} build {containers}'))
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
        run(split(f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} pull'))
        # restart all containers
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
