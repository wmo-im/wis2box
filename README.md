# wis2node

[![Build Status](https://github.com/wmo-im/wis2node/workflows/flake8%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/wis2node/actions)
[![Docs](https://github.com/wmo-im/wis2node/workflows/docs/badge.svg)](https://wmo-im.github.com/wis2node)

## WIS 2.0 node in a box

WIS 2.0 node in a box provides a platform with the capabilities for centres to
integrate their data holdings and publish them to the WMO Information System
with a plug and play capability supporting data publishing, discovery
and access.

## Installation

### Docker

```bash
git clone https://github.com/wmo-im/wis2node.git
cd wis2node

# build local image
make build

# start system
make up

# view logs
make logs

# stop system
make stop

# update images
make update

# redeploy containers
make up

# clean up dangling containers and images
make prune

# run a flake8 check on all Python code
make flake8
```

## Running

From command line:
```bash
# fetch version
wis2node --version

# publish discovery metadata to local catalogue
wis2node metadata discovery publish /path/to/discovery-metadata-file.mcf

# unpublish discovery metadata to local catalogue
wis2node metadata discovery unpublish some_identifier

# publish station metadata to WMO OSCAR/Surface
wis2node metadata station publish /path/to/station-metadata-file.mcf
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
