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
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from typer.testing import CliRunner

from cbc_importer import __version__
from cbc_importer.cli.connector import (
    cli,
    process_stix1_file,
    process_stix2_file,
    process_taxii1_server,
    process_taxii2_server,
)
from tests.fixtures import cbc_sdk_mock

runner = CliRunner()


@patch.object(Path, "read_text", return_value=None)
@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("cbc_importer.cli.connector.process_taxii1_server")
@patch("yaml.safe_load")
def test_process_server_with_taxii1_server(safe_load, process_taxii1_server, *args, **kwargs):
    """Testing the CLI command `process-server` (TAXII 1 Server)"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 1.2,
                "enabled": True,
                "cbc_feed_options": {"replace": True, "severity": 5, "feed_id": None},
                "proxies": None,
                "connection": {
                    "host": "test.test.com",
                    "discovery_path": "/taxii/discovery",
                    "port": None,
                    "use_https": True,
                    "headers": None,
                    "timeout": None,
                },
                "auth": {
                    "username": "test",
                    "password": "test",
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "key_password": None,
                    "jwt_auth_url": None,
                    "verify_ssl": True,
                },
                "options": {
                    "begin_date": "2022-01-01 00:00:00",
                    "end_date": "2022-02-01 00:00:00",
                    "collection_management_uri": "/test/",
                    "collections": "*",
                },
            },
        ],
    }
    safe_load.return_value = configuration
    runner.invoke(cli, ["process-server", "--config-file", "./config.yml"])
    process_taxii1_server.assert_called()


@patch.object(Path, "read_text", return_value=None)
@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("cbc_importer.cli.connector.process_taxii2_server")
@patch("yaml.safe_load")
def test_process_server_with_taxii2_server(safe_load, process_taxii2_server, *args, **kwargs):
    """Testing the CLI command `process-server` (TAXII 2 Server)"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.0,
                "enabled": True,
                "cbc_feed_options": {"replace": True, "severity": 5, "feed_id": None},
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    safe_load.return_value = configuration
    runner.invoke(cli, ["process-server", "--config-file", "./config.yml"])
    process_taxii2_server.assert_called()


@patch.object(Path, "read_text", return_value=None)
@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("cbc_importer.cli.connector.process_taxii2_server")
@patch("yaml.safe_load")
def test_process_server_with_taxii_server_skip(safe_load, process_taxii2_server, cbcsdk, rt, caplog):
    """Testing the CLI command `process-server` (Skip Server)"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.0,
                "enabled": False,
                "cbc_feed_options": {"replace": True, "severity": 5, "feed_id": None},
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    safe_load.return_value = configuration
    with caplog.at_level(logging.INFO):
        runner.invoke(cli, ["process-server", "--config-file", "./config.yml"])
        assert "Skipping" in caplog.text


@patch("cbc_importer.cli.connector.process_stix1_file")
@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
def test_process_file_xml(_, process_stix1_file):
    """Testing the CLI command `process-file` (STIX 1)"""
    runner.invoke(cli, ["process-file", "./stix_file.xml", "55IOVthAZgmQHgr8eRF9rA", "-s", "5", "-r", "-c", "default"])
    process_stix1_file.assert_called_with(
        **{
            "stix_file_path": "./stix_file.xml",
            "feed_id": "55IOVthAZgmQHgr8eRF9rA",
            "severity": 5,
            "replace": True,
            "cb": cbc_sdk_mock,
        }
    )


@patch("cbc_importer.cli.connector.process_stix2_file")
@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
def test_process_file_json(_, process_stix2_file):
    """Testing the CLI command `process-file` (STIX 2)"""
    runner.invoke(cli, ["process-file", "./stix_file.json", "55IOVthAZgmQHgr8eRF9rA", "-s", "5", "-r", "-c", "default"])
    process_stix2_file.assert_called_with(
        **{
            "stix_file_path": "./stix_file.json",
            "feed_id": "55IOVthAZgmQHgr8eRF9rA",
            "severity": 5,
            "replace": True,
            "cb": cbc_sdk_mock,
        }
    )


@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
def test_process_file_raises_sys_exit(_, caplog):
    """Testing the CLI command `process-file` (Invalid Extension)"""
    runner.invoke(cli, ["process-file", "./stix_file.txt", "55IOVthAZgmQHgr8eRF9rA", "-s", "5", "-r", "-c", "default"])
    assert "Invalid extension" in caplog.text


@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("cbc_importer.cli.connector.utils_create_feed", return_value=Mock(id="90TuDxDYQtiGyg5qhwYCg"))
def test_create_feed_quiet(*args, **kwargs):
    """Testing the CLI command `create-feed` (quiet)"""
    result = runner.invoke(cli, ["create-feed", "NewFeed", "http://test.com/", "empty summary", "-ca", "STIX2", "-q"])
    assert result.stdout == "90TuDxDYQtiGyg5qhwYCg\n"
    assert result.exit_code == 0


@patch("cbc_importer.cli.connector.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("cbc_importer.cli.connector.utils_create_feed", return_value=Mock(id="90TuDxDYQtiGyg5qhwYCg"))
def test_create_feed_not_quiet(_, utils_create_feed):
    """Testing the CLI command `create-feed`"""
    runner.invoke(cli, ["create-feed", "NewFeed", "http://test.com/", "empty summary", "-ca", "STIX2"])
    utils_create_feed.assert_called()


@patch("cbc_importer.cli.connector.CBCloudAPI")
@patch("cbc_importer.cli.connector.utils_create_watchlist", return_value=Mock(id="90TuDxDYQtiGyg5qhwYCg"))
def test_create_watchlist_quiet(*args, **kwargs):
    """Testing the CLI command `create-watchlist` (quiet)"""
    result = runner.invoke(cli, ["create-watchlist", "90TuDxDYQtiGyg5qhwYCg", "TestName", "-d", "Test", "-e", "-q"])
    assert result.stdout == "90TuDxDYQtiGyg5qhwYCg\n"
    assert result.exit_code == 0


@patch("cbc_importer.cli.connector.CBCloudAPI")
@patch("cbc_importer.cli.connector.utils_create_watchlist", return_value=Mock(id="90TuDxDYQtiGyg5qhwYCg"))
def test_create_watchlist_not_quiet(_, utils_create_watchlist):
    """Testing the CLI command `create-watchlist`"""
    runner.invoke(cli, ["create-watchlist", "90TuDxDYQtiGyg5qhwYCg", "TestName", "-d", "Test", "-e"])
    utils_create_watchlist.assert_called()


def test_version():
    """Test if the application has the right version"""
    result = runner.invoke(cli, ["version"])
    assert result.stdout == "1.2\n"


@patch("cbc_importer.cli.connector.STIX1Parser")
@patch("cbc_importer.cli.connector.process_iocs")
def test_process_stix1_file(process_iocs, stix1_parser, caplog):
    """Testing if the functions is calling the right callables."""
    with caplog.at_level(logging.INFO):
        process_stix1_file(**{"stix_file_path": "./test.test", "cb": 1})
        process_iocs.assert_called()
        stix1_parser.assert_called()
        assert "Successfully imported ./test.test into CBC." in caplog.text


@patch("cbc_importer.cli.connector.STIX2Parser")
@patch("cbc_importer.cli.connector.process_iocs")
def test_process_stix2_file(process_iocs, stix2_parser, caplog):
    """Testing if the functions is calling the right callables."""
    with caplog.at_level(logging.INFO):
        process_stix2_file(**{"stix_file_path": "./test.test", "cb": 1})
        process_iocs.assert_called()
        stix2_parser.assert_called()
        assert "Successfully imported ./test.test into CBC." in caplog.text


@patch("cbc_importer.cli.connector.STIX1Parser")
@patch("cbc_importer.cli.connector.process_iocs")
def test_process_taxii1_server(process_iocs, stix1_parser, caplog):
    """Testing if the functions is calling the right callables."""
    with caplog.at_level(logging.INFO):
        process_taxii1_server(MagicMock(), 1)
        process_iocs.assert_called()
        stix1_parser.assert_called()
        assert "Successfully imported " in caplog.text


@patch("cbc_importer.cli.connector.STIX2Parser")
@patch("cbc_importer.cli.connector.process_iocs")
def test_process_taxii2_server(process_iocs, stix2_parser, caplog):
    """Testing if the functions is calling the right callables."""
    with caplog.at_level(logging.INFO):
        process_taxii2_server(MagicMock(), 1)
        process_iocs.assert_called()
        stix2_parser.assert_called()
        assert "Successfully imported " in caplog.text
