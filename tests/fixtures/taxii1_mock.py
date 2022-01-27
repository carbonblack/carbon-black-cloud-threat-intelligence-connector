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
from unittest.mock import Mock

XML_COLLECTION = "./tests/fixtures/files/stix_v1.2.xml"


class MockCollection:
    def __init__(self, name) -> None:
        self.name = name


class ContentBlockMock:
    def __init__(self, xml_stix_package) -> None:
        with open(xml_stix_package, "rb") as file:
            self.content = file.read()


class TAXII1ServerMock:
    @staticmethod
    def get_collections():
        return [MockCollection("COLLECTION_1"), MockCollection("COLLECTION_2")]

    @staticmethod
    def poll(*args, **kwargs):
        yield ContentBlockMock(XML_COLLECTION)
