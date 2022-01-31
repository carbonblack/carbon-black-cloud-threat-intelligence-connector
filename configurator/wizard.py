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
from typing import List

import yaml
from cbc_sdk.rest_api import CBCloudAPI
from validators import ValidationFailure, domain

from cbc_importer import __version__
from cbc_importer.utils import get_feed

CBC_PROFILE_NAME = "default"
CONFIG_FILE = "../config.yml"
OLD_CONFIG_FILE = "../config.yml"
CBC_FEED_FIELD = "feed_base_name"
EVAL_VALUES = [
    "version",
    "enabled",
    "use_https",
    "ssl_verify",
    "default_score",
    "size_of_request_in_minutes",
]

"""Helpers for entering data"""


def enter_api_routes(key: str) -> dict:
    """Helper function to enter the information about the routes.

    Example:
    {
        'title': '*',
        'title2': ['collection_id1', 'collection_id2']
    }

    Args:
        key (str): key of the property

    Returns:
        dict: dictionary with the api routes information
    """
    api_routes = {}
    answer = input(f"Would you like to enter `{key}` (y/N) ")
    if answer.upper() == "N" or not answer:
        return ""
    while True:
        api_route_title = input(f"Please enter the title for `{key}` or enter to stop: ")
        if not api_route_title:
            break
        value = input("Please enter the values for collections separated with space or `*` for all: ")
        if value == "*":
            api_routes[api_route_title] = "*"
        else:
            api_routes[api_route_title] = value.split()
    return api_routes


def enter_collections(key: str, value: str = None) -> List[str]:
    """Helper function to enter and parse the collections for v1.2

    Args:
        key (str): key of the property
        value (str): (optional) if provided will not ask for the value (used for migration,
                     where the property is present.

    Returns:
        list: list of collections
    """
    if not value:
        value = input(f"Please enter the values for `{key}` separated with space: ")
    return value.split()


def enter_and_validate_url(key: str, value: str = None) -> str:
    # if value is provided then this is migration, do not validate the url in that case
    if value:
        return value

    # no value, means normal flow
    done = False
    value = input(f"Please enter a value for `{key}`: ")
    while not done:
        result = domain(value)
        if isinstance(result, ValidationFailure):
            value = input(f"Please enter a valid value for `{key}`: ")
        else:
            done = True
    return value


TEMPLATE_SITE_DATA_V1 = {
    "version": 1.2,
    "enabled": True,
    "feed_base_name": "",
    "site": enter_and_validate_url,
    "discovery_path": "",
    "collection_management_path": "",
    "poll_path": "",
    "use_https": "",
    "ssl_verify": False,
    "cert_file": "",
    "key_file": "",
    "default_score": "",
    "collections": enter_collections,
    "start_date": "",
    "size_of_request_in_minutes": "",
    "ca_cert": "",
    "http_proxy_url": "",
    "https_proxy_url": "",
    "username": "guest",
    "password": "guest",
}

TEMPLATE_SITE_DATA_V2 = {
    "version": 2.0,
    "enabled": True,
    "feed_base_name": "",
    "site": enter_and_validate_url,
    "api_routes": enter_api_routes,
    "username": "guest",
    "password": "guest",
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
    data = {"cbc_profile_name": CBC_PROFILE_NAME, "default_severity": 5, "sites": []}

    cb = get_cb()
    # convert data to the new format
    for site_name, values in old_config["sites"].items():
        # for each site in the old config, add one item
        item_data = {site_name: copy.deepcopy(TEMPLATE_SITE_DATA_V1)}

        # add feed name instead of feed_id
        item_data[site_name]["feed_base_name"] = get_feed(cb, feed_id=values["feed_id"]).name

        for inner_key in values:
            if inner_key == "feed_id":
                continue
            if isinstance(item_data[site_name][inner_key], types.FunctionType):
                func = item_data[site_name][inner_key]
                item_data[site_name][inner_key] = func(inner_key, values[inner_key])
            elif values[inner_key]:
                item_data[site_name][inner_key] = values[inner_key]

        # add this site information
        data["sites"].append(item_data)

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False, sort_keys=False)

    print("Successfully migrated the config")


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
        if not isinstance(dvalue, types.FunctionType):
            value = input(f"Please enter value for `{key}` or press enter to use default ({dvalue}): ")
            if value:
                feed_data[key] = eval(value) if key in EVAL_VALUES else value
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
        site_name = input("Enter site name: ")
        feed_data = enter_feed_data()
        if not feed_data:
            return
        site_data = {site_name: feed_data}
        data["sites"].append(site_data)


def generate_config() -> None:
    """Create config file."""
    print("This script will lead you through the generation of the config file")
    print("=" * 80)
    cbc_profile_name = input("Enter cbc profile name or just press enter for default: ") or "default"

    default_severity = input("Enter default severity for the reports or just press enter for default (5): ") or "5"
    data = {"cbc_profile_name": cbc_profile_name, "default_severity": int(default_severity), "sites": []}
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


def main():
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
    main()
