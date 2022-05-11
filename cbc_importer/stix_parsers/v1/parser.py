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
from typing import List, Union

from cabby import Client10, Client11
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

from cbc_importer.stix_parsers.v1.object_parsers import (
    AddressParser,
    DomainNameParser,
    FileParser,
    URIParser,
)

logger = logging.getLogger(__name__)


class STIX1Parser:
    """Parser for translating STIX Indicator
    objects to `cbc_sdk.enterprise_edr.IOC_V2`.

    The parser can be used for STIX 1.x
    by default the client that can be used is for 1.0 and 1.2.
    """

    CB_MAPPINGS = {
        DomainName: DomainNameParser,
        Address: AddressParser,
        File: FileParser,
        URI: URIParser,
    }

    def __init__(self, cbcapi: CBCloudAPI) -> None:
        """
        Args:
            cbcapi (CBCloudAPI): [description]
        """
        self.cbcapi = cbcapi
        self.iocs: List[IOC_V2] = []

    def parse_file(self, file: str) -> List[IOC_V2]:
        """Parsing STIX 1x content

        Args:
            file (str): Path to the STIX feed file in XML Format.

        Raises:
            ValueError: If the XML file is not valid or empty.

        Returns:
           List[IOC_V2] of parsed STIX Objects into IOCs.
        """
        if validate_xml(file).is_valid:
            stix_package = STIXPackage.from_xml(file)
            indicators = stix_package.indicators
            observables = stix_package.observables
            if indicators and len(indicators) > 0:
                self._parse_stix_indicators(indicators)
            elif observables and len(observables) > 0:
                self._parse_stix_observable(observables)
        else:
            raise ValueError("File is not valid.")
        return self.iocs

    def parse_taxii_server(
        self,
        client: Union[Client11, Client10],
        collections: Union[list, str] = "*",
        collection_management_uri: str = None,
        **kwargs,
    ) -> List[IOC_V2]:
        """Parsing a TAXII Server

        It uses the default discovery services and it finds the Feed Management Service
        among them.

        `collections` represents the collections that the script will collect,
        by default it collects data from all of the collections.

        Args:
            client (Union[Client11, Client10]): authenticated cabby client
            collections (list | str): the list of collections to be gathered
            collection_management_uri (str): the uri for the collection management
            **kwargs (dict): commonly used for `begin_date` and `end_date` to
                support content range.

        Returns:
            List[IOC_V2]: List of parsed Indicators into IOCs
        """
        # `get_collections` needs management path
        collections_to_gather = self._get_collections(
            client.get_collections(uri=collection_management_uri), collections
        )
        for collection_name in collections_to_gather:
            content_block = client.poll(collection_name, **kwargs)
            for block in content_block:
                try:
                    xml_content = etree.parse(BytesIO(block.content))
                    stix_package = STIXPackage.from_xml(xml_content)

                    indicators = stix_package.indicators
                    observables = stix_package.observables

                    if indicators and len(indicators) > 0:
                        self._parse_stix_indicators(indicators)
                    elif observables and len(observables) > 0:
                        self._parse_stix_observable(observables)

                except XMLSyntaxError as e:
                    # Sometimes there is a invalid block of XML
                    logger.exception(msg=e)
                    logger.error(f"XMLSyntaxError occurred at {stix_package} with XML Content: {xml_content}")
                except Exception as e:
                    # Sometimes there is an error within the STIX parsing
                    # such as `GDSParseError` but it can be different.
                    logger.exception(msg=e)
        return self.iocs

    def _parse_stix_observable(self, observables: Observables) -> None:
        """Parsing a STIX Observable object into list of IOCs

        Args:
            observables (Observables): Observables object that comes from `STIXPackage`
        """
        for observable in observables:
            try:
                logger.info(f"Parsing {observable.id_}")
                observable_props = observable.object_.properties
                parser = self.CB_MAPPINGS[type(observable_props)](observable_props)
                ioc_dict = parser.parse()  # type: ignore
                if ioc_dict:
                    ioc_id = str(uuid.uuid4())
                    ioc = IOC_V2(self.cbcapi, ioc_id, ioc_dict)
                    self.iocs.append(ioc)
            except KeyError:
                # If there is not parser for that object
                return None
            except AttributeError:
                logger.warn(f"Observable {observable} has no `object_.properties`")
                # Sometimes the `observable.object_.properties` has no properties
                return None

    def _parse_stix_indicators(self, indicators: Indicators) -> None:
        """Parsing a STIX Indicator object into list of IOCs

        Args:
            indicators (Indicators): Indicators object that comes from `STIXPackage`
        """
        for indicator in indicators:
            if not indicator.observable:
                return None
            logger.info(f"Parsing {indicator.id_}")
            try:
                if (
                    hasattr(indicator.observable, "observable_composition")
                    and indicator.observable.observable_composition is not None
                ):
                    # Whenever there is a composition within the `observable`
                    for observable in indicator.observable.observable_composition:
                        observable_props = observable.object_.properties
                        self._create_ioc_from_observable_props(observable_props)
                elif (
                    hasattr(indicator.observable, "object_")
                    and hasattr(indicator.observable.object_, "properties")
                    and indicator.observable.object_.properties is not None
                ):
                    observable_props = indicator.observable.object_.properties
                    self._create_ioc_from_observable_props(observable_props)
            except KeyError:
                # If there is no parser for that object
                return None
            except AttributeError:
                continue

    def _create_ioc_from_observable_props(self, observable_props: Union[Address, DomainName, File, URI]) -> None:
        """Creates an IOC from observable properties

        Args:
            observable_props (Union[Address, DomainName, File, URI]): the properties of the observable.
        """
        parser = self.CB_MAPPINGS[type(observable_props)](observable_props)
        ioc_dict = parser.parse()  # type: ignore
        ioc_id = str(uuid.uuid4())
        if ioc_dict:
            ioc = IOC_V2(self.cbcapi, ioc_id, ioc_dict)
            self.iocs.append(ioc)

    @staticmethod
    def _get_collections(client_collections: List[Collection], collections: Union[list, str]) -> list:
        """Getting the collections specified in `collections` and
        returns the collections that match .

        Args:
            client_collections (List[Collection]): typically that comes from `Client11.get_collections`
            collections (list | str): Specified collections to be filtered

        Returns:
            list: collections to be gathered
        """
        gathered_collections = []
        if isinstance(collections, str) and collections == "*":
            return [collection.name for collection in client_collections]
        for collection in client_collections:
            if collection.name in collections:
                gathered_collections.append(collection.name)
        return gathered_collections
