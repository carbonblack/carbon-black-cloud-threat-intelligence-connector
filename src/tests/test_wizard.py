# -*- coding: utf-8 -*-

# *******************************************************
# Copyright (c) VMware, Inc. 2020-2021. All Rights Reserved.
# SPDX-License-Identifier: MIT
# *******************************************************
# *
# * DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# * WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# * EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# * WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

"""Tests for wizard."""
import pytest

from tests.fixtures.cbc_sdk_mock_responses import FEED_GET_RESP
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_credentials_mock import MockCredentialProvider
from cbc_sdk.credential_providers.default import default_provider_object

from src.cli.wizard import main, get_cb, CBCloudAPI
from cbc_sdk.credentials import Credentials


class MockFileManager:
    """Mock class for the opening a file."""

    def __enter__(self):
        """Open file."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close file."""
        ...


def open_file_mock(*args, **kwargs):
    """Open file mock."""
    return MockFileManager()


@pytest.fixture(scope="function")
def cb(monkeypatch):
    """Create CBCloudAPI singleton."""
    creds = Credentials(
        {"url": "https://example.com", "token": "ABCDEFGHIJKLM", "org_key": "A1B2C3D4"}
    )
    mock_provider = MockCredentialProvider({"default": creds})
    monkeypatch.setattr(
        default_provider_object, "get_default_provider", lambda x: mock_provider
    )
    return CBCloudAPI(profile="default")


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch, cb):
    """Mock CBC SDK for unit tests."""
    return CBCSDKMock(monkeypatch, cb)


def test_get_cb():
    """Test get_cb"""
    obj = get_cb()
    assert isinstance(obj, CBCloudAPI)


def test_migrate_file_doesnt_exist(monkeypatch):
    """Test for migration of config that doesn't exist."""
    called = False

    def migrate_input(the_prompt=""):
        nonlocal called
        if not called:
            called = True
            return "1"
        return ""

    monkeypatch.setattr("builtins.input", migrate_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    main()


def test_migrate_file_exists(monkeypatch, cbcsdk_mock):
    """Test for migrating config - success."""
    monkeypatch.setattr("src.cli.wizard.get_cb", lambda: cbcsdk_mock.api)
    called = False
    dump_called = False
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds/", FEED_GET_RESP
    )

    def migrate_input(the_prompt=""):
        nonlocal called
        if not called:
            called = True
            return "1"
        return ""

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "my_site_name_1": {
                        "version": 1.2,
                        "enabled": True,
                        "feed_base_name": "base_name",
                        "site": "site.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "collection_management_path": "/api/v1/taxii/collection_management/",
                        "poll_path": "/api/v1/taxii/poll/",
                        "use_https": "",
                        "ssl_verify": False,
                        "cert_file": "",
                        "key_file": "",
                        "default_score": "",
                        "collections": ["collection1"],
                        "start_date": "",
                        "size_of_request_in_minutes": "",
                        "ca_cert": "",
                        "http_proxy_url": "",
                        "https_proxy_url": "",
                        "username": "guest",
                        "password": "guest",
                    }
                }
            ],
        }
        nonlocal dump_called
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    old_config_data = {
        "sites": {
            "my_site_name_1": {
                "feed_id": "someid",
                "site": "site.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "collection_management_path": "/api/v1/taxii/collection_management/",
                "poll_path": "/api/v1/taxii/poll/",
                "use_https": None,
                "ssl_verify": False,
                "cert_file": None,
                "key_file": None,
                "default_score": None,
                "username": "guest",
                "password": "guest",
                "collections": "collection1",
                "start_date": None,
                "size_of_request_in_minutes": None,
                "ca_cert": None,
                "http_proxy_url": None,
                "https_proxy_url": None,
            }
        }
    }

    monkeypatch.setattr("builtins.input", migrate_input)
    monkeypatch.setattr("yaml.safe_load", lambda x: old_config_data)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("os.path.exists", lambda x: True)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called


def test_generate_config(monkeypatch):
    called = -1
    dump_called = False

    def generate_config_input(the_prompt=""):
        inputs = [
            "2",
            "",
            "y",
            "my_site_name_1",
            "1",
            "",
            "",
            "basename",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "y",
            "my_site_name_2",
            "2",
            "",
            "",
            "basename2",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "",
            "",
            "",
        ]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "my_site_name_1": {
                        "version": 1.2,
                        "enabled": True,
                        "feed_base_name": "basename",
                        "site": "site2.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
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
                        "username": "guest",
                        "password": "guest",
                    }
                },
                {
                    "my_site_name_2": {
                        "version": 2.0,
                        "enabled": True,
                        "feed_base_name": "basename2",
                        "site": "site2.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "username": "guest",
                        "password": "guest",
                    }
                },
            ],
        }
        nonlocal dump_called
        from pprint import pprint

        pprint(data)
        print("=" * 60)
        pprint(expected_data)
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", generate_config_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called


def test_update_config_add_new_site(monkeypatch):
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "my_site_name_1": {
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "site": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "collection_management_path": "/api/v1/taxii/collection_management/",
                    "poll_path": "/api/v1/taxii/poll/",
                    "use_https": "",
                    "ssl_verify": False,
                    "cert_file": "",
                    "key_file": "",
                    "default_score": "",
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": "",
                    "size_of_request_in_minutes": "",
                    "ca_cert": "",
                    "http_proxy_url": "",
                    "https_proxy_url": "",
                    "username": "guest",
                    "password": "guest",
                }
            }
        ],
    }
    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = [
            "3",
            "1",
            "y",
            "my_second_site",
            "2",
            "",
            "",
            "base_name_2",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "",
            "",
            "",
        ]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "my_site_name_1": {
                        "version": 1.2,
                        "enabled": True,
                        "feed_base_name": "base_name",
                        "site": "limo.anomali.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "collection_management_path": "/api/v1/taxii/collection_management/",
                        "poll_path": "/api/v1/taxii/poll/",
                        "use_https": "",
                        "ssl_verify": False,
                        "cert_file": "",
                        "key_file": "",
                        "default_score": "",
                        "collections": ["ISO_CBC_Export_Filter_S7085"],
                        "start_date": "",
                        "size_of_request_in_minutes": "",
                        "ca_cert": "",
                        "http_proxy_url": "",
                        "https_proxy_url": "",
                        "username": "guest",
                        "password": "guest",
                    }
                },
                {
                    "my_second_site": {
                        "version": 2.0,
                        "enabled": True,
                        "feed_base_name": "base_name_2",
                        "site": "site2.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "username": "guest",
                        "password": "guest",
                    }
                },
            ],
        }
        nonlocal dump_called
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", update_config_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called


def test_update_config_add_new_site(monkeypatch):
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "my_site_name_1": {
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "site": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "collection_management_path": "/api/v1/taxii/collection_management/",
                    "poll_path": "/api/v1/taxii/poll/",
                    "use_https": "",
                    "ssl_verify": False,
                    "cert_file": "",
                    "key_file": "",
                    "default_score": "",
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": "",
                    "size_of_request_in_minutes": "",
                    "ca_cert": "",
                    "http_proxy_url": "",
                    "https_proxy_url": "",
                    "username": "guest",
                    "password": "guest",
                }
            }
        ],
    }
    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = [
            "3",
            "1",
            "y",
            "my_second_site",
            "2",
            "",
            "",
            "base_name_2",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "",
            "",
            "",
        ]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "my_site_name_1": {
                        "version": 1.2,
                        "enabled": True,
                        "feed_base_name": "base_name",
                        "site": "limo.anomali.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "collection_management_path": "/api/v1/taxii/collection_management/",
                        "poll_path": "/api/v1/taxii/poll/",
                        "use_https": "",
                        "ssl_verify": False,
                        "cert_file": "",
                        "key_file": "",
                        "default_score": "",
                        "collections": ["ISO_CBC_Export_Filter_S7085"],
                        "start_date": "",
                        "size_of_request_in_minutes": "",
                        "ca_cert": "",
                        "http_proxy_url": "",
                        "https_proxy_url": "",
                        "username": "guest",
                        "password": "guest",
                    }
                },
                {
                    "my_second_site": {
                        "version": 2.0,
                        "enabled": True,
                        "feed_base_name": "base_name_2",
                        "site": "site2.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "username": "guest",
                        "password": "guest",
                    }
                },
            ],
        }
        from pprint import pprint

        pprint(expected_data)
        pprint(data)
        nonlocal dump_called
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", update_config_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called


def test_update_config_wrong_choice(monkeypatch):
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "my_site_name_1": {
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "site": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "collection_management_path": "/api/v1/taxii/collection_management/",
                    "poll_path": "/api/v1/taxii/poll/",
                    "use_https": "",
                    "ssl_verify": False,
                    "cert_file": "",
                    "key_file": "",
                    "default_score": "",
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": "",
                    "size_of_request_in_minutes": "",
                    "ca_cert": "",
                    "http_proxy_url": "",
                    "https_proxy_url": "",
                    "username": "guest",
                    "password": "guest",
                }
            }
        ],
    }

    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = ["3", "a"]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "my_site_name_1": {
                        "version": 1.2,
                        "enabled": True,
                        "feed_base_name": "base_name",
                        "site": "limo.anomali.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "collection_management_path": "/api/v1/taxii/collection_management/",
                        "poll_path": "/api/v1/taxii/poll/",
                        "use_https": "",
                        "ssl_verify": False,
                        "cert_file": "",
                        "key_file": "",
                        "default_score": "",
                        "collections": ["ISO_CBC_Export_Filter_S7085"],
                        "start_date": "",
                        "size_of_request_in_minutes": "",
                        "ca_cert": "",
                        "http_proxy_url": "",
                        "https_proxy_url": "",
                        "username": "guest",
                        "password": "guest",
                    }
                }
            ],
        }
        nonlocal dump_called
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", update_config_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called is False


def test_update_config_no_feed_entered(monkeypatch):
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "my_site_name_1": {
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "site": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "collection_management_path": "/api/v1/taxii/collection_management/",
                    "poll_path": "/api/v1/taxii/poll/",
                    "use_https": "",
                    "ssl_verify": False,
                    "cert_file": "",
                    "key_file": "",
                    "default_score": "",
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": "",
                    "size_of_request_in_minutes": "",
                    "ca_cert": "",
                    "http_proxy_url": "",
                    "https_proxy_url": "",
                    "username": "guest",
                    "password": "guest",
                }
            }
        ],
    }

    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = ["3", "1", "y", "my_second_site", "0", ""]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "my_site_name_1": {
                        "version": 1.2,
                        "enabled": True,
                        "feed_base_name": "base_name",
                        "site": "limo.anomali.com",
                        "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                        "collection_management_path": "/api/v1/taxii/collection_management/",
                        "poll_path": "/api/v1/taxii/poll/",
                        "use_https": "",
                        "ssl_verify": False,
                        "cert_file": "",
                        "key_file": "",
                        "default_score": "",
                        "collections": ["ISO_CBC_Export_Filter_S7085"],
                        "start_date": "",
                        "size_of_request_in_minutes": "",
                        "ca_cert": "",
                        "http_proxy_url": "",
                        "https_proxy_url": "",
                        "username": "guest",
                        "password": "guest",
                    }
                }
            ],
        }
        nonlocal dump_called
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", update_config_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called is True


def test_generate_config_no_site(monkeypatch):
    called = -1
    dump_called = False

    def generate_config_input(the_prompt=""):
        inputs = ["2", "", "n"]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [],
        }
        nonlocal dump_called
        assert data == expected_data
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", generate_config_input)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called


def test_exit(monkeypatch):
    """Test exit option."""
    called = False

    def wrong_and_exit_input():
        nonlocal called
        if called:
            return "0"
        called = True
        return "a"

    monkeypatch.setattr("builtins.input", wrong_and_exit_input)

    with pytest.raises(SystemExit):
        main()
