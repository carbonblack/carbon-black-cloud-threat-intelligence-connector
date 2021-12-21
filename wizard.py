"""
Script to either migrate the old config.yml or to configure completely new.
"""
import os
import copy
import yaml

CONFIG_INI_PATH = "config.ini"
CONFIG_FILE = "config.yml"
OLD_CONFIG_FILE = "old_config.yml"
LIST_FIELDS = ["collections"]
EVAL_VALUES = [
    "version",
    "enabled",
    "use_https",
    "ssl_verify",
    "default_score",
    "size_of_request_in_minutes",
]
TEMPLATE_SITE_DATA_V1 = {
    "version": 1.2,
    "enabled": True,
    "feed_id": "",
    "site": "",
    "discovery_path": "",
    "collection_management_path": "",
    "poll_path": "",
    "use_https": "",
    "ssl_verify": False,
    "cert_file": "",
    "key_file": "",
    "default_score": "",
    "collections": [],
    "start_date": "",
    "size_of_request_in_minutes": "",
    "ca_cert": "",
    "http_proxy_url": "",
    "https_proxy_url": "",
    "username": "",
    "password": "",
}

TEMPLATE_SITE_DATA_V2 = {
    "version": 2.0,
    "enabled": True,
    "feed_id": "",
    "site": "",
    "discovery_path": "",
    "username": "",
    "password": "",
}
TEMPLATES = [TEMPLATE_SITE_DATA_V1, TEMPLATE_SITE_DATA_V2]


def migrate():
    """Migrate the old config.yml to the new format"""
    filepath = input(
        "Please enter the path to the old config or enter for default (old_config.yml): "
    )
    if filepath == "":
        filepath = OLD_CONFIG_FILE

    if not os.path.exists(filepath):
        print("The file doesn't exist!")
        return

    with open(filepath) as file:
        old_config = yaml.safe_load(file)
    data = {"config_path": CONFIG_INI_PATH, "sites": []}

    # convert data to the new format
    for key, values in old_config["sites"].items():
        # for each site in the old config, add one item
        item_data = {key: {"feeds": []}}
        item_data[key]["feeds"].append(
            {"stix_feed1": copy.deepcopy(TEMPLATE_SITE_DATA_V1)}
        )
        for inner_key in values:
            if values[inner_key] and inner_key not in LIST_FIELDS:
                item_data[key]["feeds"][0]["stix_feed1"][inner_key] = values[inner_key]

        # add collections as a list
        item_data[key]["feeds"][0]["stix_feed1"]["collections"].append(
            values["collections"]
        )
        # add this site information
        data["sites"].append(item_data)

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False, sort_keys=False)


def enter_feed_data():
    """Gather the information about the feed data

    Returns:
         dict: feed data or None if not additional feed needs to be added
    """
    print("Configure a feed:")
    print("1 Version 1.2")
    print("2 Version 2.0 or 2.1")
    print("0 Exit")
    version = int(input())
    if not version:
        return
    feed_name = input("Enter name for the feed:")
    feed_data = {feed_name: copy.deepcopy(TEMPLATES[version - 1])}

    for key, dvalue in TEMPLATES[version - 1].items():
        if key not in LIST_FIELDS:
            value = input(
                f"Please enter value for `{key}` or press enter to use default ({dvalue}): "
            )
            if value:
                feed_data[feed_name][key] = eval(value) if key in EVAL_VALUES else value
        else:
            value = input(f"Please enter the values for `{key}` separated with space: ")
            feed_data[feed_name][key].extend(value.split())
    return feed_data


def enter_new_site(data=None):
    """Gather the information about the new site data, including the feeds

    Args:
        data (dict): existing data for all the sites
    """
    while True:
        choice = input("Add a site (y/N) ")
        if not choice or choice.lower() == "n":
            break
        site_name = input("Enter site name: ")
        site_data = {site_name: {"feeds": []}}
        while True:
            feed_data = enter_feed_data()
            if not feed_data:
                break
            site_data[site_name]["feeds"].append(feed_data)

        data["sites"].append(site_data)


def generate_config():
    """Create config file"""
    print("This script will lead you through the generation of the config file")
    print("=" * 80)

    data = {"config_path": CONFIG_INI_PATH, "sites": []}
    enter_new_site(data)

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False, sort_keys=False)


def update_config():
    """Update config of the new structure"""
    with open(CONFIG_FILE) as file:
        config_data = yaml.safe_load(file)

    print("1 Add new site")
    print("2 Add feeds to existing site")
    choice = int(input())

    if choice == 1:
        enter_new_site(config_data)
    elif choice == 2:
        map_index_to_name = {}
        for i, item in enumerate(config_data["sites"]):
            site_name = list(item.keys())[0]
            map_index_to_name[i] = site_name
            print(f"{i + 1} Add feeds to {site_name}")
        print("0 Exit")
        site_choice = input()
        if not site_choice or site_choice == "0" or not site_choice.isalnum() or int(site_choice) > i + 1:
            return

        while True:
            feed_data = enter_feed_data()
            if not feed_data:
                break
            config_data["sites"][int(site_choice) - 1][
                map_index_to_name[int(site_choice) - 1]
            ]["feeds"].append(feed_data)

    with open(CONFIG_FILE, "w") as new_config:
        yaml.dump(config_data, new_config, default_flow_style=False, sort_keys=False)


def main():
    """Main menu to migrate or create/update config"""
    print("1 Migrate old config")
    print("2 Create new config")
    print("3 Update config")
    print("0 Exit")
    choice = int(input())
    if choice == 1:
        migrate()
    elif choice == 2:
        generate_config()
    elif choice == 3:
        update_config()
    else:
        return


if __name__ == "__main__":
    main()
