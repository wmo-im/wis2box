# wis2node

[![Tests](https://github.com/wmo-im/wis2node/workflows/tests%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/wis2node/actions/workflows/tests.yml)
[![Docs](https://github.com/wmo-im/wis2node/workflows/docs/badge.svg)](https://github.com/wmo-im/wis2node/actions/workflows/docs.yml)

## WIS 2.0 in a box

WIS 2.0 in a box provides a platform with the capabilities for centres to
integrate their data holdings and publish them to the WMO Information System
with a plug and play capability supporting data publishing, discovery
and access.

## Installation

```bash
python3 -m venv wis2node
cd wis2node
git clone https://github.com/wmo-im/wis2node.git
cd wis2node

# setup local environment variables
cp wis2node.env dev.env
# edit/adjust accordingly
vi dev.env
```

## Deploying with Docker Compose

```bash
# build local images
make build

# start system
make up

# login to main wis2node container
make login

# view logs
make logs

# stop system
make stop

# update images
make update

# redeploy containers
make up
```

## Running

- Note: run `make login` first to access the container

From command line:
```bash
# fetch version
wis2node --version

# create text file of stations (1 WSI per line)
vi stations.txt

# cache station metadata from OSCAR/Surface from a CSV of station name/WSI records
wis2node metadata station sync /path/to/station_list.csv

# publish station metadata to WMO OSCAR/Surface
wis2node metadata station publish $WIS2NODE_DATADIR/metadata/station/1.yml
wis2node metadata station publish $WIS2NODE_DATADIR/metadata/station/2.yml
wis2node metadata station publish $WIS2NODE_DATADIR/metadata/station/3.yml

# generate local station collection GeoJSON for pygeoapi publication
wis2node metadata station generate-collection

# create discovery metadata control file (MCF)
# pygeometa MCF reference: https://geopython.github.io/pygeometa/reference/mcf
vi $WIS2NODE_DATADIR/metadata/discovery/surface-weather-observations.yml

# publish discovery metadata to local catalogue
wis2node metadata discovery publish $WIS2NODE_DATADIR/metadata/discovery/surface-weather-observations.yml

# unpublish discovery metadata to local catalogue
wis2node metadata discovery unpublish some_identifier

# process incoming data (manually/no PubSub)
wis2node data observations process /path/to/file.csv --discovery-metadata /path/to/dm.yml --station-metadata /path/to/sm.json --mappings /path/to/mappings.json
```

## Development workflows

## Maintenance and code linting

```bash
# clean up dangling containers and images
make prune

# run a flake8 check on all Python code
make flake8
```

### Running tests

```bash
# via setuptools
python3 setup.py test
# directly via pytest
pytest
```

## Releasing

```bash
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/wis2node/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
