.PHONY: clean-pyc clean-build docs clean

help:
	@echo "setup - basic setup and installation"
	@echo "dev-setup - basic setup and installation for developers"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "run - Start BigchainDB for development"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

setup:
	pip install -U pip setuptools
	pip install .

dev-setup:
	mkdir -p docs/_static
	pip install -U pip setuptools
	pip install -e .[dev]

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +

run:
	rm -r rethinkdb_data || true
	bigchaindb --dev-start-rethinkdb --dev-allow-temp-keypair start

test:
	python setup.py test

coverage:
	coverage run --source prov2bigchaindb setup.py test
	coverage report -m
	coverage html

docs:
	$(MAKE) -C docs clean
	sphinx-apidoc -o docs prov2bigchaindb prov2bigchaindb/tests/*
	sphinx-build -a -b html -d docs/build/doctrees docs/ docs/build/html

docs-travis:
	$(MAKE) -C docs clean
	./.travis_docs.sh

release: clean
	python setup.py sdist upload -r pypi

dist: clean
	python setup.py sdist
