# PROV 2 BigchainDB

## Master branch

[![build status master branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/master/build.svg)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/commits/master)
[![coverage master branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/master/coverage.svg?job=test)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/commits/master)

## Develop branch

[![build status develop branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/develop/build.svg)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/commits/develop)
[![coverage develop branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/develop/coverage.svg?job=test)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/develop/master)

# Software Requirements

* Python 3.4 or Python 3.5
* python development libraries
* gcc and make
* local rethinkdb server
* python virtualenv package [recommended]

# User Setup

## With pip (Yet not supported)

```bash
pip install prov2bigchaindb
```

## Local build and egg installation

```bash
# Clone project and change into project folder and execute make

make setup
```


# Development Setup

## General Setup

```bash
# Clone project and change into project folder

# Create virtual environment
pyvenv env

# Activate virtual environment
source env/bin/activate

make dev-setup
```

## Start a BigchainDB-Node

```bash
make run
```

## Run Tests

```bash
# Test setup with running the test suite
make test
```

## Test Code Coverage

```bash
make coverage
```

## Build Documentation

```
# Resulting documentation can be found in docs/build/html
make docs
```

# License

See [LICENSE](./LICENSE) file

# Class Diagram

[Core model](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/blob/graph-concept/core.svg)
