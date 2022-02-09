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
from main import configure_taxii1_server, configure_taxii2_server, process_taxii1_server, process_taxii2_server


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
    taxii_client = configure_taxii2_server(config, stix_version=2.0)
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
        "summary": "AlienVault OTX",
        "category": "STIX",
    }
    taxii_client = configure_taxii1_server(config)
    assert taxii_client.__dict__["host"] == "test.server.test"
    assert taxii_client.__dict__["discovery_path"] == "/taxii/discovery"
    assert taxii_client.__dict__["use_https"]

