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
    ]
}

FEED_GET_RESP = {
    "feedinfo": {
        "name": "base_name",
        "owner": "WNEXFKQ7",
        "provider_url": "https://thisistheplace.com",
        "summary": "this is the details",
        "category": "thiswouldgood",
        "source_label": None,
        "access": "private",
        "id": "90TuDxDYQtiGyg5qhwYCg",
    }
}

REPORT_INIT = {
    "id": "69e2a8d0-bc36-4970-9834-8687efe1aff7",
    "title": "ReportTitle",
    "description": "The report description",
    "timestamp": 1234567890,
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
        "name": "FeedName",
        "provider_url": "http://example.com",
        "summary": "Summary information",
        "category": "Intrusion",
        "source_label": "SourceLabel",
        "owner": "JRN",
        "access": "private",
    },
    "reports": [REPORT_INIT],
}

WATCHLIST_FROM_FEED_IN = {
    "name": "Subscribed feed",
    "description": "STIX/TAXII",
    "tags_enabled": True,
    "alerts_enabled": False,
    "classifier": {"key": "feed_id", "value": "qwertyuiop"},
}

WATCHLIST_FROM_FEED_OUT = {
    "name": "Subscribed feed",
    "description": "STIX/TAXII",
    "id": "ABCDEFGHabcdefgh",
    "tags_enabled": True,
    "alerts_enabled": False,
    "create_timestamp": 1234567890,
    "last_update_timestamp": 1234567890,
    "report_ids": None,
    "classifier": {"key": "feed_id", "value": "qwertyuiop"},
}
