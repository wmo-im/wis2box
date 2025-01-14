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
import os
import re
import requests
import subprocess
import shutil

# read wis2box.version file if it exists
WIS2BOX_VERSION = 'LOCAL_BUILD'
if os.path.exists('wis2box.version'):
    with open('wis2box.version', 'r') as f:
        WIS2BOX_VERSION = f.read().strip()

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

parser = argparse.ArgumentParser(
    description='Manage a composition of Docker containers to implement wis2box',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('--simulate',
                    action='store_true',
                    help='Simulate execution by printing action rather than executing')

commands = [
    'build',
    'config',
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
    'update'
]

parser.add_argument('command',
                    choices=commands,
                    help="""The command to execute:
    - config: validate and view Docker configuration
    - build: build all services
    - start: start system
    - start-dev: start system in local development mode
    - login: login to the container (default: wis2box-management)
    - stop: stop system
    - update: update Docker images
    - prune: cleanup dangling containers and images
    - restart: restart containers
    - status: view status of wis2box containers
    - lint: run PEP8 checks against local Python code
    """)

parser.add_argument('args', nargs=argparse.REMAINDER, help='Additional arguments for the command')

args = parser.parse_args()

LOCAL_IMAGES = [
    'wis2box-management',
    'wis2box-broker',
    'wis2box-mqtt-metrics-collector'
]

def remove_docker_images(filter: str) -> None:
    # Get the IDs of images matching the filter
    result = subprocess.run(
        ['docker', 'images', '--filter', f'reference={filter}', '-q', '--no-trunc'],
        capture_output=True,
        text=True
    )
    
    image_ids = result.stdout.strip()
    if image_ids:  # If there are images to remove
        for image_id in image_ids.splitlines():
            try:
                subprocess.run(['docker', 'rmi', image_id], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                # do nothing
                pass

def build_local_images() -> None:
    """
    Build local images

    :returns: None.
    """
    for image in LOCAL_IMAGES:
        print(f'Building {image}')
        run(split(f'docker build -t ghcr.io/wmo-im/{image}:local {image}'))
    return None
    
def get_latest_release_tag(image: str, major_release: str = '') -> str:
    """

    Fetches the latest release tag for a GitHub repository.
    
    :param image: required, string. The name of the image repository.
    :param major_release: required, string. The major release version.

    :return: The latest release tag or an error message if not found.
    """
    url = f'https://api.github.com/repos/wmo-im/{image}/releases'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    print(f'Fetching latest release tag from GitHub for {image} using wis2box-version={major_release}')

    options = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            releases = response.json()
            for release in releases:
                print(release['tag_name'])
                if major_release in release['tag_name']:
                    options.append(release['tag_name'])
        else:
            print(f'Error fetching latest release tag for {image}: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error fetching latest release tag for {image}: {e}')

    # throw error if options is empty
    if not options:
        raise ValueError(f'No release tags found for {image} with major release {major_release}')

    # sort descending and return the first element
    options.sort(reverse=True)
    return options[0]
            
def update_docker_images(wis2box_version: str) -> None:
    """
    Write docker-compose.yml using docker-compose.base.yml as base
    

    :param wis2box_version: required, string. The version of wis2box to use.
    
    :returns: None.
    """
    
    if os.path.exists('docker-compose.yml'):
        print('Backing up current docker-compose.yml to docker-compose.yml.bak')
        shutil.copy('docker-compose.yml', 'docker-compose.yml.bak')

    if wis2box_version == 'LOCAL_BUILD':
        print('Building local images')
        build_local_images()

    print(f'Updating docker-compose.yml for wis2box_version={wis2box_version}')

    with open('docker-compose.base.yml', 'r') as f:
        lines = f.readlines()
        with open('docker-compose.yml', 'w') as f:
            for line in lines:
                if 'image: ghcr.io/wmo-im/wis2box' in line:
                    image = line.split('ghcr.io/wmo-im/')[1].split(':')[0]
                    tag = 'latest'
                    if image in LOCAL_IMAGES and wis2box_version == 'LOCAL_BUILD':
                        tag = 'local'
                    elif wis2box_version != 'LOCAL_BUILD':
                        tag = get_latest_release_tag(image, wis2box_version)
                    # pull the image if it is not local
                    if tag != 'local':
                        print(f'Pulling ghcr.io/wmo-im/{image}:{tag}')
                        # pull the latest tag for the image
                        run(split(f'docker pull ghcr.io/wmo-im/{image}:{tag}'))
                    # update the image tag in the docker-compose.yml
                    print(f'Set {image} to {tag}')
                    f.write(f'    image: ghcr.io/wmo-im/{image}:{tag}\n')
                else:
                    f.write(line)
        print('docker-compose.yml updated')
        return None

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
    docker_compose_args = DOCKER_COMPOSE_ARGS
    if (ssl_key and ssl_cert):
        docker_compose_args +=" --file docker-compose.ssl.yml"
    # if you selected a bunch of them, default to all
    containers = "" if not args.args else ' '.join(args.args)

    # if there can be only one, default to wisbox
    container = "wis2box-management" if not args.args else ' '.join(args.args)

    if args.command == "config":
        run(split(f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} config'))
    elif args.command in ["up", "start", "start-dev"]:
        if not os.path.exists('docker-compose.yml'):
            update_docker_images()
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
    elif args.command in ["update"]:
        update_docker_images(WIS2BOX_VERSION)
        # restart all containers
        run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} down --remove-orphans'))
        run(split(
                f'{DOCKER_COMPOSE_COMMAND} {docker_compose_args} up -d'))
        # perform cleanup of images after update, unless updating local build
        if not WIS2BOX_VERSION == 'LOCAL_BUILD':
            remove_docker_images('wmoim/wis2box*')
            remove_docker_images('ghcr.io/wmo-im/wis2box*')
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
    elif args.command == "prune":
        run(split('docker builder prune -f'))
        run(split('docker container prune -f'))
        run( split('docker volume prune -f'))
        # prune any unused images starting with wmoim/wis2box
        remove_docker_images('wmoim/wis2box*')
        # prune any unused images starting with ghcr.io/wmo-im/wis2box
        remove_docker_images('ghcr.io/wmo-im/wis2box*')
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
