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
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

import arrow
import taxii2client
import typer
import yaml
from cabby import Client10, Client11
from cabby import create_client as create_taxii1_client
from cbc_sdk import CBCloudAPI
from taxii2client.v20 import Server as create_taxii20_client
from taxii2client.v21 import Server as create_taxii21_client
from typer import Argument, Option

from cbc_importer import __version__
from cbc_importer.importer import process_iocs
from cbc_importer.stix_parsers.v1.parser import STIX1Parser
from cbc_importer.stix_parsers.v2.parser import STIX2Parser
from cbc_importer.utils import transform_date, validate_provider_url, validate_severity

DEBUG = True

if DEBUG:
    # Providing a rich traceback for errors
    from rich.traceback import install

    install(show_locals=True)

DEFAULT_CONFIG_PATH = Path(__file__).parent.resolve() / "config.yml"


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)

app = typer.Typer(no_args_is_help=True)


def init_cbcsdk(cbc_profile_name: str) -> CBCloudAPI:
    """Return CBCLoudAPI instance

    Returns:
        CBCloudAPI: A reference to the CBCloudAPI object.
    """
    return CBCloudAPI(profile=cbc_profile_name, integration_name=("STIX/TAXII " + __version__))


def _get_only_set_values(values: list, dict_: dict) -> dict:
    """Getting only the set values in a dict

    Args:
        values (list): Passed values that should exists in `dict_`
        dict_ (dict): The dictionary with all the values

    Returns:
        dict: only with the values from `values`
    """
    config = {}
    for i in values:
        try:
            config[i] = dict_[i]
        except KeyError:
            continue
    return config


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


def connect_taxii1_server(config: dict) -> Union[Client10, Client11]:
    """Configuring and creating a TAXII 1.x Client instance

    Args:
        config (dict): The configuration for the TAXII Client

    Returns:
        Union[Client10, Client11]: TAXII Client instance
    """
    # Removing unset keys
    for key in list(config.keys()):
        if not config[key]:
            del config[key]

    taxii_client_keys = [
        "host",
        "port",
        "discovery_path",
        "use_https",
        "discovery_url",
        "headers",
    ]

    authentication_keys = ["username", "password", "jwt_auth_url", "cert_file", "key_file"]

    taxii_config = _get_only_set_values(taxii_client_keys, config)
    taxii_auth_config = _get_only_set_values(authentication_keys, config)

    if taxii_auth_config:
        taxii_client = create_taxii1_client(**taxii_config)
        taxii_client.set_auth(**taxii_auth_config)
    else:
        taxii_client = create_taxii1_client(**taxii_config)

    if config.get("http_proxy_url", None):
        taxii_client.set_proxies(config["http_proxy_url"])
    elif config.get("https_proxy_url", None):
        taxii_client.set_proxies(config["https_proxy_url"])

    return taxii_client


def connect_taxii2_server(config: dict, stix_version: float) -> Union[taxii2client.v20.Server, taxii2client.v21.Server]:
    """Configuring and creating a TAXII 2.0/2.1 Client instance

    Note: The config file contains `host` param, but the TAXII Client accepts it as `url`,
    same applies for `user` and `username`.

    Args:
        config (dict): The configuration for the TAXII Client
        stix_version (float): The version of STIX

    Returns:
        Union[taxii2client.v20.Server, taxii2client.v21.Server]: TAXII Client instance
    """
    # Removing unset keys
    for key in list(config.keys()):
        if not config[key]:
            del config[key]

    taxii_client_keys = [
        "host",
        "proxies",
        "verify",
        "username",
        "password",
        "cert",
    ]

    taxii_config = _get_only_set_values(taxii_client_keys, config)

    url = taxii_config.pop("host")
    user = taxii_config.pop("username")

    if stix_version == 2.0:
        taxii_client = create_taxii20_client(url=url, user=user, **taxii_config)
    else:
        taxii_client = create_taxii21_client(url=url, user=user, **taxii_config)
    return taxii_client


def process_taxii1_server(config: dict, cbcsdk: CBCloudAPI, server_name: str) -> None:
    """Processing a TAXII 1.x Server, parsing IOCs and loading them
    into a feed.

    Args:
        config (dict): The configuration for the TAXII Client
        cbcsdk (CBCloudAPI): The Authenticated instance of CBC
        server_name (str): The name of the TAXII Server
    """
    start_date, end_date = get_default_time_range_taxii1(config)
    taxii_client = connect_taxii1_server(config)
    iocs = STIX1Parser(cbcsdk).parse_taxii_server(
        taxii_client, config["collections"], begin_date=start_date, end_date=end_date
    )
    feeds = process_iocs(
        cbcsdk,
        iocs,
        config["cbc_config"]["feed_base_name"],
        config["version"],
        start_date=arrow.get(start_date).format("YYYY-MM-DD HH:mm:ss ZZ"),
        end_date=arrow.get(end_date).format("YYYY-MM-DD HH:mm:ss ZZ"),
        provider_url=config["host"],
        summary=config["cbc_config"]["summary"],
        category=config["cbc_config"]["category"],
        severity=config["cbc_config"]["severity"],
    )
    logging.info(f"Successfully imported {server_name} into CBC.")
    for i in feeds:
        logging.info(f"Created feed with ID: {i.id}")
    logging.info(f"Created {len(feeds)} Feeds.")


def process_taxii2_server(config: dict, cbcsdk: CBCloudAPI, server_name: str, stix_version: float) -> None:
    """Processing a TAXII 2.0/2.1 Server, parsing IOCs and loading them
    into a feed.

    Args:
        config (dict): The configuration for the TAXII Client
        cbcsdk (CBCloudAPI): Authenticated instance of CBC
        server_name (str): The name of the TAXII Server
        stix_version (float): The version of STIX
    """
    added_after = get_default_time_range_taxii2(config)

    taxii_client = connect_taxii2_server(config, stix_version)
    iocs = STIX2Parser(cbcsdk).parse_taxii_server(taxii_client, config["api_routes"], added_after=added_after)
    feeds = process_iocs(
        cbcsdk,
        iocs,
        config["cbc_config"]["feed_base_name"],
        config["version"],
        start_date=arrow.get(added_after).format("YYYY-MM-DD HH:mm:ss ZZ"),
        end_date=arrow.utcnow().format("YYYY-MM-DD HH:mm:ss ZZ"),
        provider_url=config["host"],
        summary=config["cbc_config"]["summary"],
        category=config["cbc_config"]["category"],
        severity=config["cbc_config"]["severity"],
    )
    logging.info(f"Successfully imported {server_name} into CBC.")
    for i in feeds:
        logging.info(f"Created feed with ID: {i.id}")
    logging.info(f"Created {len(feeds)} Feeds.")


def get_default_time_range_taxii2(config: dict) -> datetime:
    """Getting the default `added_after` date for TAXII 2 Server

    Args:
        config (dict): The configuration dictionary

    Returns:
        datetime: The `added_after` value
    """
    if config.get("added_after", None):
        added_after = arrow.get(config["added_after"], tzinfo="UTC").datetime
    else:
        # Set the default to be a month ago
        added_after = arrow.utcnow().shift(months=-1).datetime

    return added_after


def get_default_time_range_taxii1(config: dict) -> Tuple[datetime, datetime]:
    """Get the default time range for TAXII 1 Server

    Args:
        config (dict): The configuration dictionary

    Returns:
        datetime, datetime: Tuple of `start_date` and `end_date`
    """
    if config.get("start_date", None) and config.get("start_date", None):
        start_date = arrow.get(config["start_date"], tzinfo="UTC").datetime
        end_date = arrow.get(config["end_date"], tzinfo="UTC").datetime
    else:
        # Set the default range to be (now-1month to now)
        start_date = arrow.utcnow().shift(months=-1).datetime
        end_date = arrow.utcnow().datetime

    return start_date, end_date


@app.command(
    help="""
    Process and import a single STIX content file into CBC `Accepts *.json (STIX 2.1/2.0) / *.xml (1.x)`

    Example usage:

        python main.py process-file ./stix_content.xml http://yourprovider.com/

        python main.py process-file ./stix_content.xml http://yourprovider.com/ --start-date=2022-01-01 --end-date=2022-02-01

        python main.py process-file ./stix_content.xml -http://yourprovider.com/ --severity=9

    """
)
def process_file(
    stix_file_path: str = Argument(None, help="The location of the STIX Content file."),
    provider_url: str = Argument(None, help="The URL of the provider of the content.", callback=validate_provider_url),
    start_date: Optional[str] = Option(
        f"{arrow.utcnow().shift(months=-1).format()}",
        help="The start date of the STIX Content, The format should be ISO 8601",
        callback=transform_date,
    ),
    end_date: Optional[str] = Option(
        f"{arrow.utcnow().format()}",
        help="The end date of the STIX Content, The format should be ISO 8601",
        callback=transform_date,
    ),
    severity: Optional[int] = Option(5, help="The severity of the generated Reports", callback=validate_severity),
    summary: Optional[str] = Option("...", help="Summary of the feed"),
    category: Optional[str] = Option("STIX", help="The category that the feed will have"),
    cbc_profile: Optional[str] = Option("default", help="The CBC Profile set in the CBC Credentials"),
    feed_base_name: str = Option("STIX Feed", help="The base name for the feed that is going to be created"),
) -> None:
    """Processing a single STIX file content.

    Args:
        stix_file_path (str): the path to the file
        provider_url (str): An url of the provider of that STIX content
        start_date (Optional[str]): The start date of the script
        end_date (Optional[str]): The end date of the script
        severity (Optional[int]): The severity of the reports that are going to be imported
        summary (Optional[str]): Summary of the Feed
        category (Optional[str]): The category of the Feed
        cbc_profile (Optional[str]): The CBC Profile set in the CBC Credentials
        feed_base_name (str, optional): The base name for the feed that is going to be created

    Raises:
        ValueError: If the `stix_file_path` has invalid extension
    """
    extension = os.path.splitext(stix_file_path)[1]
    cbcsdk = CBCloudAPI(profile=cbc_profile)

    kwargs = {
        "stix_file_path": stix_file_path,
        "provider_url": provider_url,
        "start_date": start_date,
        "end_date": end_date,
        "severity": severity,
        "summary": summary,
        "category": category,
        "feed_base_name": feed_base_name,
        "cb": cbcsdk,
    }

    if extension == ".xml":
        process_stix1_file(**kwargs)
    elif extension == ".json":
        process_stix2_file(**kwargs)
    else:
        raise ValueError(f"Invalid extension: `{extension}`")


@app.command(
    help="""
    Process and import a TAXII Server (2.0/2.1/1.x)

    Example usage:

        python main.py process-server --config-file=./config.yml


    """
)
def process_server(config_file: str = Option(DEFAULT_CONFIG_PATH, help="The configuration of the servers")) -> None:
    """Processing a TAXII Server

    Args:
        config_file (str, optional): configuration file for the server, uses default config path if none provided

    Raises:
        ValueError: Whenever a STIX Version is incompatible
    """
    config = yaml.safe_load(Path(config_file).read_text())

    cbcsdk = init_cbcsdk(config["cbc_profile_name"])

    for site in config["sites"]:
        server_name = site["name"]
        logger.info(f"Processing {server_name}")
        stix_version = site["version"]
        enabled = site["enabled"]
        if enabled:
            if stix_version == 1.2:
                process_taxii1_server(site, cbcsdk, server_name)
            elif stix_version == 2.1 or stix_version == 2.0:
                process_taxii2_server(site, cbcsdk, server_name, stix_version)
            else:
                raise ValueError("Invalid STIX Version")
        else:
            logger.info(f"{server_name} is not enabled, skipping")


@app.command(help="Shows the version of the connector")
def version():
    """Shows the version of the connector in the cli

    Raises:
        typer.Exit
    """
    typer.echo(__version__)
    raise typer.Exit()


if __name__ == "__main__":
    app()
