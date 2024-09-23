#! /bin/bash

set -e

echo 'Running tests....'
coverage run -m pytest tests/unit

echo 'Running report....'
coverage report -m
