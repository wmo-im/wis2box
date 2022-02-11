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

import os
import subprocess
import sys

DOCKER_COMPOSE_ARGS = """
    -f docker/docker-compose.yml
    -f docker/docker-compose.override.yml
    --env-file dev.env
    -p wis2box_project
    """

def usage() -> str:
    text = """
    Usage: {program} <command> <args>

    - config: validate and view Docker configuration
    - build: build all services
    - start: start system
    - login: login to the wis2box container
    - login-root: login to the wis2box container as root
    - stop: stop system
    - update: update Docker images
    - prune: cleanup dangling containers and images
    - restart [container]: restart one or all containers
    - status [-a]: view status of wis2box containers
    - lint: run PEP8 checks against local Python code
    """

    return text.format(program=sys.argv[0])


def split(value: str) -> list:
    """
    Splits string and returns as list

    :param value: required, string. bash command.

    :returns: list. List of separated arguments.
    """
    return value.split()


def walk_path(path: str) -> list:
    """
    Walks os directory path collecting all CSV files.

    :param path: required, string. os directory.

    :returns: list. List of csv filepaths.
    """
    file_list = []
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            if name.endswith('.py'):
                file_list.append(os.path.join(root, name))

    return file_list


def make(command: str, *args) -> None:
    """
    Serves as pseudo Makefile using python subprocesses.

    :param command: required, string. Make command.

    :returns: None.
    """
    if command == "config":
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} config'))
    elif command == "build":
        cmd = "" if args[-1] == command else args[-1]
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} build {cmd}'))
    elif command == "start":
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} up -d'))
    elif command == "login":
        subprocess.run(split('docker exec -it wis2box /bin/bash'))
    elif command == "login-root":
        subprocess.run(split('docker exec -u -0 -it wis2box /bin/bash'))
    elif command == "logs":
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} logs --follow'))
    elif command == "stop":
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} down --remove-orphans'))
    elif command == "update":
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} pull'))
    elif command == "prune":
        subprocess.run(split('docker container prune -f'))
        subprocess.run(split('docker volume prune -f'))
        _ = subprocess.run(split('docker images --filter dangling=true -q --no-trunc'), stdout=subprocess.PIPE).stdout.decode('ascii')
        subprocess.run(split(f'docker rmi {_}'))
        _ = subprocess.run(split('docker ps -a -q'), stdout=subprocess.PIPE).stdout.decode('ascii')
        subprocess.run(split(f'docker rm {_}'))
    elif command == "restart":
        container = "" if args[-1] == command else args[-1]
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} restart {container}'))
    elif command == "status":
        cmd = "" if args[-1] == command else args[-1]
        subprocess.run(split(f'docker-compose {DOCKER_COMPOSE_ARGS} ps {cmd}'))
    elif command == "lint":
        files = walk_path(".")
        subprocess.run(('flake8', *files))
    else:
        print(usage())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(usage())
        sys.exit(1)

    make(sys.argv[1], *sys.argv)
