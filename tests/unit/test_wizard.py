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
import copy

import pytest
from cbc_sdk.credential_providers.default import default_provider_object
from cbc_sdk.credentials import Credentials

from cbc_importer.cli.wizard import CBCloudAPI, main
from tests.fixtures.cbc_sdk_credentials_mock import MockCredentialProvider
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_mock_responses import FEED_GET_RESP
from tests.fixtures.config_mock import (
    CREATE_CONFIG_DATA,
    MIGRATED_DATA,
    MIGRATED_DATA_NO_PROXY,
    OLD_CONFIG_DATA,
    OLD_CONFIG_DATA_NO_PROXY,
    UPDATE_CONFIG_DATA,
    UPDATE_CONFIG_DATA_INIT,
    UPDATE_CONFIG_DATA_NO_ROUTES,
)


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
    monkeypatch.setattr("cbc_importer.cli.wizard.get_cb", lambda: cbcsdk_mock.api)
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
        nonlocal dump_called
        assert data == MIGRATED_DATA
        assert kwargs["sort_keys"] is False
        dump_called = True

    old_config_data = OLD_CONFIG_DATA

    monkeypatch.setattr("builtins.input", migrate_input)
    monkeypatch.setattr("yaml.safe_load", lambda x: old_config_data)
    monkeypatch.setattr("yaml.dump", dump_method)
    monkeypatch.setattr("os.path.exists", lambda x: True)
    monkeypatch.setattr("builtins.open", open_file_mock)
    main()
    assert dump_called


def test_migrate_file_exists_no_proxy(monkeypatch, cbcsdk_mock):
    """Test for migrating config without proxy- success."""
    monkeypatch.setattr("cbc_importer.cli.wizard.get_cb", lambda: cbcsdk_mock.api)
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
        nonlocal dump_called
        assert data == MIGRATED_DATA_NO_PROXY
        assert kwargs["sort_keys"] is False
        dump_called = True

    monkeypatch.setattr("builtins.input", migrate_input)
    monkeypatch.setattr("yaml.safe_load", lambda x: OLD_CONFIG_DATA_NO_PROXY)
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
            "my_site_name_1",
            "",
            "",
            "basename",
            "",
            "",
            "6",
            "someid",
            "y",
            "http://some:8080",
            "wrong",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "8080",
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
            "*",
            "y",
            "1",
            "my_site_name_3",
            "",
            "",
            "basename",
            "",
            "",
            "6",
            "someid",
            "",
            "site2.com",
            "/api/v1/taxii/taxii-discovery-service/",
            "8080",
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
            "*",
            "y",
            "2",
            "my_site_name_2",
            "",
            "",
            "basename2",
            "",
            "",
            "",
            "someid",
            "site2.com",
            "",
            "",
            "",
            "",
            "",
            "",
            "y",
            "my_api_route",
            "col1 col2",
            "",
            "",
        ]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        nonlocal dump_called
        assert data == CREATE_CONFIG_DATA
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
    load_data = copy.deepcopy(UPDATE_CONFIG_DATA_INIT)
    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = [
            "3",
            "1",
            "y",
            "2",
            "my_site_name_2",
            "",
            "",
            "basename2",
            "",
            "",
            "",
            "someid",
            "site2.com",
            "",
            "",
            "",
            "",
            "",
            "",
            "y",
            "my_api_route",
            "*",
            "",
            "",
        ]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        nonlocal dump_called
        assert data == UPDATE_CONFIG_DATA
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
    load_data = copy.deepcopy(UPDATE_CONFIG_DATA_INIT)
    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = [
            "3",
            "1",
            "y",
            "2",
            "my_site_name_2",
            "",
            "",
            "basename2",
            "",
            "",
            "",
            "someid",
            "site2.com",
            "",
            "",
            "",
            "",
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

        nonlocal dump_called
        assert data == UPDATE_CONFIG_DATA_NO_ROUTES
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
    load_data = copy.deepcopy(UPDATE_CONFIG_DATA_INIT)
    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = ["3", "a"]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        nonlocal dump_called
        assert data == UPDATE_CONFIG_DATA_INIT
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
    load_data = copy.deepcopy(UPDATE_CONFIG_DATA_INIT)

    called = -1
    dump_called = False

    def update_config_input(the_prompt=""):
        inputs = ["3", "1", "y", "0"]
        nonlocal called
        called += 1
        return inputs[called]

    def dump_method(data, config, **kwargs):
        nonlocal dump_called
        assert data == UPDATE_CONFIG_DATA_INIT
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
            "cbc_auth_profile": "default",
            "servers": [],
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
