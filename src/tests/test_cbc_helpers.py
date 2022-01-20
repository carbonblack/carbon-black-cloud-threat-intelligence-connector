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

"""Tests for the cbc helpers"""
import copy

import pytest
from cbc_sdk.rest_api import CBCloudAPI
from cbc_sdk.credential_providers.default import default_provider_object
from cbc_sdk.credentials import Credentials
from cbc_sdk.errors import (
    ObjectNotFoundError,
    MoreThanOneResultError,
    InvalidObjectError,
)
from cbc_sdk.enterprise_edr.threat_intelligence import Feed, Report, IOC_V2

from tests.fixtures.cbc_sdk_credentials_mock import MockCredentialProvider
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_mock_responses import (
    FEED_CREATE_NO_REPORT_INIT,
    FEED_GET_ALL_RESP,
    FEED_GET_RESP,
    FEED_INIT,
    FEED_POST_RESP,
    WATCHLIST_FROM_FEED_IN,
    WATCHLIST_FROM_FEED_OUT,
)

from utils.cbc_helpers import create_feed, get_feed, create_watchlist


@pytest.fixture(scope="function")
def cb(monkeypatch):
    """Create CBCloudAPI singleton"""
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
    """Mocks CBC SDK for unit tests"""
    return CBCSDKMock(monkeypatch, cb)


# ==================================== UNIT TESTS BELOW ====================================


def test_create_feed_no_reports(cbcsdk_mock):
    """Create feed without reports"""

    def on_post(url, body, **kwargs):
        assert body == FEED_CREATE_NO_REPORT_INIT
        return FEED_GET_RESP

    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds", on_post
    )
    api = cbcsdk_mock.api
    obj = create_feed(
        api,
        "base_name",
        "https://thisistheplace.com",
        "this is the details",
        "thiswouldgood",
    )
    assert obj.name == "base_name"


def test_create_feed_with_reports(cbcsdk_mock):
    """Create feed with reports"""

    def on_post(url, body, **kwargs):
        expected = copy.deepcopy(FEED_INIT)
        initial_body = copy.deepcopy(body)
        del expected["feedinfo"]["id"]
        del expected["reports"][0]["timestamp"]
        del initial_body["reports"][0]["timestamp"]
        del expected["reports"][0]["id"]
        del initial_body["reports"][0]["id"]
        assert initial_body == expected
        return FEED_POST_RESP

    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds", on_post
    )
    api = cbcsdk_mock.api

    report_builder = Report.create(api, "ReportTitle", "The report description", 5)
    report_builder.set_severity(5).set_link("https://example.com").add_tag(
        "Alpha"
    ).add_tag("Bravo")
    report_builder.add_ioc(
        IOC_V2.create_equality(api, "foo", "process_name", "evil.exe")
    )
    report_builder.add_ioc(
        IOC_V2.create_equality(api, "bar", "netconn_ipv4", "10.29.99.1")
    )
    report_builder.set_visibility("visible")
    report = report_builder.build()
    obj = create_feed(
        api,
        "base_name",
        "https://thisistheplace.com",
        "this is the details",
        "thiswouldgood",
        reports=[report],
    )
    assert obj.name == "base_name"


def test_get_feed_by_id(cbcsdk_mock):
    """Test get_feed by providing feed id"""
    api = cbcsdk_mock.api
    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds/90TuDxDYQtiGyg5qhwYCg",
        FEED_GET_RESP,
    )
    obj = get_feed(api, feed_id="90TuDxDYQtiGyg5qhwYCg")
    assert obj.name == "base_name"


def test_get_feed_by_name(cbcsdk_mock):
    """Test get_feed by providing feed name"""
    api = cbcsdk_mock.api
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds", FEED_GET_ALL_RESP
    )
    obj = get_feed(api, feed_name="EA16489_test_2")
    assert obj.name == "EA16489_test_2"
    assert obj.id == "QtQcKTyySgaUdXlQPsXXWA"


def test_get_feed_by_name_not_found(cbcsdk_mock):
    """Test get_feed by providing not existing feed name"""
    api = cbcsdk_mock.api
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds", FEED_GET_ALL_RESP
    )
    with pytest.raises(ObjectNotFoundError):
        get_feed(api, feed_name="alabala")


def test_get_feed_by_name_more_than_one(cbcsdk_mock):
    """Test get_feed by providing duplicate feed name"""
    api = cbcsdk_mock.api
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/A1B2C3D4/feeds", FEED_GET_ALL_RESP
    )
    with pytest.raises(MoreThanOneResultError):
        get_feed(api, feed_name="TEST")


def test_get_feed_by_missing_params(cbcsdk_mock):
    """Test get_feed without either feed_name or feed id"""
    api = cbcsdk_mock.api
    with pytest.raises(ValueError):
        get_feed(api)


def test_create_watchlist(cbcsdk_mock):
    """Test create_watchlist"""

    def on_post(url, body, **kwargs):
        assert body == WATCHLIST_FROM_FEED_IN
        return WATCHLIST_FROM_FEED_OUT

    cbcsdk_mock.mock_request(
        "POST", "/threathunter/watchlistmgr/v3/orgs/A1B2C3D4/watchlists", on_post
    )
    api = cbcsdk_mock.api
    feed = Feed(api, initial_data=FEED_INIT)
    watchlist = create_watchlist(feed)
    assert watchlist is not None


def test_create_watchlist_no_valid_feed(cbcsdk_mock):
    """Test create_watchlist with no feed"""
    with pytest.raises(InvalidObjectError):
        create_watchlist(None)
