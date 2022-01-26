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

import json

JSON_FEED_TEST_VALID = "./tests/fixtures/files/stix_v2.1.json"
JSON_FEED_TEST_VALID_STIX_20 = "./tests/fixtures/files/stix_v2.0.json"


class MockCollection:
    def __init__(self, id, serve_data):
        self.serve_data = serve_data
        self.id = id

    def get_objects(self, *args, **kwargs):
        with open(self.serve_data) as stix_content:
            return json.load(stix_content)


class APIRootsMock:
    def __init__(self, title, collections) -> None:
        self.title = title
        self.collections = collections


class TAXII2ServerMock:

    api_roots = [
        APIRootsMock(
            title="Malware Research Group",
            collections=[
                MockCollection("1", JSON_FEED_TEST_VALID),
                MockCollection("2", JSON_FEED_TEST_VALID),
            ],
        ),
        APIRootsMock(title="Test Data", collections=[MockCollection("1", JSON_FEED_TEST_VALID)]),
        APIRootsMock(
            title="Test Data STIX2.0",
            collections=[MockCollection("1", JSON_FEED_TEST_VALID_STIX_20)],
        ),
    ]
