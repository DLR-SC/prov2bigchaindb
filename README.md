# PROV  BigchainDB

## Master branch

[![build status master branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/master/build.svg)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/commits/master)
[![coverage master branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/master/coverage.svg?job=test)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/commits/master)

## Develop branch

[![build status develop branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/develop/build.svg)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/commits/develop)
[![coverage develop branch](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/badges/develop/coverage.svg?job=test)](https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb/develop/master)

# Software Requirements

* Python 3.5 or Python 3.6
* Python development libraries
* GCC and Make
* A local rethinkdb server

# General setup

## With pip (Yet not supported)

```bash
pip install prov2bigchaindb
```

## Local build and egg installation

```bash
# Clone project and change into project folder and execute make

make setup
```

# Usage

## Example Document-Concept

```python
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

test_prov_files = setup_test_files()
prov_document = utils.to_prov_document(content=test_prov_files["simple2"])
doc_client = clients.DocumentConceptClient(account_id="ID", host="127.0.0.1", port=9984)

# Store a document
tx_id = doc_client.save_document(prov_document)

# Retrieve a document
doc = doc_client.get_document(tx_id)
```


## Example Graph-Client

```python
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

test_prov_files = setup_test_files()
prov_document = utils.to_prov_document(content=self.test_prov_files["simple2"])
graph_client = clients.GraphConceptClient(host="127.0.0.1", port=9984)

# Store a document
tx_ids = graph_client.save_document(prov_document)

# Retrieve a document
doc = graph_client.get_document(tx_ids)

```

## Example Role-Client

```python
from prov2bigchaindb.tests.core import setup_test_files
from prov2bigchaindb.core import utils, clients

test_prov_files = setup_test_files()
prov_document = utils.to_prov_document(content=self.test_prov_files["simple2"])
role_client = clients.RoleConceptClient(host=self.host, port=self.port)

# Store a document
tx_ids = role_client.save_document(prov_document)

# Retrieve a document
doc = role_client.get_document(tx_ids)
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
