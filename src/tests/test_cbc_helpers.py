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
import pytest
from src.tests.fixtures.cbc_sdk_mock import CBCSDKMock
from src.tests.fixtures.cbc_sdk_mock_responses import (
    FEED_GET_ALL_RESP,
    FEED_GET_RESP,
    FEED_INIT,
    WATCHLIST_FROM_FEED_IN,
    WATCHLIST_FROM_FEED_OUT,
)
from src.tests.fixtures.cbc_sdk_credentials_mock import MockCredentialProvider

from src.utils.cbc_helpers import get_feed, create_watchlist

from cbc_sdk.rest_api import CBCloudAPI
from cbc_sdk.credential_providers.default import default_provider_object
from cbc_sdk.credentials import Credentials
from cbc_sdk.errors import ObjectNotFoundError, MoreThanOneResultError
from cbc_sdk.enterprise_edr.threat_intelligence import Feed


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
    watchlist = create_watchlist(api, feed)
    assert watchlist is not None
