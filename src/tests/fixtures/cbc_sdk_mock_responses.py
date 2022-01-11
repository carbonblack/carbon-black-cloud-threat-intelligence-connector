# -*- coding: utf-8 -*-

# *******************************************************
# Copyright (c) VMware, Inc. 2020-2021. All Rights Reserved.
# SPDX-License-Identifier: MIT
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
    ]
}

FEED_GET_RESP = {
"feedinfo": {
    "name": "IBM IRIS Feed",
    "owner": "WNEXFKQ7",
    "provider_url": "https://thisistheplace.com",
    "summary": "this is the details",
    "category": "thiswouldgood",
    "source_label": None,
    "access": "private",
    "id": "90TuDxDYQtiGyg5qhwYCg",
}
}
