#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

install_requires=[
    "bigchaindb_driver~=0.3",
    "prov"
]

tests_require = [
    "BigchainDB~=1.0.0rc1",
    'coverage',
    'coveralls'
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
    author_email='martin.stoffers@dlr.de',
    url='https://github.com/DLR-SC/prov2bigchaindb',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],

    packages=find_packages(),
    package_dir={
        'prov2bigchaindb': 'prov2bigchaindb'
    },
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require + docs_require,
        'dev': tests_require + docs_require,
        'docs': docs_require,
    },

    license="Apache License 2.0",
    test_suite='prov2bigchaindb.tests',
)
