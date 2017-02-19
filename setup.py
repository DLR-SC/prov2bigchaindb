#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

tests_require = [
    'coverage',
]

docs_require = [
    'Sphinx>=1.3.5',
    'recommonmark>=0.4.0',
    'sphinx-rtd-theme>=0.1.9',
    'sphinxcontrib-napoleon>=0.4.4',
    'sphinxcontrib-httpdomain>=1.5.0',
]


# get version
version = {}
with open('prov2bigchaindb/version.py') as fp:
    exec(fp.read(), version)


setup(
    name='prov2bigchaindb',
    version=version['__version__'],
    description='PROV 2 BigchainDB',
    long_description=__doc__,
    keywords=[
        'provenance', 'BigchainDB', 'blockchain', 'PROV', 'PROV-DM', 'PROV-JSON',
        'PROV-XML', 'PROV-N'
    ],
    author='Martin Stoffers',
    author_email='martin.stoffers@studserv.uni-leipzig.de',
    url='https://gitlab.fastreboot.de/Dr4k3/prov2bigchaindb',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: Apache License 2.0',
        'Programming Language :: Python 3.5',
    ],

    packages=find_packages(),
    package_dir={
        'prov2bigchaindb': 'prov2bigchaindb'
    },
    include_package_data=True,
    entry_points={
        'console_scripts': ['bigchaindbclient=prov2bigchaindb.bigchaindbclient:main'],
    },
    zip_safe=False,

    install_requires=[
        "bigchaindb",
        "bigchaindb_driver",
        "prov"
    ],# + tests_require + docs_require, # This can be removed if prov-db-connector is on pypi -> than install with "pip install '.[dev]' for development
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': tests_require + docs_require,
        'docs': docs_require,
    },

    license="Apache License 2.0",
    test_suite='prov2bigchaindb.tests',
)
