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


"""Tests for the importer."""
import copy

import pytest
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2

from cbc_importer.importer import process_iocs, subscribe_to_feed
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_mock_responses import (
    FEED_CREATE_STIX,
    FEED_GET_ALL_RESP,
    FEED_GET_ALL_RESP_NO_FEED,
    FEED_RESP_POST_STIX,
    REPORT_INIT_ONE_IOCS,
    REPORTS_3_INIT_1000_IOCS,
    REPORTS_GET_3_WITH_1000_IOCS,
    REPORTS_GET_ONE_IOCS,
    WATCHLIST_FROM_FEED_OUT,
)


@pytest.fixture(scope="function")
def cb():
    """Create CBCloudAPI singleton"""
    return CBCloudAPI(url="https://example.com", org_key="test", token="abcd/1234", ssl_verify=False)


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch, cb):
    """Mocks CBC SDK for unit tests"""
    return CBCSDKMock(monkeypatch, cb)


# ==================================== UNIT TESTS BELOW ====================================


def test_process_iocs_single_ioc(cbcsdk_mock):
    """Test process iocs with a single ioc"""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")

    def on_post_report(url, body, **kwargs):
        report_body = copy.deepcopy(body)
        # remove the variable properties
        if report_body["reports"]:
            del report_body["reports"][0]["id"]
            del report_body["reports"][0]["timestamp"]
        assert report_body == REPORT_INIT_ONE_IOCS
        return REPORT_INIT_ONE_IOCS

    def on_post_feed(url, body, **kwargs):
        assert body == FEED_CREATE_STIX
        return FEED_RESP_POST_STIX

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_GET_ONE_IOCS

    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds", FEED_GET_ALL_RESP_NO_FEED)
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds", on_post_feed)
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports", on_post_report
    )
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports", on_get_reports
    )
    feeds = process_iocs(
        api,
        [ioc],
        "my_base_name",
        "2.0",
        "2022-01-27",
        "2022-02-27",
        "limo.domain.com",
        "feed for stix taxii",
        "thiswouldgood",
        5,
    )

    assert len(feeds) == 1
    assert len(feeds[0].reports) == 1
    assert len(feeds[0].reports[0]["iocs_v2"]) == 1


def test_process_a_few_reports(cbcsdk_mock):
    """Test process iocs enough for 3 reports"""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")
    iocs_list = [ioc for i in range(3000)]
    counter_r = 1

    def on_post_report(url, body, **kwargs):
        nonlocal counter_r
        report_body = copy.deepcopy(body)
        # remove the variable properties
        for i in range(len(report_body["reports"])):
            del report_body["reports"][i]["id"]
            del report_body["reports"][i]["timestamp"]
            title = report_body["reports"][i]["title"]
            assert "Report my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1-" + str(counter_r) == title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1-1"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000
            counter_r += 1

        assert report_body == REPORTS_3_INIT_1000_IOCS
        return REPORTS_3_INIT_1000_IOCS

    def on_post_feed(url, body, **kwargs):
        assert body == FEED_CREATE_STIX
        return FEED_RESP_POST_STIX

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_GET_3_WITH_1000_IOCS

    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds", FEED_GET_ALL_RESP_NO_FEED)
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds", on_post_feed)
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports", on_post_report
    )
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports", on_get_reports
    )
    feeds = process_iocs(
        api,
        iocs_list,
        "my_base_name",
        "2.0",
        "2022-01-27",
        "2022-02-27",
        "limo.domain.com",
        "feed for stix taxii",
        "thiswouldgood",
        5,
    )

    assert len(feeds) == 1
    assert len(feeds[0].reports) == 3
    assert len(feeds[0].reports[0]["iocs_v2"]) == 1000
    assert len(feeds[0].reports[1]["iocs_v2"]) == 1000
    assert len(feeds[0].reports[2]["iocs_v2"]) == 1000


def test_subscribed_to_feed_by_base_name(cbcsdk_mock):
    """Test subscribed to feed"""
    api = cbcsdk_mock.api
    counter = 0

    def on_post(url, body, **kwargs):
        nonlocal counter
        counter += 1
        return WATCHLIST_FROM_FEED_OUT

    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds", FEED_GET_ALL_RESP)
    cbcsdk_mock.mock_request("POST", "/threathunter/watchlistmgr/v3/orgs/test/watchlists", on_post)
    subscribe_to_feed(api, feed_base_name="TEST")
    assert counter == 3


def test_subscribed_to_feed_by_name(cbcsdk_mock):
    """Test subscribed to feed"""
    api = cbcsdk_mock.api
    counter = 0

    def on_post(url, body, **kwargs):
        nonlocal counter
        counter += 1
        return WATCHLIST_FROM_FEED_OUT

    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds", FEED_GET_ALL_RESP)
    cbcsdk_mock.mock_request("POST", "/threathunter/watchlistmgr/v3/orgs/test/watchlists", on_post)
    subscribe_to_feed(api, feed_name="TEST123")
    assert counter == 1


def test_subscribed_to_feed_no_arg(cbcsdk_mock):
    """Test subscribed to feed"""
    api = cbcsdk_mock.api
    with pytest.raises(Exception):
        subscribe_to_feed(api)
