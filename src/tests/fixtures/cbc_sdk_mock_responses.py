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

FEED_POST_RESP = {
    "name": "base_name",
    "provider_url": "https://thisistheplace.com",
    "summary": "this is the details",
    "category": "thiswouldgood",
    "source_label": None,
    "access": "private",
    "id": "90TuDxDYQtiGyg5qhwYCg",
}

FEED_GET_RESP = {
    "feedinfo": {
        "name": "base_name",
        "provider_url": "https://thisistheplace.com",
        "summary": "this is the details",
        "category": "thiswouldgood",
        "source_label": None,
        "access": "private",
        "id": "90TuDxDYQtiGyg5qhwYCg",
    },
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

FEED_CREATE_NO_REPORT_INIT = {
    "feedinfo": {
        "name": "base_name",
        "provider_url": "https://thisistheplace.com",
        "summary": "this is the details",
        "category": "thiswouldgood",
    },
    "reports": [],
}
