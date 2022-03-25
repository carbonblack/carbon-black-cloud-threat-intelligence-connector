# -*- coding: utf-8 -*-

# *******************************************************
# Copyright (c) VMware, Inc. 2022. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# *******************************************************
# *
# * DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# * WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# * EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# * WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
import logging
import os.path
import sys
from pathlib import Path
from typing import Optional

import arrow
import typer
import yaml
from cbc_sdk import CBCloudAPI
from typer import Argument, Option

from cbc_importer import __version__
from cbc_importer.importer import process_iocs
from cbc_importer.stix_parsers.v1.parser import STIX1Parser
from cbc_importer.stix_parsers.v2.parser import STIX2Parser
from cbc_importer.taxii_configurator import TAXIIConfigurator
from cbc_importer.utils import transform_date, validate_provider_url, validate_severity

DEFAULT_CONFIG_PATH = Path(__file__).parent.resolve() / "config.yml"


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)

cli = typer.Typer(no_args_is_help=True)


def process_stix1_file(**kwargs) -> None:
    """Processing a STIX 1 Content file

    Args:
        kwargs (dict): All of the configuration
    """
    file_path = kwargs.pop("stix_file_path")
    iocs = STIX1Parser(kwargs["cb"]).parse_file(file_path)
    kwargs.update({"iocs": iocs, "stix_version": 1})
    feeds = process_iocs(**kwargs)
    logging.info(f"Successfully imported {file_path} into CBC.")
    for i in feeds:
        logging.info(f"Created feed with ID: {i.id}")
    logging.info(f"Created {len(feeds)} Feeds.")


def process_stix2_file(**kwargs) -> None:
    """Processing a STIX 2 Content file

    Args:
        kwargs (dict): All of the configuration
    """
    file_path = kwargs.pop("stix_file_path")
    iocs = STIX2Parser(kwargs["cb"]).parse_file(file_path)
    kwargs.update({"iocs": iocs, "stix_version": 2})
    feeds = process_iocs(**kwargs)
    logging.info(f"Successfully imported {file_path} into CBC.")
    for i in feeds:
        logging.info(f"Created feed with ID: {i.id}")
    logging.info(f"Created {len(feeds)} Feeds.")


def process_taxii1_server(server_config: TAXIIConfigurator, cbcsdk: CBCloudAPI) -> None:
    """Processing a TAXII 1.x Server, parsing IOCs and loading them
    into a feed.

    Args:
        config (TAXIIConfigurator): The configuration for the TAXII Client
        cbcsdk (CBCloudAPI): The Authenticated instance of CBC
        server_name (str): The name of the TAXII Server
    """
    iocs = STIX1Parser(cbcsdk).parse_taxii_server(server_config.client, **server_config.search_options)
    feeds = process_iocs(cb=cbcsdk, iocs=iocs, **server_config.cbc_feed_options)
    logging.info(f"Successfully imported {server_config.server_name} into CBC.")
    for i in feeds:
        logging.info(f"Created feed with ID: {i.id}")
    logging.info(f"Created {len(feeds)} Feeds.")


def process_taxii2_server(server_config: TAXIIConfigurator, cbcsdk: CBCloudAPI) -> None:
    """Processing a TAXII 2.0/2.1 Server, parsing IOCs and loading them
    into a feed.

    Args:
        config (TAXIIConfigurator): The configuration for the TAXII Client
        cbcsdk (CBCloudAPI): Authenticated instance of CBC
        server_name (str): The name of the TAXII Server
        stix_version (float): The version of STIX
    """
    iocs = STIX2Parser(cbcsdk).parse_taxii_server(server_config.client, **server_config.search_options)
    feeds = process_iocs(cbcsdk, iocs, **server_config.cbc_feed_options)
    logging.info(f"Successfully imported {server_config.server_name} into CBC.")
    for i in feeds:
        logging.info(f"Created feed with ID: {i.id}")
    logging.info(f"Created {len(feeds)} Feeds.")


@cli.command(
    help="""
    Process and import a single STIX content file into CBC `Accepts *.json (STIX 2.1/2.0) / *.xml (1.x)`

    Example usage:

        cbc-threat-intel process-file ./stix_content.xml http://yourprovider.com/

        cbc-threat-intel process-file ./stix_content.xml http://yourprovider.com/ --start-date=2022-01-01 --end-date=2022-02-01

        cbc-threat-intel process-file ./stix_content.xml http://yourprovider.com/ --severity=9

    """,
    no_args_is_help=True
)
def process_file(
    stix_file_path: str = Argument(None, help="The location of the STIX Content file."),
    provider_url: str = Argument(None, help="The URL of the provider of the content.", callback=validate_provider_url),
    feed_name: str = Argument(None, help="The name for the feed that is going to be created"),
    severity: Optional[int] = Option(5, help="The severity of the generated Reports", callback=validate_severity),
    summary: Optional[str] = Option("...", help="Summary of the feed"),
    category: Optional[str] = Option("STIX", help="The category that the feed will have"),
    cbc_profile: Optional[str] = Option("default", help="The CBC Profile set in the CBC Credentials"),
) -> None:
    """Processing a single STIX file content.

    Args:
        stix_file_path (str): the path to the file
        provider_url (str): An url of the provider of that STIX content
        feed_name (str): The base name for the feed that is going to be created
        severity (Optional[int]): The severity of the reports that are going to be imported
        summary (Optional[str]): Summary of the Feed
        category (Optional[str]): The category of the Feed
        cbc_profile (Optional[str]): The CBC Profile set in the CBC Credentials

    Raises:
        ValueError: If the `stix_file_path` has invalid extension
    """
    extension = os.path.splitext(stix_file_path)[1]
    cbcsdk = CBCloudAPI(profile=cbc_profile)

    kwargs = {
        "stix_file_path": stix_file_path,
        "provider_url": provider_url,
        "severity": severity,
        "summary": summary,
        "category": category,
        "feed_name": feed_name,
        "cb": cbcsdk,
    }

    if extension == ".xml":
        process_stix1_file(**kwargs)
    elif extension == ".json":
        process_stix2_file(**kwargs)
    else:
        raise ValueError(f"Invalid extension: `{extension}`")


@cli.command(
    help="""
    Process and import a TAXII Server (2.0/2.1/1.x)

    Example usage:

         cbc-threat-intel process-server --config-file=./config.yml


    """,
    no_args_is_help=True
)
def process_server(config_file: str = Option(DEFAULT_CONFIG_PATH, help="The configuration of the servers")) -> None:
    """Processing a TAXII Server

    Args:
        config_file (str, optional): configuration file for the server, uses default config path if none provided

    Raises:
        ValueError: Whenever a STIX Version is incompatible
    """
    configuration = yaml.safe_load(Path(config_file).read_text())
    cbcsdk = CBCloudAPI(profile=configuration["cbc_auth_profile"], integration_name=("STIX/TAXII " + __version__))

    for server_configuration in configuration["servers"]:
        logger.info(f"Processing {server_configuration['name']}")
        server_config = TAXIIConfigurator(server_configuration)
        if server_config.enabled:
            if server_config.version < 2.0:
                process_taxii1_server(server_config, cbcsdk)
            elif server_config.version == 2.0 or server_config.version == 2.1:
                process_taxii2_server(server_config, cbcsdk)
            else:
                raise ValueError("Invalid STIX Version")
        else:
            logger.info(f"Skipping {server_config.server_name}")


@cli.command(help="Shows the version of the connector")
def version():
    """Shows the version of the connector in the cli

    Raises:
        typer.Exit
    """
    typer.echo(__version__)
    raise typer.Exit()
    

if __name__ == "__main__":
    cli()