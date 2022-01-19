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
import logging
import uuid
from io import BytesIO
from pydoc import cli
from typing import List

from cabby import Client11
from cabby.entities import Collection
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr import IOC_V2
from cybox.core.observable import Observables
from cybox.objects.address_object import Address
from cybox.objects.domain_name_object import DomainName
from cybox.objects.file_object import File
from cybox.objects.uri_object import URI
from lxml import etree
from lxml.etree import XMLSyntaxError
from sdv import validate_xml
from stix.core import Indicators, STIXPackage

from stix_parsers.stix1_object_parsers import (
    AddressParser,
    DomainNameParser,
    FileParser,
    URIParser,
)


class STIX1Parser:

    CB_MAPPINGS = {
        DomainName: DomainNameParser,
        Address: AddressParser,
        File: FileParser,
        URI: URIParser,
    }

    def __init__(self, cbcapi: CBCloudAPI) -> None:
        self.cbcapi = cbcapi
        self._client = None

    def parse_file(self, file: str) -> List[IOC_V2]:
        iocs = []
        if validate_xml(file).is_valid:
            stix_package = STIXPackage.from_xml(file)
            indicators = stix_package.indicators
            observables = stix_package.observables
            if indicators and len(indicators) > 0:
                iocs += self._parse_stix_indicators(indicators)
            elif observables and len(observables) > 0:
                iocs += self._parse_stix_observable(observables)
        else:
            raise ValueError("File is not valid.")
        return iocs

    def parse_taxii_server(self, client: Client11, collections: list, **kwargs) -> List[IOC_V2]:
        iocs = []
        collections_to_gather = self._get_collections(client.get_collections(), collections)
        for collection_name in collections_to_gather:
            content_block = client.poll(collection_name, **kwargs)
            for block in content_block:
                try:
                    xml_content = etree.parse(BytesIO(block.content))
                    stix_package = STIXPackage.from_xml(xml_content)
                    indicators = stix_package.indicators
                    observables = stix_package.observables
                    if indicators and len(indicators) > 0:
                        iocs += self._parse_stix_indicators(indicators)
                    elif observables and len(observables) > 0:
                        iocs += self._parse_stix_observable(observables)
                except XMLSyntaxError:
                    # Sometimes there is a invalid block of XML
                    continue
                except Exception as e:
                    logging.error(e, exc_info=True)
                    continue
            return iocs

    def _parse_stix_observable(self, observables: Observables) -> List[IOC_V2]:
        iocs = []
        for observable in observables:
            try:
                observable_props = observable.object_.properties
                parser = self.CB_MAPPINGS[type(observable_props)](observable_props)
                ioc_dict = parser.parse()
                if ioc_dict:
                    ioc_id = str(uuid.uuid4())
                    ioc = IOC_V2(self.cbcapi, ioc_id, ioc_dict)
                    iocs.append(ioc)
            except KeyError:
                # If there is not parser for that object
                return []
            except AttributeError:
                # Sometimes the `observable.object_.properties` has no properties
                return []
        return iocs

    def _parse_stix_indicators(self, indicators: Indicators) -> List[IOC_V2]:
        iocs = []
        for indicator in indicators:
            if not indicator.observable:
                return []
            try:
                observable_props = indicator.observable.object_.properties
                parser = self.CB_MAPPINGS[type(observable_props)](observable_props)
                ioc_dict = parser.parse()
                ioc_id = str(uuid.uuid4())
                if ioc_dict:
                    ioc = IOC_V2(self.cbcapi, ioc_id, ioc_dict)
                    iocs.append(ioc)
            except KeyError:
                # If there is not parser for that object
                return []
            except AttributeError:
                # Sometimes the `observable.object_.properties` has no properties
                return []
        return iocs

    @staticmethod
    def _get_collections(client_collections: List[Collection], collections: list) -> list:
        gathered_collections = []
        for collection in client_collections:
            if collection.name in collections:
                gathered_collections.append(collection.name)
        return gathered_collections
