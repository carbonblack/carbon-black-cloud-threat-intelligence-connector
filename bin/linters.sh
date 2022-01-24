#!/bin/sh

set -e

echo 'Running flake8....'
flake8 --docstring-convention google src/
