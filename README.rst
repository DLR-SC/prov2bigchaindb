PROV 2 BigchainDB
=======================

Introduction
------------

.. image:: https://badge.fury.io/py/prov2bigchaindb.svg
    :target: https://pypi.python.org/pypi/prov2bigchaindb
    :alt: PyPI version
.. image:: https://readthedocs.org/projects/prov2bigchaindb/badge/?version=latest
    :target: http://prov2bigchaindb.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://travis-ci.org/DLR-SC/prov2bigchaindb.svg?branch=master
    :target: https://travis-ci.org/DLR-SC/prov2bigchaindb
    :alt: Build Status
.. image:: https://coveralls.io/repos/github/DLR-SC/prov2bigchaindb/badge.svg?branch=master
    :target: https://coveralls.io/github/DLR-SC/prov2bigchaindb?branch=master
    :alt: Coverage Status
.. image:: https://www.quantifiedcode.com/api/v1/project/00b76af4d7d747ee8dd0a6e4a5fa4ce5/badge.svg
    :target: https://www.quantifiedcode.com/app/project/00b76af4d7d747ee8dd0a6e4a5fa4ce5
    :alt: Code issues
.. image:: https://pyup.io/repos/github/DLR-SC/prov2bigchaindb/shield.svg
    :target: https://pyup.io/repos/github/DLR-SC/prov2bigchaindb/
    :alt: Updates
.. image:: https://zenodo.org/badge/87302481.svg
   :target: https://zenodo.org/badge/latestdoi/87302481

This python module provides three different clients to save `W3C-PROV <https://www.w3.org/TR/prov-overview/>`_ documents into a federation of `BigchainDB <https://www.bigchaindb.com/>`_ nodes.
All clients are implemented with respect to the proposed concepts from the masters thesis `Trustworthy Provenance Recording using a blockchain-like database <http://elib.dlr.de/111772/>`_.

See full documentation at: `prov2bigchaindb.readthedocs.io <http://prov2bigchaindb.readthedocs.io>`_

Software Requirements
~~~~~~~~~~~~~~~~~~~~~

* Python 3.5 or Python 3.6
* Python development libraries
* GCC and Make
* A local rethinkdb server

Installation
------------

PyPi
~~~~

Install it by running::

    pip install prov2bigchaindb

You can view `prov2bigchaindb on PyPi's package index <https://pypi.python.org/pypi/prov2bigchaindb/>`_

Source
~~~~~~

.. code:: sh

    # Clone project
    git clone git@github.com:DLR-SC/prov2bigchaindb.git
    cd prov2bigchaindb

    # Setup virtual environment
    pyenv env
    source env/bin/activate

    # Install dependencies and package into virtual enviroment
    make setup

Usage
-----

DocumentConceptClient
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from prov2bigchaindb.tests.core import setup_test_files
    from prov2bigchaindb.core import utils, clients

    test_prov_files = setup_test_files()
    prov_document = utils.to_prov_document(content=test_prov_files["simple2"])
    doc_client = clients.DocumentConceptClient(account_id="ID", host="127.0.0.1", port=9984)

    # Store a document
    tx_id = doc_client.save_document(prov_document)

    # Retrieve a document
    doc = doc_client.get_document(tx_id)


GraphConceptClient
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from prov2bigchaindb.tests.core import setup_test_files
    from prov2bigchaindb.core import utils, clients

    test_prov_files = setup_test_files()
    prov_document = utils.to_prov_document(content=test_prov_files["simple2"])
    graph_client = clients.GraphConceptClient(host="127.0.0.1", port=9984)

    # Store a document
    tx_ids = graph_client.save_document(prov_document)

    # Retrieve a document
    doc = graph_client.get_document(tx_ids)


RoleConceptClient
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from prov2bigchaindb.tests.core import setup_test_files
    from prov2bigchaindb.core import utils, clients

    test_prov_files = setup_test_files()
    prov_document = utils.to_prov_document(content=test_prov_files["simple2"])
    role_client = clients.RoleConceptClient(host="127.0.0.1", port=9984)

    # Store a document
    tx_ids = role_client.save_document(prov_document)

    # Retrieve a document
    doc = role_client.get_document(tx_ids)

License
-------

See `LICENSE <https://github.com/DLR-SC/prov2bigchaindb/blob/master/LICENSE>`_ file

