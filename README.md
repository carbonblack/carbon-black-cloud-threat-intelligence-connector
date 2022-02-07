# STIX Threat Connector for CBC

This is a python project that can be used for ingesting Threat Intelligence from various STIX Feeds. The current supported versions of STIX Feeds are 1.x, 2.0 and 2.1. 

[![Coverage Status](https://coveralls.io/repos/github/carbonblack/cbc-taxii-connector/badge.svg?t=6yDdHe)](https://coveralls.io/github/carbonblack/cbc-taxii-connector)
[![Codeship Status for carbonblack/cbc-taxii-connector](https://app.codeship.com/projects/a0c7096c-4359-48af-944a-75399f7b42f2/status?branch=main)](https://app.codeship.com/projects/455332)


## Installation

You can install this connector either via Poetry or using the `virtualenv`.

### Using [Poetry](https://python-poetry.org/docs/)

You will need to [install poetry](https://python-poetry.org/docs/#installation) first. 

To install the connector run:

```console
$ poetry install --no-dev
$ poetry run python ./main.py --help
```

Or if you don't want to type `poetry run` every time.

```console
$ poetry shell 
(cbc-taxii-connector-WePRHx-s-py3.8) $ python ./main.py --help
```

### Using [virtualenv](https://virtualenv.pypa.io/en/latest/)

You will need to [install virtualenv](https://python-poetry.org/docs/#installation) first. 

```console
$ virtualenv venv
...
$ source ./venv/bin/activate
(venv) $ pip install -r requirements.txt
...
(venv) $ python ./main.py --help
```

## Usage

### Parsing STIX Content file into CBC

You can parse a file with the connector with the `process-file` command. 

An example usage and description of that command can be found with:

```console
$ python main.py process-file --help
```

It can be as simple as: 
```console
$ python main.py process-file ./stix_content.xml --provider-url=http://yourprovider.com/
``` 

The connector will automatically figure out the STIX version for you and use its appropriate parsers (you can use json files too), all you need to do is to pass the file and the required parameters.

### Parsing a TAXII Server

You can start parsing STIX content served by a TAXII Server with the connector with the `process-server` command. 

An example usage and description of that command can be found with:

```console
$ python main.py process-server --help
```

This command will gather your config file and it will start to ingest STIX content that is served by those TAXII Servers. In the `configurator/config.yml.example` file you can find an example configuration that you can use to setup your STIX content providers. 

Alternatively if you have used our old connector you can use the `configurator/wizard.py` to migrate your old configuration into the new one. 

#### Using the configuration wizard

You can use the configuration wizard to easily manage the config.yml.

An example usage of the command:
```console
$ python wizard.py
```
This is going to provide a menu with the options:
* migrate your current config
* create new config file
* add new site/feed information

If you were using the old [config.yml](https://github.com/carbonblack/carbon-black-cloud-sdk-python/blob/master/examples/enterprise_edr/threat_intelligence/config.yml) and want to migrate it, copy the old config.yml in the root directory of your project and run the wizard using the first option. This is going to override the old config and convert it in the new format [new config](https://github.com/carbonblack/cbc-taxii-connector/blob/create-entrypoint-script/configurator/config.yml.example).

With the second option of the wizard you will be able to create a completely new config (if there was existing config.yml it will be deleted). The wizard will lead you through the configurations and values you need to provide to have a valid config. Please enable only the feeds that you would like to use.

The last option allows you to add one more site information to the existing ones. You need to have a valid config.yml in the new format with existing site/feed information in order to use it.

## Developing the connector

We rely on pull requests to keep this project maintained. By participating in this project, you agree to abide by the VMware [code of conduct](CODE-OF-CONDUCT.md).

## Setup

It is recommended to use Python3.8 / Python3.9 version for that project, assuming that you installed the deps with either virtualenv or poetry. 

If you have used poetry run the following command:

```
$ poetry install 
```

For a good code quality make sure to install the hooks from `pre-commit` as well.

```
$ pre-commit install
``` 

## Submitting a PR

It is strongly recommended to have written tests and documentation for your changes before submitting a PR to the project. Make sure to write good commit messages as well. 