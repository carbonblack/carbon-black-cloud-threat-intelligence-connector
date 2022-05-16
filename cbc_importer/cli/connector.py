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

import typer
import yaml
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr import Feed
from typer import Argument, Option

from cbc_importer import __version__
from cbc_importer.importer import process_iocs
from cbc_importer.stix_parsers.v1.parser import STIX1Parser
from cbc_importer.stix_parsers.v2.parser import STIX2Parser
from cbc_importer.taxii_configurator import TAXIIConfigurator
from cbc_importer.utils import create_feed as utils_create_feed
from cbc_importer.utils import create_watchlist as utils_create_watchlist
from cbc_importer.utils import validate_provider_url, validate_severity

DEFAULT_CONFIG_PATH = Path(__file__).parent.resolve() / "config.yml"


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)

cli = typer.Typer(no_args_is_help=True, add_completion=False)


def process_stix1_file(**kwargs) -> None:
    """Processing a STIX 1 Content file

    Args:
        kwargs (dict): All of the configuration
    """
    file_path = kwargs.pop("stix_file_path")
    iocs = STIX1Parser(kwargs["cb"]).parse_file(file_path)
    kwargs.update({"iocs": iocs})
    process_iocs(**kwargs)
    logger.info(f"Successfully imported {file_path} into CBC.")


def process_stix2_file(**kwargs) -> None:
    """Processing a STIX 2 Content file

    Args:
        kwargs (dict): All of the configuration
    """
    file_path = kwargs.pop("stix_file_path")
    iocs = STIX2Parser(kwargs["cb"]).parse_file(file_path)
    kwargs.update({"iocs": iocs})
    process_iocs(**kwargs)
    logger.info(f"Successfully imported {file_path} into CBC.")


def process_taxii1_server(server_config: TAXIIConfigurator, cbcsdk: CBCloudAPI) -> None:
    """Processing a TAXII 1.x Server, parsing IOCs and loading them
    into a feed.

    Args:
        config (TAXIIConfigurator): The configuration for the TAXII Client
        cbcsdk (CBCloudAPI): The Authenticated instance of CBC
        server_name (str): The name of the TAXII Server
    """
    iocs = STIX1Parser(cbcsdk).parse_taxii_server(server_config.client, **server_config.search_options)
    process_iocs(cb=cbcsdk, iocs=iocs, **server_config.cbc_feed_options)
    logger.info(f"Successfully imported {server_config.server_name} into CBC.")


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
    process_iocs(cbcsdk, iocs, **server_config.cbc_feed_options)
    logger.info(f"Successfully imported {server_config.server_name} into CBC.")


@cli.command(
    help="""
    Process and import a single STIX content file into CBC `Accepts *.json (STIX 2.1/2.0) / *.xml (1.x)`

    Example usage:

        cbc-threat-intel process-file ./stix_content.xml 55IOVthAZgmQHgr8eRF9rA

        cbc-threat-intel process-file ./stix_content.xml 55IOVthAZgmQHgr8eRF9rA -s 5

        cbc-threat-intel process-file ./stix_content.xml 55IOVthAZgmQHgr8eRF9rA -c default

    """,
    no_args_is_help=True,
)
def process_file(
    stix_file_path: str = Argument(None, help="The location of the STIX Content file."),
    feed_id: str = Argument(None, help="The id of the feed"),
    severity: Optional[int] = Option(
        5, "--severity", "-s", help="The severity of the generated Reports", callback=validate_severity
    ),
    replace: Optional[bool] = Option(
        False, "--replace", "-r", help="Replacing the existing Reports in the Feed, if false it will append the results"
    ),
    cbc_profile: Optional[str] = Option(
        "default", "--cbc-profile", "-c", help="The CBC Profile set in the CBC Credentials"
    ),
) -> None:
    """Processing a single STIX file content.

    Args:
        stix_file_path (str): the path to the file
        feed_id (str): the id of the feed
        severity (Optional[int]): The severity of the reports that are going to be imported
        replace: (Optional[bool]): Replacing the existing Reports in the Feed, if false it will append the results
        cbc_profile (Optional[str]): The CBC Profile set in the CBC Credentials

    Raises:
        ValueError: If the `stix_file_path` has invalid extension
    """
    extension = os.path.splitext(stix_file_path)[1]
    cbcsdk = CBCloudAPI(profile=cbc_profile)

    kwargs = {
        "stix_file_path": stix_file_path,
        "feed_id": feed_id,
        "severity": severity,
        "replace": replace,
        "cb": cbcsdk,
    }

    if extension == ".xml":
        process_stix1_file(**kwargs)
    elif extension == ".json":
        process_stix2_file(**kwargs)
    else:
        logger.error(f"Invalid extension: `{extension}`")
        exit(1)


@cli.command(
    help="""
    Process and import a TAXII Server (2.0/2.1/1.x)

    Example usage:

        cbc-threat-intel process-server --config-file=./config.yml

    """,
    no_args_is_help=False,
)
def process_server(config_file: str = Option(DEFAULT_CONFIG_PATH, help="The configuration of the servers")) -> None:
    """Processing a TAXII Server

    Args:
        config_file (Optional[str]): configuration file for the server, uses default config path if none provided

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
            logger.info(f"Skipping {server_config.server_name}")


@cli.command(help="Shows the version of the connector")
def version():
    """Shows the version of the connector in the cli

    Raises:
        typer.Exit
    """
    typer.echo(__version__)
    raise typer.Exit()


@cli.command(
    help="""
    Creates a feed in CBC

    Example usage:

        cbc-threat-intel create-feed STIXFeed http://test.test/ empty

        cbc-threat-intel create-feed STIXFeed http://test.test/ empty -ca STIX -c default -q


    """,
    no_args_is_help=True,
)
def create_feed(
    feed_name: str = Argument(None, help="The name for the feed that is going to be created"),
    provider_url: str = Argument(None, help="The URL of the provider of the content", callback=validate_provider_url),
    summary: str = Argument(None, help="Summary of the feed"),
    category: Optional[str] = Option("STIX", "--category", "-ca", help="The category that the feed will have"),
    cbc_profile: Optional[str] = Option(
        "default", "--cbc-profile", "-c", help="The CBC Profile set in the CBC Credentials"
    ),
    quiet: Optional[bool] = Option(False, "--quiet", "-q", help="This will only print the id of the created feed"),
) -> None:
    """Creates a feed in CBC

    Args:
        feed_name (str): The name for the feed that is going to be created
        provider_url (str): The URL of the provider of the content
        summary (str): Summary of the feed
        category (Optional[str]): The category that the feed will have
        cbc_profile (Optional[str]): The CBC Profile set in the CBC Credentials
        quiet (Optional[bool]): This will only print only the id of the created feed

    Raises:
        typer.Exit
    """
    cbcsdk = CBCloudAPI(profile=cbc_profile, integration_name=("STIX/TAXII " + __version__))
    feed = utils_create_feed(cbcsdk, name=feed_name, provider_url=provider_url, summary=summary, category=category)

    if quiet:
        typer.echo(feed.id)
    else:
        typer.echo(feed)
    raise typer.Exit(0)


@cli.command(
    help="""
    Creates a Watchlist in CBC (from already created feed)

    Example usage:

        cbc-threat-intel create-watchlist 55IOVthAZgmQHgr8eRF9rA STIXWatchlist

        cbc-threat-intel create-watchlist 55IOVthAZgmQHgr8eRF9rA STIXWatchlist -d description -e -t -q

    """,
    no_args_is_help=True,
)
def create_watchlist(
    feed_id: str = Argument(None, help="The watchlist will subscribe from that feed"),
    watchlist_name: str = Argument(None, help="The name of the watchlist"),
    description: Optional[str] = Option("empty", "--description", "-d", help="The description of the watchlist"),
    enable_alerts: Optional[bool] = Option(
        False, "--enable-alerts", "-e", help="Whether alerts should be enabled for this watchlist"
    ),
    quiet: Optional[bool] = Option(False, "--quiet", "-q", help="This will only print the id of the created feed."),
    cbc_profile: Optional[str] = Option(
        "default", "--cbc-profile", "-c", help="The CBC Profile set in the CBC Credentials"
    ),
) -> None:
    """Creates a Watchlist in CBC

    Args:
        feed_id (str): The id of the Feed that is going to be subscribed from
        watchlist_name (str): The name for the watchlist that is going to be created
        description (str): Description of the Watchlist
        enable_alerts (Optional[str]): If the watchlist will generate alerts
        quiet (Optional[str]): This will only print only the id of the created watchlist
        cbc_profile (Optional[bool]): The CBC Profile set in the CBC Credentials

    Raises:
        typer.Exit
    """
    cbcsdk = CBCloudAPI(profile=cbc_profile, integration_name=("STIX/TAXII " + __version__))
    feed = cbcsdk.select(Feed, feed_id)
    watchlist = utils_create_watchlist(feed, watchlist_name, description, enable_alerts)

    if quiet:
        typer.echo(watchlist.id)
    else:
        typer.echo(watchlist)
    raise typer.Exit(0)


if __name__ == "__main__":
    raise SystemExit(cli())
