import os
import yaml
import copy


LIST_FIELDS = ["collections"]
EVAL_VALUES = ['enabled', 'use_https', 'ssl_verify', 'default_score', 'size_of_request_in_minutes']
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
    filepath = input("Please enter the path to the old config or enter for default: ")
    if filepath == "":
        filepath = "old_config.yml"

    if not os.path.exists(filepath):
        print("The file doesn't exist!")
        return

    with open(filepath) as file:
        old_config = yaml.safe_load(file)

    data = {"sites": [], "config_path": "config.ini"}

    # convert data to the new format
    for key, values in old_config["sites"].items():
        # for each site in the old config, add one item
        item_data = {key: {"feeds": []}}
        for inner_key in values:
            item_data[key]["feeds"].append(
                {"stix_feed1": {copy.deepcopy(TEMPLATE_SITE_DATA_V1)}}
            )
            if values[inner_key] and inner_key not in LIST_FIELDS:
                item_data[key]["feeds"][0]["stix_feed1"][inner_key] = values[inner_key]

        # add collections as a list
        item_data[key]["feeds"][0]["stix_feed1"]["collections"].append(
            values["collections"]
        )
        # add this site information
        data["sites"][key]["feeds"].append(item_data)

    with open("config.yml", "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False)


def add_data(sites=None):
    if sites:
        initial = copy.deepcopy(sites)
    else:
        initial = []
    data = {"sites": initial, "config_path": "config.ini"}
    while True:
        choice = input("Add a site (y/N) ")
        if not choice or choice.lower() == "n":
            break
        site_name = input("Enter site name:")
        site_data = {site_name: {"feeds": []}}
        while True:
            print("Configure a feed:")
            print("1 Version 1.2")
            print("2 Version 2.0 or 2.1")
            print("0 Exit")
            version = int(input())
            if not version:
                break

            feed_data = copy.deepcopy(TEMPLATES[version - 1])
            for key in TEMPLATES[version - 1]:
                if key not in LIST_FIELDS:
                    value = input(
                        f"Please enter value for `{key}` or press enter to skip it: "
                    )
                    if value:
                        feed_data[key] = eval(value) if key in EVAL_VALUES else value
                else:
                    value = input(f"Please enter the values for `{key}` separated with space: ")
                    feed_data[key].extend(value.split())
            site_data[site_name]["feeds"].append(feed_data)

        data["sites"].append(site_data)

    with open("config.yml", "w") as new_config:
        yaml.dump(data, new_config, default_flow_style=False)


def generate_config():
    print("This script will lead you through the generation of the config file")
    print("=" * 40)
    add_data()


def main():
    # migrate()
    generate_config()


if __name__ == "__main__":
    main()
