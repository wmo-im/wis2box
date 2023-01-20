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
import subprocess

DOCKER_COMPOSE_ARGS = """
    --file docker-compose.yml
    --file docker-compose.override.yml
    --file docker-compose.monitoring.yml
    --env-file dev.env
    --project-name wis2box_project
    """

parser = argparse.ArgumentParser(
    description='manage a compposition of docker containers to implement a wis 2 box',
    formatter_class=argparse.RawTextHelpFormatter)

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


def run(args, cmd, asciiPipe=False) -> str:

    if args.simulate:
        if asciiPipe:
            print(f"simulation: {' '.join(cmd)} >/tmp/temp_buffer$$.txt")
        else:
            print(f"simulation: {' '.join(cmd)}")
        return '`cat /tmp/temp_buffer$$.txt`'
    else:
        if asciiPipe:
            return subprocess.run(
                cmd, stdout=subprocess.PIPE).stdout.decode('ascii')
        else:
            subprocess.run(cmd)
    return None


def make(args) -> None:
    """
    Serves as pseudo Makefile using Python subprocesses.

    :param command: required, string. Make command.

    :returns: None.
    """

    # if you selected a bunch of them, default to all
    containers = "" if not args.args else ' '.join(args.args)

    # if there can be only one, default to wisbox
    container = "wis2box-management" if not args.args else ' '.join(args.args)

    if args.command == "config":
        run(args, split(f'docker-compose {DOCKER_COMPOSE_ARGS} config'))
    elif args.command == "build":
        run(args, split(
            f'docker-compose {DOCKER_COMPOSE_ARGS} build {containers}'))
    elif args.command in ["up", "start", "start-dev"]:
        run(args, split(
            'docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions > /dev/null 2>&1'))
        run(args, split(
            'docker plugin enable loki'))
        if containers:
            run(args, split(f"docker-compose {DOCKER_COMPOSE_ARGS} start {containers}"))
        else:
            if args.command == 'start-dev':
                run(args, split(f'docker-compose {DOCKER_COMPOSE_ARGS} --file docker-compose.dev.yml up'))
            else:
                run(args, split(f'docker-compose {DOCKER_COMPOSE_ARGS} up -d'))
    elif args.command == "execute":
        run(args, ['docker', 'exec', '-i', 'wis2box-management', 'sh', '-c', containers])
    elif args.command == "login":
        run(args, split(f'docker exec -it {container} /bin/bash'))
    elif args.command == "login-root":
        run(args, split(f'docker exec -u -0 -it {container} /bin/bash'))
    elif args.command == "logs":
        run(args, split(
            f'docker-compose {DOCKER_COMPOSE_ARGS} logs --follow {containers}'))
    elif args.command in ["stop", "down"]:
        if containers:
            run(args, split(f"docker-compose {DOCKER_COMPOSE_ARGS} {containers}"))
        else:
            run(args, split(
                f'docker-compose {DOCKER_COMPOSE_ARGS} down --remove-orphans {containers}'))
    elif args.command == "update":
        run(args, split(f'docker-compose {DOCKER_COMPOSE_ARGS} pull'))
    elif args.command == "prune":
        run(args, split('docker builder prune -f'))
        run(args, split('docker container prune -f'))
        run(args, split('docker volume prune -f'))
        _ = run(args,
                split('docker images --filter dangling=true -q --no-trunc'),
                asciiPipe=True)
        run(args, split(f'docker rmi {_}'))
        _ = run(args, split('docker ps -a -q'), asciiPipe=True)
        run(args, split(f'docker rm {_}'))
    elif args.command == "restart":
        if containers:
            run(args, split(
                f'docker-compose {DOCKER_COMPOSE_ARGS} stop {containers}'))
            run(args, split(
                f'docker-compose {DOCKER_COMPOSE_ARGS} start {containers}'))
        else:
            run(args, split(
                f'docker-compose {DOCKER_COMPOSE_ARGS} down --remove-orphans'))
            run(args, split(
                f'docker-compose {DOCKER_COMPOSE_ARGS} up -d'))
    elif args.command == "status":
        run(args, split(
            f'docker-compose {DOCKER_COMPOSE_ARGS} ps {containers}'))
    elif args.command == "lint":
        files = walk_path(".")
        run(args, ('python3', '-m', 'flake8', *files))


if __name__ == "__main__":
    make(args)
