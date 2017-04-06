.. _test_howto:

Testing Howto
-------------
To run the test local follow the next steps

1. Setup your env
~~~~~~~~~~~~~~~~~

.. include::  ./development.rst
    :start-after: Setup
    :end-before: Execute tests

2. Start your BigchainDB test node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tests require a running BigchainDB and RethinkDB instance.

.. code:: sh

    make run

3. Setup environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- BDB_HOST: Default: 127.0.0.1
- BDB_PORT: Default: 9984

If you like to connect to BigchainDB node, hosted on a different port and/or machine:

.. code:: sh

    BDB_HOST=127.0.0.1
    BDB_HOST=9984


4. Run your tests
~~~~~~~~~~~~~~~~~

.. code:: sh

    # Change to env
    source env/bin/activate
    #Start tests
    make test