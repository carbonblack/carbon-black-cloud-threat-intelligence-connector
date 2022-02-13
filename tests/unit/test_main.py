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
from datetime import datetime
from unittest.mock import patch

import arrow
from cabby import Client11 as TAXIIClient11
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2
from taxii2client import Server as TAXIIClient2

from cbc_importer.stix_parsers.v1.parser import STIX1Parser
from cbc_importer.stix_parsers.v2.parser import STIX2Parser
from main import (
    connect_taxii1_server,
    connect_taxii2_server,
    get_default_time_range_taxii1,
    get_default_time_range_taxii2,
    process_taxii1_server,
    process_taxii2_server,
)


def test_configure_taxii2_server():
    """Test for passing the configuration correctly to the client"""
    config = {
        "version": 2.0,
        "enabled": True,
        "feed_base_name": "StixTaxiiFeedName",
        "host": "test.server.test",
        "severity": 5,
        "summary": "TestFeed",
        "category": "STIX",
        "api_routes": "*",
        "username": "guest",
        "password": "guest",
        "added_after": "",
    }
    taxii_client = connect_taxii2_server(config, stix_version=2.0)
    assert taxii_client.__dict__["_user"] == "guest"
    assert taxii_client.__dict__["_password"] == "guest"
    assert taxii_client.__dict__["url"] == "test.server.test/"


def test_configure_taxii1_server():
    """Test for passing the configuration correctly to the client"""
    config = {
        "version": 1.2,
        "enabled": True,
        "feed_base_name": "StixTaxiiFeedName",
        "host": "test.server.test",
        "discovery_path": "/taxii/discovery",
        "use_https": True,
        "cert_file": None,
        "key_file": None,
        "default_score": None,
        "collections": "*",
        "start_date": None,
        "ca_cert": None,
        "http_proxy_url": None,
        "https_proxy_url": None,
        "username": "test",
        "password": "test",
        "severity": 5,
        "summary": "...",
        "category": "STIX",
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
):
    """Test for calling the right functions with the right values"""
    config = {
        "version": 1.2,
        "enabled": True,
        "feed_base_name": "StixTaxiiFeedName",
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
        "severity": 5,
        "summary": "TEST SUMMARY",
        "category": "STIX",
    }
    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    start_date = arrow.utcnow().shift(months=-1).datetime.replace(microsecond=0)
    end_date = arrow.utcnow().datetime.replace(microsecond=0)
    client = TAXIIClient11()

    mock_connect_taxii1_server.return_value = client
    mock_get_default_time_range_taxii1.return_value = (start_date, end_date)
    mock_parse_taxii_server.return_value = iocs

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
        summary="TEST SUMMARY",
        category="STIX",
        severity=5,
    )


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
):
    """Test for calling the right functions with the right values"""
    iocs = [IOC_V2.create_query(cbcsdk_mock.api, "unsigned-chrome", "process_name:chrome.exe")]
    added_after = arrow.utcnow().shift(months=-1).datetime.replace(microsecond=0)
    client = TAXIIClient2(url="test.com")

    mock_connect_taxii2_server.return_value = client
    mock_get_default_time_range_taxii2.return_value = added_after
    mock_parse_taxii_server.return_value = iocs

    config = {
        "version": 2.0,
        "enabled": True,
        "feed_base_name": "StixTaxiiFeedName",
        "host": "test.server.test",
        "severity": 5,
        "summary": "TEST SUMMARY",
        "category": "STIX",
        "api_routes": "*",
        "username": "guest",
        "password": "guest",
        "added_after": "",
    }

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
        summary="TEST SUMMARY",
        category="STIX",
        severity=5,
    )
