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
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2, Feed
from cbc_sdk.errors import ObjectNotFoundError

from cbc_importer.importer import process_iocs
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_mock_responses import (
    FEED_GET_RESP,
    REPORT_INIT_ONE_IOCS,
    REPORTS_3_INIT_1000_IOCS,
    REPORTS_GET_3_WITH_1000_IOCS,
    REPORTS_GET_NO_REPORTS, REPORT_WITH_998_IOCS, REPORTS_GET_2_WITH_998_IOCS,
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


def test_process_iocs_no_feed(cbcsdk_mock):
    """Test process 1 iocs - replace"""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")

    def on_get_feed(url, *args, **kwargs):
        raise ObjectNotFoundError(404)

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        on_get_feed,
    )

    with pytest.raises(SystemExit):
        process_iocs(
            api,
            [ioc],
            5,
            "feedid",
            True
        )


def test_process_iocs_replace(cbcsdk_mock):
    """Test process 1 iocs - replace"""
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

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report
    )
    feed = process_iocs(
        api,
        [ioc],
        5,
        "feedid",
        True
    )
    assert isinstance(feed, Feed)


'''
def test_process_iocs_append_with_existing_reports(cbcsdk_mock):
    """Test process 1004 iocs - append, existing 2 reports with 998 iocs"""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")
    iocs_list = [ioc for i in range(1004)]
    counter_r = 1

    def on_post_report(url, body, **kwargs):
        nonlocal counter_r
        report_body = copy.deepcopy(body)
        # remove the variable properties
        for i in range(len(report_body["reports"])):
            del report_body["reports"][i]["id"]
            del report_body["reports"][i]["timestamp"]
            title = report_body["reports"][i]["title"]
            assert "Report My STIX Feed-" + str(counter_r) == title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1-1"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000
            counter_r += 1
        assert report_body == REPORTS_3_INIT_1000_IOCS
        return REPORTS_3_INIT_1000_IOCS

    def on_get_reports(url, *args, **kwargs):
        print('here', url, args, kwargs)
        return REPORTS_GET_2_WITH_998_IOCS

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report
    )
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_get_reports
    )
    feed = process_iocs(
        api,
        [ioc],
        5,
        "feedid",
        False
    )
'''


def test_process_iocs_append(cbcsdk_mock):
    """Test process 1 iocs - append, no existing reports"""
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

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_GET_NO_REPORTS

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report
    )
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_get_reports
    )
    feed = process_iocs(
        api,
        [ioc],
        5,
        "feedid",
        False
    )
    assert isinstance(feed, Feed)


def test_process_a_few_reports_replace(cbcsdk_mock):
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
            assert "Report My STIX Feed-" + str(counter_r) == title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report My STIX Feed-1"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000
            counter_r += 1

        assert report_body == REPORTS_3_INIT_1000_IOCS
        return REPORTS_3_INIT_1000_IOCS

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_GET_3_WITH_1000_IOCS

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report
    )

    feed = process_iocs(
        api,
        iocs_list,
        5,
        "feedid",
        True
    )
    assert isinstance(feed, Feed)
