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

"""Tests for wizard."""
import pytest
from cbc_sdk.credential_providers.default import default_provider_object
from cbc_sdk.credentials import Credentials

from tests.fixtures.cbc_sdk_credentials_mock import MockCredentialProvider
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_mock_responses import FEED_GET_RESP
from wizard import CBCloudAPI, main


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
    creds = Credentials({"url": "https://example.com", "token": "ABCDEFGHIJKLM", "org_key": "A1B2C3D4"})
    mock_provider = MockCredentialProvider({"default": creds})
    monkeypatch.setattr(default_provider_object, "get_default_provider", lambda x: mock_provider)
    return CBCloudAPI(profile="default")


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch, cb):
    """Mock CBC SDK for unit tests."""
    return CBCSDKMock(monkeypatch, cb)


# ==================================== UNIT TESTS BELOW ====================================


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
    monkeypatch.setattr("wizard.get_cb", lambda: cbcsdk_mock.api)
    called = False
    dump_called = False
    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds/90TuDxDYQtiGyg5qhwYCg", FEED_GET_RESP)

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
                    "cbc_config": {
                        "category": "STIX Feed",
                        "summary": "STIX Feed",
                        "severity": 5,
                        "feed_id": "90TuDxDYQtiGyg5qhwYCg",
                    },
                    "name": "my_site_name_1",
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1",
                    "host": "site.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "use_https": True,
                    "cert_file": None,
                    "key_file": None,
                    "collections": ["collection1"],
                    "start_date": None,
                    "end_date": None,
                    "ca_cert": None,
                    "proxy": {
                        "http": "http://proxy:8080",
                        "https": "http://proxy:8080"
                    },
                    "username": "guest",
                    "password": "guest",
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
                "feed_id": "90TuDxDYQtiGyg5qhwYCg",
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
                "http_proxy_url": "http://proxy:8080",
                "https_proxy_url": "http://proxy:8080",
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
    """Test generate config - successful case"""
    called = -1
    dump_called = False

    def generate_config_input(the_prompt=""):
        inputs = [
            "2",
            "",
            "y",
            "1",
            "",
            "",
            "6",
            "someid",
            "my_site_name_1",
            "",
            "",
            "basename",
            "wrong",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "",
            "",
            "",
            "*",
            "",
            "",
            "",
            "y",
            "http://some:8080",
            "",
            "",
            "y",
            "2",
            "",
            "",
            "",
            "",
            "my_site_name_2",
            "",
            "",
            "basename2",
            "site2.com",
            "y",
            "my_api_route",
            "col1 col2",
            "",
            "",
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
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 6, "feed_id": "someid"},
                    "name": "my_site_name_1",
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "basename",
                    "host": "site2.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "use_https": True,
                    "cert_file": None,
                    "key_file": None,
                    "collections": "*",
                    "start_date": None,
                    "end_date": None,
                    "ca_cert": None,
                    "proxy": {'http': 'http://some:8080', 'https': 'http://some:8080'},
                    "username": "guest",
                    "password": "guest",
                },
                {
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_site_name_2",
                    "version": 2.0,
                    "enabled": True,
                    "feed_base_name": "basename2",
                    "host": "site2.com",
                    "api_routes": {"my_api_route": ["col1", "col2"]},
                    "username": "guest",
                    "password": "guest",
                    "added_after": None,
                },
            ],
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


def test_update_config_add_new_site(monkeypatch):
    """Test update config - add new site - successful case"""
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                "name": "my_site_name_1",
                "version": 1.2,
                "enabled": True,
                "feed_base_name": "base_name",
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "use_https": True,
                "cert_file": None,
                "key_file": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
                "start_date": None,
                "end_date": None,
                "ca_cert": None,
                "proxy": {},
                "username": "guest",
                "password": "guest",
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
            "2",
            "",
            "",
            "",
            "",
            "my_second_site",
            "",
            "",
            "base_name_2",
            "site2.com",
            "y",
            "my_api_route",
            "*",
            "",
            "",
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
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_site_name_1",
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "host": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "use_https": True,
                    "cert_file": None,
                    "key_file": None,
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": None,
                    "end_date": None,
                    "ca_cert": None,
                    "proxy": {},
                    "username": "guest",
                    "password": "guest",
                },
                {
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_second_site",
                    "version": 2.0,
                    "enabled": True,
                    "feed_base_name": "base_name_2",
                    "host": "site2.com",
                    "api_routes": {"my_api_route": "*"},
                    "username": "guest",
                    "password": "guest",
                    "added_after": None,
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


def test_update_config_add_new_site_no_api_routes(monkeypatch):
    """Test update config - add new site, but no api routes provided"""
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                "name": "my_site_name_1",
                "version": 1.2,
                "enabled": True,
                "feed_base_name": "base_name",
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "use_https": True,
                "cert_file": None,
                "key_file": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
                "start_date": None,
                "end_date": None,
                "ca_cert": None,
                "proxy": {},
                "username": "guest",
                "password": "guest",
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
            "2",
            "",
            "",
            "",
            "",
            "my_second_site",
            "",
            "",
            "base_name_2",
            "site2.com",
            "",
            "",
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
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_site_name_1",
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "host": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "use_https": True,
                    "cert_file": None,
                    "key_file": None,
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": None,
                    "end_date": None,
                    "ca_cert": None,
                    "proxy": {},
                    "username": "guest",
                    "password": "guest",
                },
                {
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_second_site",
                    "version": 2.0,
                    "enabled": True,
                    "feed_base_name": "base_name_2",
                    "host": "site2.com",
                    "api_routes": {},
                    "username": "guest",
                    "password": "guest",
                    "added_after": None,
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


def test_update_config_wrong_choice(monkeypatch):
    """Test update config - wrong choice"""
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                "name": "my_site_name_1",
                "version": 1.2,
                "enabled": True,
                "feed_base_name": "base_name",
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "use_https": True,
                "cert_file": None,
                "key_file": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
                "start_date": None,
                "end_date": None,
                "ca_cert": None,
                "proxy": {},
                "username": "guest",
                "password": "guest",
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
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_site_name_1",
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "host": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "use_https": True,
                    "cert_file": None,
                    "key_file": None,
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": None,
                    "end_date": None,
                    "ca_cert": None,
                    "proxy": {},
                    "username": "guest",
                    "password": "guest",
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
    """Test update config, but no feed info entered"""
    load_data = {
        "cbc_profile_name": "default",
        "sites": [
            {
                "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                "name": "my_site_name_1",
                "version": 1.2,
                "enabled": True,
                "feed_base_name": "base_name",
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "use_https": True,
                "cert_file": None,
                "key_file": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
                "start_date": None,
                "end_date": None,
                "ca_cert": None,
                "proxy": {},
                "username": "guest",
                "password": "guest",
            }
        ],
    }

    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = ["3", "1", "y", "0"]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        expected_data = {
            "cbc_profile_name": "default",
            "sites": [
                {
                    "cbc_config": {"category": "STIX Feed", "summary": "STIX Feed", "severity": 5, "feed_id": None},
                    "name": "my_site_name_1",
                    "version": 1.2,
                    "enabled": True,
                    "feed_base_name": "base_name",
                    "host": "limo.anomali.com",
                    "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                    "use_https": True,
                    "cert_file": None,
                    "key_file": None,
                    "collections": ["ISO_CBC_Export_Filter_S7085"],
                    "start_date": None,
                    "end_date": None,
                    "ca_cert": None,
                    "proxy": {},
                    "username": "guest",
                    "password": "guest",
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
    """Test generate new config - no site provided"""
    called = -1
    dump_called = False

    def generate_config_input(the_prompt=""):
        inputs = ["2", "", "N"]
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
