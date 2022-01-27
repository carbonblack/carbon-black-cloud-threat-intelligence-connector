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
import pytest
import copy

from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2

from cbc_importer.importer import process_iocs
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.cbc_sdk_mock_responses import (FEED_RESP_POST_STIX,
                                                   FEED_CREATE_STIX,
                                                   FEED_GET_ALL_RESP_NO_FEED)


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
    """Test process iocs with a single iocs"""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")
    called = False
    '''
    def on_post_reports(url, body, **kwargs):
        ...

    def on_post(url, body, **kwargs):
        from pprint import pprint
        result = copy.deepcopy(body)
        pprint(body)
        assert body == FEED_CREATE_STIX
        nonlocal called
        if not called:
            called = False
            assert body == FEED_CREATE_STIX
            return FEED_RESP_POST_STIX
        else:
            return ''

    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds", FEED_GET_ALL_RESP_NO_FEED)
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds", on_post)
    cbcsdk_mock.mock_request("POST",
                             "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports",
                             on_post_report)
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
    '''
