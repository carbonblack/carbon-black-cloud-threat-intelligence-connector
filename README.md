# Threat Intelligence Connector for Carbon Black Cloud

This is a python project that can be used for ingesting Threat Intelligence from various STIX Feeds. The current supported versions of STIX Feeds are 1.x, 2.0 and 2.1.
It supports python >= 3.8

[![Coverage Status](https://coveralls.io/repos/github/carbonblack/carbon-black-cloud-threat-intelligence-connector/badge.svg?t=TczX1a)](https://coveralls.io/github/carbonblack/carbon-black-cloud-threat-intelligence-connector)
[![Codeship Status for carbonblack/carbon-black-cloud-threat-intelligence-connector](https://app.codeship.com/projects/73a21e3d-2c23-4fa8-a611-ada9d9849f2c/status?branch=main)](https://app.codeship.com/projects/456985)

## Installation

```shell-session
$ pip install carbon-black-cloud-threat-intelligence-connector
$ cbc-threat-intel --help
Usage: cbc-threat-intel [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create-feed       Creates a feed in CBC
  create-watchlist  Creates a Watchlist in CBC (from already created feed)
  process-file      Process and import a single STIX content file into...
  process-server    Process and import a TAXII Server (2.0/2.1/1.x)
  version           Shows the version of the connector
```

## Documentation

Visit the [developer network of Carbon Black Cloud](https://developer.carbonblack.com/reference/carbon-black-cloud/integrations/threat-intelligence-connector/) for more information of how to use the connector.

## Developing the connector

We rely on pull requests to keep this project maintained. By participating in this project, you agree to abide by the VMware [code of conduct](CODE-OF-CONDUCT.md).

### Setup

It is recommended to use Python3.8 / Python3.9 version for that project, assuming that you installed the deps with either virtualenv or poetry.

For a good code quality make sure to install the hooks from `pre-commit` as well.

```shell-session
$ pre-commit install
```

### Installation

Clone the repository

```bash
$ git clone https://github.com/carbonblack/carbon-black-cloud-threat-intelligence-connector.git
$ cd carbon-black-cloud-threat-intelligence-connector/
```

You can install this connector either via Poetry or using the `virtualenv`.

#### Using [Poetry](https://python-poetry.org/docs/)

You will need to [install poetry](https://python-poetry.org/docs/#installation) first.

To install the connector run:

```shell-session
$ poetry install
```

#### Using [virtualenv](https://virtualenv.pypa.io/en/latest/)

You will need to [install virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) first.

```bash
$ virtualenv venv
...
$ source ./venv/bin/activate
(venv) $ pip install -r requirements.txt
```

### Tests

The tests can be run with the following command:

```shell-session
$ pytest ./tests/unit/
```
For running the performance tests check out the [README](tests/performance/README.md)

### Support

1. View all API and integration offerings on the [Developer Network](https://developer.carbonblack.com) along with reference documentation, video tutorials, and how-to guides.
2. Use the [Developer Community Forum](https://community.carbonblack.com/) to discuss issues and get answers from other API developers in the Carbon Black Community.
3. Create a github issue for bugs and change requests or create a ticket with [Carbon Black Support](http://carbonblack.com/resources/support/).

### Submitting a PR

It is strongly recommended to have written tests and documentation for your changes before submitting a PR to the project. Make sure to write good commit messages as well.
