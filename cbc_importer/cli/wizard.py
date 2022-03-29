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

"""Script to either migrate the old config.yml or to configure completely new."""
import copy
import os
import sys
import types
from typing import List, Union, no_type_check

import yaml
from cbc_sdk.rest_api import CBCloudAPI
from typer import BadParameter

from cbc_importer import __version__
from cbc_importer.utils import get_feed, validate_provider_url

CBC_PROFILE_NAME = "default"
CONFIG_FILE = "config.yml"
OLD_CONFIG_FILE = "config.yml"
CBC_FEED_FIELD = "feed_base_name"
EVAL_VALUES = ["version", "enabled", "use_https", "severity", "port", "replace"]

"""Helpers for entering data"""


def enter_proxy(key: str) -> dict:
    """Helper function to enter the information about the proxy settings.

    Example:
    {
        'http': '<entered_url>',
        'https': '<entered_url>',
    }

    Args:
        key (str): key of the property

    Returns:
        dict: dictionary with the proxy information
    """
    answer = input("Would you like to proxy settings (y/N) ")
    if answer.upper() == "N" or not answer:
        return {}
    else:
        http_url = input("Please enter url for the proxy: ")
        return {"http": http_url, "https": http_url}


def enter_collections(key: str, value: str = None) -> Union[List[str], str]:
    """Helper function to enter and parse the collections for v1.2

    Args:
        key (str): key of the property
        value (str): (optional) if provided will not ask for the value (used for migration,
                     where the property is present.

    Returns:
        list: list of collections or '*' for all
    """
    if not value:
        value = input(f"Please enter the values for `{key}` separated with space or * for all: ")
    return value if value == "*" else value.split()


def enter_roots(key: str) -> dict:
    """Helper function to enter the information about the roots.

    Example:
    [
        {
            "title": "Test Root Title",
            "collections: ["collection-a"]
        },
        {
            "title": "Test Root Title",
            "collections: *
        }
    ]

    Args:
        key (str): key of the property

    Returns:
        dict: dictionary with the api routes information
    """
    roots = []
    answer = input("Would you like to enter roots (y/N) ")
    if answer.upper() == "N" or not answer:
        return roots
    while True:
        title = input("Please enter the title for root or enter to stop: ")
        if title:
            root = {"title": title, "collections": enter_collections("collections")}
            roots.append(root)
        else:
            break
    return roots


def enter_and_validate_url(key: str) -> str:
    """Helper function to enter and validate site url.

    Args:
        key (str): key of the property

    Returns:
        str: the site url
    """
    done = False
    value = input(f"Please enter a value for `{key}`: ")
    while not done:
        try:
            value = validate_provider_url(value)
        except BadParameter:
            value = input(f"Please enter a valid value for `{key}`: ")
        else:
            done = True
    return value


def enter_inner_dict_info(key: str = None, value: dict = None) -> dict:
    """Helper function to enter inner dictionaries in the configuration.

    Args:
        key (str): key of the property
        value (dict): dict with the default values

    Returns:
        dict: dictionary with all the values
    """
    info = copy.deepcopy(value)
    for key, value in info.items():
        if isinstance(value, types.FunctionType):
            func = value
            info[key] = func(key)
        else:
            value = input(f"Please enter value for {key} or enter for default ({info[key]}) ")
            if value:
                info[key] = eval(value) if value and key in EVAL_VALUES else value
    return info


TEMPLATE_SITE_DATA_V1 = {
    "name": "",
    "version": 1.2,
    "enabled": True,
    "cbc_feed_options": {"feed_id": None, "severity": 5, "replace": True},
    "proxies": enter_proxy,
    "connection": {
        "host": enter_and_validate_url,
        "discovery_path": "",
        "port": None,
        "use_https": True,
        "headers": None,
        "timeout": None,
    },
    "auth": {
        "username": "guest",
        "password": "guest",
        "cert_file": None,
        "key_file": None,
        "ca_cert": None,
        "key_password": None,
        "jwt_auth_url": None,
        "verify_ssl": True,
    },
    "options": {
        "begin_date": None,
        "end_date": None,
        "collection_management_uri": None,
        "collections": enter_collections,
    },
}

TEMPLATE_SITE_DATA_V2 = {
    "name": "",
    "version": 2.0,
    "enabled": True,
    "cbc_feed_options": {"feed_id": None, "severity": 5, "replace": True},
    "connection": {"url": enter_and_validate_url},
    "proxies": enter_proxy,
    "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
    "options": {
        "added_after": None,
        "roots": enter_roots,
    },
}

TEMPLATES = [TEMPLATE_SITE_DATA_V1, TEMPLATE_SITE_DATA_V2]


def get_cb() -> CBCloudAPI:
    """Return CBCLoudAPI instance

    Returns:
        CBCloudAPI: A reference to the CBCloudAPI object.
    """
    return CBCloudAPI(profile=CBC_PROFILE_NAME, integration_name=("STIX/TAXII " + __version__))


def migrate() -> None:
    """Migrate the old config.yml to the new format."""
    filepath = input(f"Please enter the path to the old config or enter for default ({OLD_CONFIG_FILE}): ")
    if filepath == "":
        filepath = OLD_CONFIG_FILE

    if not os.path.exists(filepath):
        print("The file doesn't exist!")
        return

    with open(filepath) as file:
        old_config = yaml.safe_load(file)

    data = {"cbc_auth_profile": CBC_PROFILE_NAME, "servers": []}

    # convert data to the new format
    for site_name, values in old_config["sites"].items():
        # for each site in the old config, add one item
        item_data = copy.deepcopy(TEMPLATE_SITE_DATA_V1)
        # migrate the proxy settings
        if values.get("http_proxy_url"):
            item_data["proxies"] = {"https": values.get("http_proxy_url"), "http": values.get("http_proxy_url")}
        else:
            item_data["proxies"] = {}

        # set the name
        item_data["name"] = site_name
        # add connection information
        item_data["connection"] = {}
        # add host instead of site
        item_data["connection"]["host"] = values["site"]
        item_data["connection"]["port"] = None
        item_data["connection"]["headers"] = None
        item_data["connection"]["timeout"] = None
        item_data["connection"]["discovery_path"] = None
        item_data["connection"]["use_https"] = True

        # add severity, feed_id, replace
        item_data["cbc_feed_options"] = {}
        # add feed name instead of feed_id
        item_data["cbc_feed_options"]["feed_id"] = values["feed_id"]
        item_data["cbc_feed_options"]["severity"] = 5
        item_data["cbc_feed_options"]["replace"] = True

        for key, value in item_data.items():
            if isinstance(value, dict):
                for inner_key in item_data[key]:
                    if values.get(inner_key) and isinstance(item_data[key][inner_key], types.FunctionType):
                        func = item_data[key][inner_key]
                        item_data[key][inner_key] = func(inner_key, values[inner_key])  # type: ignore
                    elif values.get(inner_key):
                        item_data[key][inner_key] = values.get(inner_key)

        item_data["options"]["begin_date"] = values["start_date"]
        # add this site information
        data["servers"].append(item_data)  # type: ignore

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False, sort_keys=False)

    print("Successfully migrated the config")


@no_type_check
def enter_feed_data() -> dict:
    """Gather the information about the feed data.

    Returns:
         dict: feed data or None if no additional feed needs to be added
    """
    print("Configure a feed:")
    print("1 Version 1.2")
    print("2 Version 2.0 or 2.1")
    print("0 Exit")
    version = input()
    if not (version and version.isdigit() and 1 <= int(version) <= 2):
        return
    version = int(version)
    feed_data = copy.deepcopy(TEMPLATES[version - 1])

    for key, dvalue in TEMPLATES[version - 1].items():
        if isinstance(dvalue, dict):
            info = enter_inner_dict_info(value=dvalue)
            feed_data[key] = info
        elif not isinstance(dvalue, types.FunctionType):
            value = input(f"Please enter value for `{key}` or press enter to use default ({dvalue}): ")
            if value:
                feed_data[key] = eval(value) if key in EVAL_VALUES and value else value
        else:
            feed_data[key] = dvalue(key)
    return feed_data


def enter_new_site(data: dict = None) -> None:
    """Gather the information about the new site data, including the feeds.

    Args:
        data (dict): existing data for all the sites
    """
    while True:
        choice = input("Add a site (y/N) ")
        if not choice or choice.lower() == "n":
            break
        feed_data = enter_feed_data()
        if not feed_data:
            return
        data["servers"].append(feed_data)  # type: ignore


def generate_config() -> None:
    """Create config file."""
    print("This script will lead you through the generation of the config file")
    print("=" * 80)
    cbc_profile_name = input("Enter cbc profile name or just press enter for default: ") or "default"

    data = {"cbc_auth_profile": cbc_profile_name, "servers": []}
    enter_new_site(data)

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False, sort_keys=False)


def update_config() -> None:
    """Update config of the new structure."""
    with open(CONFIG_FILE) as file:
        config_data = yaml.safe_load(file)

    print("1 Add new site")
    choice = input()
    if not (choice and choice.isdigit() and int(choice) == 1):
        return
    choice = int(choice)
    if choice == 1:
        enter_new_site(config_data)

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(config_data, new_config, default_flow_style=False, sort_keys=False)


def cli():
    """Entry for the main script."""
    menu_text = [
        "1 Migrate old config",
        "2 Create new config",
        "3 Update config",
        "0 Exit",
    ]

    menu = {"0": sys.exit, "1": migrate, "2": generate_config, "3": update_config}

    print(*menu_text, sep="\n")
    choice = input()
    while choice not in menu:
        print(*menu_text, sep="\n")
        choice = input()

    menu[choice]()


if __name__ == "__main__":
    cli()
