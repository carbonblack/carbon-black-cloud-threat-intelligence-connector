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
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import arrow
import pytest
from cabby import Client11 as TAXIIClient11
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2
from taxii2client import Server as TAXIIClient2
from taxii2client.v20 import Server as taxii20_client
from taxii2client.v21 import Server as taxii21_client

from cbc_importer import __version__
from cbc_importer.stix_parsers.v1.parser import STIX1Parser
from cbc_importer.stix_parsers.v2.parser import STIX2Parser
from main import (
    connect_taxii1_server,
    connect_taxii2_server,
    get_default_time_range_taxii1,
    get_default_time_range_taxii2,
    init_cbcsdk,
    process_file,
    process_server,
    process_stix1_file,
    process_stix2_file,
    process_taxii1_server,
    process_taxii2_server,
)
from tests.fixtures import cbc_sdk_mock


def test_configure_taxii2_server():
    """Test for passing the configuration correctly to the client"""
    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 2.0,
        "enabled": True,
        "host": "test.server.test",
        "api_routes": "*",
        "username": "guest",
        "password": "guest",
        "added_after": "",
    }
    taxii_client = connect_taxii2_server(config, stix_version=2.0)
    assert isinstance(taxii_client, taxii20_client)
    assert taxii_client.__dict__["_user"] == "guest"
    assert taxii_client.__dict__["_password"] == "guest"
    assert taxii_client.__dict__["url"] == "test.server.test/"


def test_configure_taxii2_server_client_for_21():
    """Test for passing the configuration correctly to the client"""
    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 2.1,
        "enabled": True,
        "host": "test.server.test",
        "api_routes": "*",
        "username": "guest",
        "password": "guest",
        "added_after": "",
    }
    taxii_client = connect_taxii2_server(config, stix_version=2.1)
    assert isinstance(taxii_client, taxii21_client)
    assert taxii_client.__dict__["_user"] == "guest"
    assert taxii_client.__dict__["_password"] == "guest"
    assert taxii_client.__dict__["url"] == "test.server.test/"


def test_configure_taxii1_server_no_auth():
    """Test for passing the configuration correctly to the client"""
    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 1.2,
        "enabled": True,
        "host": "test.server.test",
        "discovery_path": "/taxii/discovery",
        "use_https": True,
        "cert_file": None,
        "key_file": None,
        "collections": "*",
        "start_date": None,
        "ca_cert": None,
        "http_proxy_url": None,
        "https_proxy_url": None,
    }
    taxii_client = connect_taxii1_server(config)
    assert taxii_client.__dict__["username"] is None
    assert taxii_client.__dict__["password"] is None


def test_configure_taxii1_server_with_proxy_dict():
    """Test for passing the configuration correctly to the client"""
    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 1.2,
        "enabled": True,
        "host": "test.server.test",
        "discovery_path": "/taxii/discovery",
        "use_https": True,
        "cert_file": None,
        "key_file": None,
        "collections": "*",
        "start_date": None,
        "ca_cert": None,
        "http_proxy_url": {"http": "http://10.10.10.10/"},
        "https_proxy_url": {"https": "http://10.10.10.10/"},
    }
    taxii_client = connect_taxii1_server(config)
    assert taxii_client.__dict__["proxies"] == {"http": "http://10.10.10.10/"}


def test_configure_taxii1_server():
    """Test for passing the configuration correctly to the client"""
    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 1.2,
        "enabled": True,
        "host": "test.server.test",
        "discovery_path": "/taxii/discovery",
        "use_https": True,
        "cert_file": None,
        "key_file": None,
        "collections": "*",
        "start_date": None,
        "ca_cert": None,
        "http_proxy_url": None,
        "https_proxy_url": None,
        "username": "test",
        "password": "test",
    }
    taxii_client = connect_taxii1_server(config)
    assert taxii_client.__dict__["host"] == "test.server.test"
    assert taxii_client.__dict__["discovery_path"] == "/taxii/discovery"
    assert taxii_client.__dict__["use_https"]


def test_get_default_time_range_taxii1_defaults():
    """Test for getting the default time range"""
    start_date = arrow.utcnow().shift(months=-1).datetime.replace(microsecond=0)
    end_date = arrow.utcnow().datetime.replace(microsecond=0)

    start_date_, end_date_ = get_default_time_range_taxii1({})

    assert isinstance(start_date_, datetime)
    assert isinstance(end_date_, datetime)
    assert start_date.tzname() == "UTC"
    assert end_date.tzname() == "UTC"
    assert start_date_.replace(microsecond=0) == start_date
    assert end_date_.replace(microsecond=0) == end_date


def test_get_default_time_range_taxii1_custom():
    """Test for getting the custom time range"""

    start_date, end_date = get_default_time_range_taxii1({"start_date": "2022-01-01", "end_date": "2022-02-01"})
    assert isinstance(start_date, datetime)
    assert start_date.tzname() == "UTC"
    assert start_date.isoformat() == "2022-01-01T00:00:00+00:00"
    assert isinstance(end_date, datetime)
    assert end_date.tzname() == "UTC"
    assert end_date.isoformat() == "2022-02-01T00:00:00+00:00"


def test_get_default_time_range_taxii2_defaults():
    """Tests for getting the default `added_after`"""
    added_after_ = arrow.utcnow().shift(months=-1).datetime.replace(microsecond=0)
    added_after = get_default_time_range_taxii2({})
    assert isinstance(added_after, datetime)
    assert added_after.replace(microsecond=0) == added_after_
    assert added_after.tzname() == "UTC"


def test_get_default_time_range_taxii2_custom():
    """Tests for getting the default `added_after`"""
    added_after = get_default_time_range_taxii2({"added_after": "2022-01-01"})
    assert isinstance(added_after, datetime)
    assert added_after.isoformat() == "2022-01-01T00:00:00+00:00"
    assert added_after.tzname() == "UTC"


@patch("main.get_default_time_range_taxii1")
@patch("main.connect_taxii1_server")
@patch.object(STIX1Parser, "parse_taxii_server")
@patch("main.process_iocs")
def test_process_taxii1_server(
    mock_process_iocs,
    mock_parse_taxii_server,
    mock_connect_taxii1_server,
    mock_get_default_time_range_taxii1,
    cbcsdk_mock,
    caplog,
):
    """Test for calling the right functions with the right values"""
    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 1.2,
        "enabled": True,
        "host": "test.server.test",
        "discovery_path": "/taxii/discovery",
        "use_https": True,
        "cert_file": None,
        "key_file": None,
        "default_score": None,
        "collections": "*",
        "start_date": "2022-01-01",
        "end_date": "2022-02-01",
        "ca_cert": None,
        "http_proxy_url": None,
        "https_proxy_url": None,
        "username": "test",
        "password": "test",
    }
    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    start_date = arrow.utcnow().shift(months=-1).datetime.replace(microsecond=0)
    end_date = arrow.utcnow().datetime.replace(microsecond=0)
    client = TAXIIClient11()

    mock_connect_taxii1_server.return_value = client
    mock_get_default_time_range_taxii1.return_value = (start_date, end_date)
    mock_parse_taxii_server.return_value = iocs
    mock_process_iocs.return_value = [MagicMock()]

    with caplog.at_level(logging.INFO):
        process_taxii1_server(config, cbcsdk_mock, "test_name")
        mock_parse_taxii_server.assert_called_with(client, "*", begin_date=start_date, end_date=end_date)
        mock_get_default_time_range_taxii1.assert_called_with(config)
        mock_connect_taxii1_server.assert_called_with(config)
        mock_process_iocs.assert_called_with(
            cbcsdk_mock,
            iocs,
            "StixTaxiiFeedName",
            1.2,
            start_date=arrow.get(start_date).format("YYYY-MM-DD HH:mm:ss ZZ"),
            end_date=arrow.get(end_date).format("YYYY-MM-DD HH:mm:ss ZZ"),
            provider_url="test.server.test",
            summary="...",
            category="STIX",
            severity=5,
        )
        assert "Created feed with ID" in caplog.text


@patch("main.get_default_time_range_taxii2")
@patch("main.connect_taxii2_server")
@patch.object(STIX2Parser, "parse_taxii_server")
@patch("main.process_iocs", return_value=[])
def test_process_taxii2_server_calls(
    mock_process_iocs,
    mock_parse_taxii_server,
    mock_connect_taxii2_server,
    mock_get_default_time_range_taxii2,
    cbcsdk_mock,
    caplog,
):
    """Test for calling the right functions with the right values"""
    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    added_after = arrow.utcnow().shift(months=-1).datetime.replace(microsecond=0)
    client = TAXIIClient2(url="test.com")

    mock_connect_taxii2_server.return_value = client
    mock_get_default_time_range_taxii2.return_value = added_after
    mock_parse_taxii_server.return_value = iocs
    mock_process_iocs.return_value = [MagicMock()]

    config = {
        "cbc_config": {
            "severity": 5,
            "summary": "...",
            "category": "STIX",
            "feed_base_name": "StixTaxiiFeedName",
        },
        "version": 2.0,
        "enabled": True,
        "host": "test.server.test",
        "api_routes": "*",
        "username": "guest",
        "password": "guest",
        "added_after": "",
    }

    with caplog.at_level(logging.INFO):
        process_taxii2_server(config, cbcsdk_mock, "test_server", 2.0)
        mock_get_default_time_range_taxii2.assert_called_with(config)
        mock_connect_taxii2_server.assert_called_with(config, 2.0)
        mock_parse_taxii_server.assert_called_with(client, "*", added_after=added_after)
        mock_process_iocs.assert_called_with(
            cbcsdk_mock,
            iocs,
            "StixTaxiiFeedName",
            2.0,
            start_date=arrow.get(added_after).format("YYYY-MM-DD HH:mm:ss ZZ"),
            end_date=arrow.utcnow().format("YYYY-MM-DD HH:mm:ss ZZ"),
            provider_url="test.server.test",
            summary="...",
            category="STIX",
            severity=5,
        )
        assert "Created feed with ID" in caplog.text


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


@patch("main.process_stix2_file", return_value=[])
def test_process_file_json(process_stix2_file):
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


@patch("main.process_stix1_file", return_value=[])
def test_process_file_xml(process_stix1_file):
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


def test_process_file_invalid():
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


@patch("main.init_cbcsdk", return_value=cbc_sdk_mock)
@patch("main.process_taxii1_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_taxii1(safe_load, read_text, mock_process_taxii1_server, init_cbcsdk, caplog):
    """Test process_server gives calls the taxi1 process"""
    expected = {"cbc_profile_name": "test", "sites": [{"name": "test_site", "version": 1.2, "enabled": True}]}
    mock_process_taxii1_server.return_value = [MagicMock()]
    safe_load.return_value = expected

    process_server(config_file="test.yml")
    mock_process_taxii1_server.assert_called_with(expected["sites"][0], cbc_sdk_mock, "test_site")


@patch("main.init_cbcsdk", return_value=cbc_sdk_mock)
@patch("main.process_taxii2_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_taxii20(safe_load, read_text, mock_process_taxii2_server, init_cbcsdk):
    """Test process_server gives calls the taxi20 process"""
    expected = {"cbc_profile_name": "test", "sites": [{"name": "test_site", "version": 2.0, "enabled": True}]}
    safe_load.return_value = expected
    process_server(config_file="test.yml")
    mock_process_taxii2_server.assert_called_with(
        expected["sites"][0], cbc_sdk_mock, "test_site", expected["sites"][0]["version"]
    )


@patch("main.init_cbcsdk", return_value=cbc_sdk_mock)
@patch("main.process_taxii2_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_taxii21(safe_load, read_text, mock_process_taxii2_server, init_cbcsdk):
    """Test process_server gives calls the taxi21 process"""
    expected = {"cbc_profile_name": "test", "sites": [{"name": "test_site", "version": 2.1, "enabled": True}]}
    safe_load.return_value = expected
    process_server(config_file="test.yml")
    mock_process_taxii2_server.assert_called_with(
        expected["sites"][0], cbc_sdk_mock, "test_site", expected["sites"][0]["version"]
    )


@patch("main.init_cbcsdk", return_value=cbc_sdk_mock)
@patch("main.process_taxii2_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_taxii_raises_value_error(safe_load, *args):
    """Test process_server raises ValueError"""
    expected = {"cbc_profile_name": "test", "sites": [{"name": "test_site", "version": 18, "enabled": True}]}
    safe_load.return_value = expected
    with pytest.raises(ValueError):
        process_server(config_file="test.yml")


@patch("main.init_cbcsdk", return_value=cbc_sdk_mock)
@patch("main.process_taxii2_server")
@patch.object(Path, "read_text", return_value=None)
@patch("yaml.safe_load")
def test_process_server_not_enabled(safe_load, rt, pts, cbcsdk, caplog):
    """Test process_server where site is not enabled"""
    expected = {"cbc_profile_name": "test", "sites": [{"name": "test_site", "version": 1.2, "enabled": False}]}
    safe_load.return_value = expected
    with caplog.at_level(logging.INFO):
        process_server(config_file="test.yml")
        assert "is not enabled, skipping" in caplog.text


@patch("main.CBCloudAPI")
def test_init_cbcsdk(cbcapi):
    """Test init of CBC"""
    init_cbcsdk("default")
    cbcapi.assert_called_with(profile="default", integration_name=("STIX/TAXII " + __version__))
