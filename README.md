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
# wi2node-ctl options
python3 wis2node-ctl.py

# view docker config
python3 wis2node-ctl.py config

# build local images
python3 wis2node-ctl.py build

# start system
python3 wis2node-ctl.py start

# login to main wis2node container
python3 wis2node-ctl.py login

# restart containers
python3 wis2node-ctl.py restart

# view upstatus
python3 wis2node-ctl.py status -a

# view logs
python3 wis2node-ctl.py  logs

# stop system
python3 wis2node-ctl.py  stop

# update images
python3 wis2node-ctl.py  update

# redeploy containers
python3 wis2node-ctl.py  up
```

## Running

- Note: run `python3 wis2node-ctl.py login` first to access the container

From command line:

```bash
# fetch version
wis2node --version

# create environment
wis2node environment create

# show environment
wis2node environment show

# create dataset topic hierarchy directories
wis2node data setup --topic-hierarchy foo.bar.baz

# display dataset topic hierarchy and directories
wis2node data info --topic-hierarchy foo.bar.baz

# process incoming data (manually/no PubSub)
wis2node data process /path/to/file.csv

# create discovery metadata control file (MCF)
# pygeometa MCF reference: https://geopython.github.io/pygeometa/reference/mcf
vi $WIS2NODE_DATADIR/data/config/foo/bar/baz/discovery-metadata.yml

# create CSV of stations
# format:
# station_name,wigos_station_identifier
vi /path/to/station_list.csv

# cache station metadata from OSCAR/Surface from a CSV of station name/WSI records
wis2node metadata station cache /path/to/station_list.csv

# publish station metadata to WMO OSCAR/Surface
wis2node metadata station publish $WIS2NODE_DATADIR/metadata/station/1.yml
wis2node metadata station publish $WIS2NODE_DATADIR/metadata/station/2.yml
wis2node metadata station publish $WIS2NODE_DATADIR/metadata/station/3.yml

# generate local station collection GeoJSON for pygeoapi publication
wis2node metadata station generate-collection

# publish dataset discovery metadata to local catalogue
wis2node metadata discovery publish foo/bar/baz

# unpublish discovery metadata to local catalogue
wis2node metadata discovery unpublish foo/bar/baz
```

## Development workflows

## Maintenance and code linting

```bash
# clean up dangling containers and images
python3 wis2node-ctl.py prune

# run a flake8 check on all Python code
python3 wis2node-ctl.py lint
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
