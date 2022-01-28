#!/bin/sh

set -e

echo 'Running flake8....'
flake8 --docstring-convention google cbc_importer/
flake8 --docstring-convention google tests/
mypy
