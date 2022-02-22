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
from multiprocessing.sharedctypes import Value
from pathlib import Path
from unittest.mock import MagicMock, patch

import arrow
import pytest
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2

from cbc_importer import __version__
from cbc_importer.stix_parsers.v1.parser import STIX1Parser
from cbc_importer.stix_parsers.v2.parser import STIX2Parser
from cbc_importer.taxii_configurator import TAXIIConfigurator
from main import (
    process_file,
    process_server,
    process_stix1_file,
    process_stix2_file,
    process_taxii1_server,
    process_taxii2_server,
)
from tests.fixtures import cbc_sdk_mock


@patch.object(STIX1Parser, "parse_file")
@patch("main.process_iocs")
def test_process_stix1_file(mock_process_iocs, mock_parse_file, cbcsdk_mock, caplog):
    """Test processing a STIX1 File"""
    kwargs = {
        "stix_file_path": "./text/path",
        "provider_url": "http://test-provider.test/",
        "start_date": "2022-01-01",
        "end_date": "2022-02-01",
        "severity": 8,
        "summary": "None",
        "category": "STIX",
        "feed_base_name": "STIXFile",
        "cb": cbcsdk_mock,
    }

    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    mock_parse_file.return_value = iocs
    mock_process_iocs.return_value = [MagicMock()]

    with caplog.at_level(logging.INFO):
        process_stix1_file(**kwargs)
        mock_process_iocs.assert_called_with(
            cb=cbcsdk_mock,
            iocs=iocs,
            feed_base_name="STIXFile",
            stix_version=1,
            start_date=arrow.get(kwargs["start_date"]).format("YYYY-MM-DD"),
            end_date=arrow.get(kwargs["end_date"]).format("YYYY-MM-DD"),
            provider_url="http://test-provider.test/",
            summary="None",
            category="STIX",
            severity=8,
        )
        assert "Created feed with ID" in caplog.text


@patch.object(STIX2Parser, "parse_file")
@patch("main.process_iocs", return_value=[])
def test_process_stix2_file(mock_process_iocs, mock_parse_file, cbcsdk_mock, caplog):
    """Test processing a STIX2 File"""
    kwargs = {
        "stix_file_path": "./text/path",
        "provider_url": "http://test-provider.test/",
        "start_date": "2022-01-01",
        "end_date": "2022-02-01",
        "severity": 8,
        "summary": "None",
        "category": "STIX",
        "feed_base_name": "STIXFile",
        "cb": cbcsdk_mock,
    }

    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    mock_parse_file.return_value = iocs
    mock_process_iocs.return_value = [MagicMock()]

    with caplog.at_level(logging.INFO):
        process_stix2_file(**kwargs)
        mock_process_iocs.assert_called_with(
            cb=cbcsdk_mock,
            iocs=iocs,
            feed_base_name="STIXFile",
            stix_version=2,
            start_date=arrow.get(kwargs["start_date"]).format("YYYY-MM-DD"),
            end_date=arrow.get(kwargs["end_date"]).format("YYYY-MM-DD"),
            provider_url="http://test-provider.test/",
            summary="None",
            category="STIX",
            severity=8,
        )
        assert "Created feed with ID" in caplog.text


@patch("main.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("main.process_stix2_file", return_value=[])
def test_process_file_json(process_stix2_file, *args):
    """Test process_file with JSON extension"""
    process_file(
        "./test.json",
        "http://test.com/",
        "2022-01-01",
        "2022-02-01",
        8,
        "...",
        "STIX",
        "default",
        "STIXFile",
    )
    process_stix2_file.assert_called()


@patch("main.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("main.process_stix1_file", return_value=[])
def test_process_file_xml(process_stix1_file, *args):
    """Test process_file with XML extension"""
    process_file(
        "./test.xml",
        "http://test.com/",
        "2022-01-01",
        "2022-02-01",
        8,
        "...",
        "STIX",
        "default",
        "STIXFile",
    )
    process_stix1_file.assert_called()


@patch("main.CBCloudAPI", return_value=cbc_sdk_mock)
def test_process_file_invalid(*args):
    """Test process_file with invalid extension"""
    with pytest.raises(ValueError):
        process_file(
            "./test.file",
            "http://test.com/",
            "2022-01-01",
            "2022-02-01",
            8,
            "...",
            "STIX",
            "default",
            "STIXFile",
        )


@patch.object(STIX1Parser, "parse_taxii_server")
@patch("main.process_iocs")
def test_process_taxii1_server(mock_process_iocs, mock_parse_taxii_server, cbcsdk_mock, caplog):
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 1.2,
                "enabled": False,
                "cbc_feed_options": {
                    "feed_base_name": "TestSTIX",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
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
    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    mock_parse_taxii_server.return_value = iocs
    mock_process_iocs.return_value = [MagicMock()]
    configurator = TAXIIConfigurator(configuration["servers"][0])

    with caplog.at_level(logging.INFO):
        process_taxii1_server(configurator, cbcsdk_mock)
        mock_parse_taxii_server.assert_called_with(configurator.client, **configurator.search_options)
        mock_process_iocs.assert_called_with(cb=cbcsdk_mock, iocs=iocs, **configurator.cbc_feed_options)
        assert "Created feed with ID" in caplog.text


@patch.object(STIX2Parser, "parse_taxii_server")
@patch("main.process_iocs")
def test_process_taxii2_server(mock_process_iocs, mock_parse_taxii_server, cbcsdk_mock, caplog):
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.0,
                "enabled": True,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    mock_parse_taxii_server.return_value = iocs
    mock_process_iocs.return_value = [MagicMock()]
    configurator = TAXIIConfigurator(configuration["servers"][0])

    with caplog.at_level(logging.INFO):
        process_taxii2_server(configurator, cbcsdk_mock)
        mock_parse_taxii_server.assert_called_with(configurator.client, **configurator.search_options)
        mock_process_iocs.assert_called_with(cbcsdk_mock, iocs, **configurator.cbc_feed_options)
        assert "Created feed with ID" in caplog.text


@patch("main.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("main.process_taxii2_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_not_enabled(safe_load, rt, pts, cbcsdk, caplog):
    """Test process_server where site is not enabled"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.0,
                "enabled": False,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    safe_load.return_value = configuration
    with caplog.at_level(logging.INFO):
        process_server(config_file="test.yml")
        assert "Skipping" in caplog.text


@patch("main.CBCloudAPI", return_value=cbc_sdk_mock)
@patch("main.process_taxii2_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_invalid_version(safe_load, rt, pts, cbcsdk, caplog):
    """Test process_server where site is not enabled"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.5,
                "enabled": False,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    safe_load.return_value = configuration
    with pytest.raises(ValueError):
        process_server(config_file="test.yml")
