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

"""Mock for CBC responses."""

FEED_GET_ALL_RESP = {
    "results": [
        {
            "name": "IBM IRIS Feed",
            "owner": "WNEXFKQ7",
            "provider_url": "https://thisistheplace.com",
            "summary": "this is the details",
            "category": "thiswouldgood",
            "source_label": None,
            "access": "private",
            "id": "90TuDxDYQtiGyg5qhwYCg",
        },
        {
            "name": "EA16489_test_2",
            "owner": "WNEXFKQ7",
            "provider_url": "some_url",
            "summary": "Simple IOC trigger",
            "category": "None",
            "source_label": None,
            "access": "private",
            "id": "QtQcKTyySgaUdXlQPsXXWA",
        },
        {
            "name": "TEST",
            "owner": "WNEXFKQ7",
            "provider_url": "some_url",
            "summary": "Simple IOC trigger",
            "category": "None",
            "source_label": None,
            "access": "private",
            "id": "QtQcKTyySgaUdXlQPsXXWA",
        },
        {
            "name": "TEST",
            "owner": "WNEXFKQ7",
            "provider_url": "some_url",
            "summary": "Simple IOC trigger",
            "category": "None",
            "source_label": None,
            "access": "private",
            "id": "QtQcKTyySgaUdXlQPsX123",
        },
        {
            "name": "TEST123",
            "owner": "WNEXFKQ7",
            "provider_url": "some_url",
            "summary": "Simple IOC trigger",
            "category": "None",
            "source_label": None,
            "access": "private",
            "id": "QtQcKTyySgaUdXlQPsX123",
        },
    ]
}


FEED_POST_RESP = {
    "name": "base_name",
    "provider_url": "https://thisistheplace.com",
    "summary": "this is the details",
    "category": "thiswouldgood",
    "source_label": None,
    "access": "private",
    "id": "90TuDxDYQtiGyg5qhwYCg",
}


REPORT_INIT = {
    "id": "495df3a4-7e19-432d-846d-432e620dd57a",
    "title": "ReportTitle",
    "description": "The report description",
    "timestamp": 1642091205,
    "severity": 5,
    "link": "https://example.com",
    "tags": ["Alpha", "Bravo"],
    "iocs_v2": [
        {
            "id": "foo",
            "match_type": "equality",
            "field": "process_name",
            "values": ["evil.exe"],
        },
        {
            "id": "bar",
            "match_type": "equality",
            "field": "netconn_ipv4",
            "values": ["10.29.99.1"],
        },
    ],
    "visibility": "visible",
}


FEED_INIT = {
    "feedinfo": {
        "id": "qwertyuiop",
        "name": "base_name",
        "provider_url": "https://thisistheplace.com",
        "summary": "this is the details",
        "category": "thiswouldgood",
    },
    "reports": [REPORT_INIT],
}


FEED_CREATE_NO_REPORT_INIT = {
    "feedinfo": {
        "name": "My STIX Feed",
        "provider_url": "https://thisistheplace.com",
        "summary": "this is the details",
        "category": "thiswouldgood",
    },
    "reports": [],
}


WATCHLIST_FROM_FEED_IN = {
    "name": "Feed base_name",
    "description": "this is the details",
    "tags_enabled": True,
    "alerts_enabled": False,
    "classifier": {"key": "feed_id", "value": "qwertyuiop"},
}


WATCHLIST_FROM_FEED_OUT = {
    "name": "base_name",
    "description": "this is the details",
    "id": "ABCDEFGHabcdefgh",
    "tags_enabled": True,
    "alerts_enabled": False,
    "create_timestamp": 1234567890,
    "last_update_timestamp": 1234567890,
    "report_ids": None,
    "classifier": {"key": "feed_id", "value": "qwertyuiop"},
}


FEED_GET_RESP = {
    "feedinfo": {
        "name": "My STIX Feed",
        "provider_url": "https://thisistheplace.com",
        "summary": "feed for stix taxii",
        "category": "thiswouldgood",
        "source_label": None,
        "access": "private",
        "id": "feedid",
    },
}


FEED_RESP_POST_REPLACE_REPORTS = {
    "reports": [
        {
            "description": "feed for stix taxii",
            "id": "a539bb2a-9fcb-4a3c-b722-02a5c5f6ccb1",
            "severity": 5,
            "tags": [],
            "timestamp": 1643305793,
            "title": "Report My STIX Feed-1",
        }
    ]
}

IOC = {"id": "unsigned-chrome", "match_type": "query", "values": ["process_name:chrome.exe"]}
REPORT_INIT_ONE_IOCS = {
    "reports": [
        {
            "description": "feed for stix taxii",
            "severity": 5,
            "tags": [],
            "title": "Report My STIX Feed-1",
            "iocs_v2": [IOC],
        }
    ]
}

REPORT = {
    "description": "feed for stix taxii",
    "severity": 5,
    "tags": [],
    "title": "Report My STIX Feed-1",
    "iocs_v2": [IOC for i in range(1000)],
}

REPORT_WITH_1_IOC = {
    "description": "feed for stix taxii",
    "severity": 5,
    "tags": [],
    "title": "Report My STIX Feed-1",
    "iocs_v2": [IOC],
    "iocs_total_count": 1,
    "timestamp": 1643305793,
    "id": "17a7bc56-a41a-4269-9e69-dbfb27e9f235",
}

REPORT_WITH_3_IOC = {
    "description": "feed for stix taxii",
    "severity": 5,
    "tags": [],
    "title": "Report My STIX Feed-1",
    "iocs_v2": [IOC, IOC, IOC],
    "iocs_total_count": 1,
    "timestamp": 1643305793,
    "id": "17a7bc56-a41a-4269-9e69-dbfb27e9f235",
}


REPORTS_2_1_IOC = {"results": [REPORT_WITH_1_IOC, REPORT_WITH_1_IOC]}


REPORTS_2_WITH_1_AND_3 = {"reports": [REPORT_WITH_3_IOC, REPORT_WITH_1_IOC]}


REPORTS_10000_INIT_1000_IOCS = {"reports": [REPORT for i in range(10000)]}


REPORTS_3_INIT_1000_IOCS = {"reports": [REPORT for i in range(3)]}


REPORTS_4_INIT_1000_IOCS = {"reports": [REPORT for i in range(4)]}


REPORTS_GET_NO_REPORTS = {"results": []}


REPORTS_GET_ONE_IOCS = {
    "results": [
        {
            "description": "feed for stix taxii",
            "severity": 5,
            "tags": [],
            "title": "Report My STIX Feed-1",
            "iocs_v2": [{"id": "unsigned-chrome", "match_type": "query", "values": ["process_name:chrome.exe"]}],
            "iocs_total_count": 1,
        }
    ]
}

REPORT_WITH_1000_IOCS = {
    "description": "feed for stix taxii",
    "severity": 5,
    "tags": [],
    "title": "Report My STIX Feed",
    "iocs_v2": [IOC for i in range(1000)],
    "iocs_total_count": 1000,
    "timestamp": 1643305793,
    "id": "17a7bc56-a41a-4269-9e69-dbfb27e9f235",
}


REPORTS_GET_10000_WITH_1000_IOCS = {"results": [REPORT_WITH_1000_IOCS for i in range(10000)]}


REPORTS_GET_3_WITH_1000_IOCS = {"results": [REPORT_WITH_1000_IOCS for i in range(3)]}


REPORT_WITH_998_IOCS = {
    "description": "feed for stix taxii",
    "severity": 5,
    "tags": [],
    "title": "Report My STIX Feed",
    "iocs_v2": [IOC for i in range(998)],
    "iocs_total_count": 998,
}

REPORTS_GET_2_WITH_998_IOCS_1_1000 = {"results": [REPORT_WITH_998_IOCS, REPORT_WITH_1000_IOCS, REPORT_WITH_998_IOCS]}
