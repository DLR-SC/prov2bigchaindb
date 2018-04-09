Development
===========

Contribute
----------

Please, fork the code on Github and develop your feature in a new branch split from the develop branch.
Commit your code to the main project by sending a pull request onto the develop branch

* Issue Tracker: https://github.com/DLR-SC/prov2bigchaindb/issues
* Source Code: https://github.com/DLR-SC/prov2bigchaindb

Setup
-----

.. code:: sh

    # Clone project
    git clone git@github.com:DLR-SC/prov2bigchaindb.git
    cd prov2bigchaindb

    # Setup virtual environment
    python -m venv env
    source env/bin/activate

    # Install dependencies
    make dev-setup

Execute tests
-------------

.. code:: sh

    make test

Coverage report
---------------

.. code:: sh

    make coverage

Compile documentation
---------------------

.. code:: sh

    make docs