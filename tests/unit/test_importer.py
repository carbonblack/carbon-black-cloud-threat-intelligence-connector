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
    REPORTS_2_1_IOC,
    REPORTS_2_WITH_1_AND_3,
    REPORTS_3_INIT_1000_IOCS,
    REPORTS_4_INIT_1000_IOCS,
    REPORTS_GET_2_WITH_998_IOCS_1_1000,
    REPORTS_GET_NO_REPORTS,
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
    """Test process 1 iocs - replace, but search by feed id returns ObjectNotFoundError"""
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
        process_iocs(api, [ioc], 5, "feedid", True)


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
            if report_body["reports"][0].get("iocs_total_count"):
                del report_body["reports"][0]["iocs_total_count"]
        assert report_body == REPORT_INIT_ONE_IOCS
        return REPORT_INIT_ONE_IOCS

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report)
    assert process_iocs(api, [ioc], 5, "feedid", True) is None


def test_process_a_few_reports_replace(cbcsdk_mock):
    """Test process iocs with replace enough for 3 reports"""
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
            assert "Report My STIX Feed" == title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report My STIX Feed"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000
            counter_r += 1

        assert report_body == REPORTS_3_INIT_1000_IOCS
        return REPORTS_3_INIT_1000_IOCS

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report)

    assert process_iocs(api, iocs_list, 5, "feedid", True) is None


def test_process_iocs_append_with_existing_reports(cbcsdk_mock):
    """Test process 1004 iocs - append, existing 2 reports with 998 iocs, so one additional report is created."""
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
            if report_body["reports"][i].get("iocs_total_count"):
                del report_body["reports"][i]["iocs_total_count"]
            title = report_body["reports"][i]["title"]
            assert "Report My STIX Feed" in title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report My STIX Feed"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000
            counter_r += 1
        assert report_body == REPORTS_4_INIT_1000_IOCS
        return REPORTS_4_INIT_1000_IOCS

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_GET_2_WITH_998_IOCS_1_1000

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report)
    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_get_reports)
    assert process_iocs(api, iocs_list, 5, "feedid", False) is None


def test_process_iocs_append_with_existing_reports_no_new_needed(cbcsdk_mock):
    """Test process 2 iocs - append, existing 2 reports with 1 report each, no additional reports are required."""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")
    iocs_list = [ioc for i in range(2)]
    counter_r = 1

    def on_post_report(url, body, **kwargs):
        nonlocal counter_r
        report_body = copy.deepcopy(body)
        expected_body = copy.deepcopy(REPORTS_2_WITH_1_AND_3)
        # remove the variable properties
        for i in range(len(report_body["reports"])):
            del report_body["reports"][i]["id"]
            del report_body["reports"][i]["timestamp"]
            del expected_body["reports"][i]["id"]
            del expected_body["reports"][i]["timestamp"]
            if report_body["reports"][i].get("iocs_total_count"):
                del report_body["reports"][i]["iocs_total_count"]
            if expected_body["reports"][i].get("iocs_total_count"):
                del expected_body["reports"][i]["iocs_total_count"]
            title = report_body["reports"][i]["title"]
            assert "Report My STIX Feed" in title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report My STIX Feed"
            if counter_r == 1:
                assert len(report_body["reports"][i]["iocs_v2"]) == 3
            else:
                assert len(report_body["reports"][i]["iocs_v2"]) == 1
            counter_r += 1
        assert report_body == expected_body
        return REPORTS_2_WITH_1_AND_3

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_2_1_IOC

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report)
    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_get_reports)
    assert process_iocs(api, iocs_list, 5, "feedid", False) is None


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
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report)
    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_get_reports)
    assert process_iocs(api, [ioc], 5, "feedid", False) is None
