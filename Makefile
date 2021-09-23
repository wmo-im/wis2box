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

DOCKER_COMPOSE_ARGS=-f docker/docker-compose.yml -f docker/docker-compose.override.yml

help:
	@echo
	@echo " - build: build local Docker image"
	@echo " - up: start system"
	@echo " - down: stop system"
	@echo " - prune: cleanup dangling containers and images"
	@echo " - flake8: run PEP8 checks against local Python code"
	@echo
    
build:
	docker-compose $(DOCKER_COMPOSE_ARGS) build wis2node_app

up:
	docker-compose $(DOCKER_COMPOSE_ARGS) up -d

down:
	docker-compose $(DOCKER_COMPOSE_ARGS) down

prune:
	docker container prune
	docker rmi $(docker images --filter "dangling=true" -q --no-trunc)

flake8:
	find . -type f -name "*.py" | xargs flake8

.PHONY: help build up down prune flake8
