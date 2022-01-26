#! /bin/bash

set -e

echo 'Running tests....'
coverage run -m pytest app

echo 'Running report and sending to coveralls....'
coverage report -m
coveralls
