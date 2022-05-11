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
from typing import List, Union

import stix2
import taxii2client
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr import IOC_V2
from stix2 import Indicator
from stix2 import parse as stix2parse
from stix2.exceptions import InvalidValueError
from stix2patterns.pattern import Pattern
from stix2validator import validate_file
from taxii2client import as_pages

from cbc_importer.stix_parsers.v2.pattern_parser import STIXPatternParser

logger = logging.getLogger(__name__)


class STIX2Parser:
    """Parser for translating STIX Indicator
    objects to `cbc_sdk.enterprise_edr.IOC_V2`.

    The parser can be used for 2.0 and 2.1
    by default it uses the 2.1 version.
    """

    def __init__(self, cbcapi: CBCloudAPI, stix_version="2.1") -> None:
        """
        Args:
            cbcapi (CBCloudAPI): authenticated CBC SDK instance
        """
        self.stix_version = stix_version
        self.cbcapi = cbcapi

    def parse_file(self, file: str) -> List[IOC_V2]:
        """Parsing STIX 2.0 and 2.1 content

        Args:
            file (str): Path to the STIX feed file in a JSON Format.

        Raises:
            ValueError: If the JSON file is not valid or empty.
            ValueError: If STIX version is unsupported.

        Returns:
            List[IOC_V2]: of parsed STIX Objects into IOCs.
        """
        logger.info(f"Parsing a file {file}")
        if self.stix_version == "2.1" or self.stix_version == "2.0":
            validate = validate_file(file)
            if validate.is_valid:
                with open(file) as stix_file:
                    stix_content = stix2parse(stix_file, allow_custom=True, version=self.stix_version)
                    return self._parse_stix_objects(stix_content)
            else:
                raise ValueError(f"JSON file is not valid or empty: {validate.as_dict()}")
        else:
            raise ValueError("Unsupported STIX version.")

    def parse_taxii_server(
        self,
        server: taxii2client.Server,
        gather_data: Union[str, List[dict]] = "*",
        **kwargs,
    ) -> List[IOC_V2]:
        """Parsing a TAXII Server with STIX 2.0 and 2.1 data

        The structure of the `gather_data` follows:

        ```
        [
            {
                "title": "api_root_title",
                "collections": ["collection-a", "collection-b"]
            },
        ]
        ```

        The following structure will get the API Root that has title `STIX DATA` and
        gather the list of collections that is provided `collection_id_1` and collection_id_2`.

        By default, `gather_data` equals to `*` which means that it will get all the API Roots and
        all the collections inside them. If all the collections are desired, a `*` can be used as
        an argument in `collections`.

        You can also specify multiple API Roots.

        ```
        [
            {
                "title": "api_root_title",
                "collections": ["collection-a", "collection-b"]
            },
            {
                "title": "api_root_title2",
                "collections": "*"
            }
        ]
        ```

        Args:
            server (taxii2client.Server): Initialized instance of a `taxii2client.Server` class.
            gather_data (str | List[dict]): String or dict representing what data will be gathered.
            **kwargs (dict): Dictionary to be provided in `as_pages`, usually used for `added_after`
                kwarg which will query the server with specific time frame results.

        Returns:
            List[IOC_V2]: of parsed STIX Objects into IOCs.
        """
        iocs = []
        collections_to_gather = self._gather_collections(server.api_roots, gather_data)
        for collection in collections_to_gather:
            for bundle in as_pages(collection.get_objects, per_request=500, **kwargs):
                if bundle:
                    stix_content = stix2parse(bundle, allow_custom=True, version=self.stix_version)
                    iocs += self._parse_stix_objects(stix_content)
        return iocs

    def _gather_collections(
        self,
        api_roots: Union[List[taxii2client.ApiRoot], str],
        gather_data: Union[List[dict], str],
    ) -> List[taxii2client.Collection]:
        """Gather the specified collections from the `gather_data` dictionary.

        Args:
            api_roots (List[taxii2client.ApiRoot] | str): List of ApiRoot
                objects coming from `taxii2client` or a "*" string meaning that all
                of the information provided by `/discovery` path is going to be
                gathered.
            gather_data (dict): Dictionary of data to be gathered, containing
                API Root titles and collections IDs inside of them.

        Returns:
           List[taxii2client.Collection]: of gathered Collections
        """
        roots_to_gather = []
        collections_to_gather = []

        if isinstance(gather_data, str) and gather_data == "*":
            for root in api_roots:
                if len(root.collections) > 0:  # type: ignore
                    collections_to_gather += root.collections  # type: ignore
        else:
            roots_to_gather += self._get_roots(api_roots, gather_data)  # type: ignore
            collections_to_gather += self._get_collections(roots_to_gather, gather_data)  # type: ignore

        return collections_to_gather

    @staticmethod
    def _get_roots(api_roots: List[taxii2client.ApiRoot], gather_data: List[dict]) -> List[taxii2client.ApiRoot]:
        """Gather the specified roots from the `gather_data` dictionary.

        Args:
            api_roots (List[taxii2client.ApiRoot] | str): List of ApiRoot objects.
            gather_data (List[dict]): List of dictionaries of data to be gathered, containing
                API Root titles and collections IDs inside of them.

        Returns:
           List[taxii2client.ApiRoot]: of gathered Collections
        """
        roots_to_gather = []
        for root in api_roots:
            for entry in gather_data:
                if entry["title"] == root.title:
                    roots_to_gather.append(root)
        return roots_to_gather

    @staticmethod
    def _get_collections(
        api_roots: List[taxii2client.ApiRoot], gather_data: List[dict]
    ) -> List[taxii2client.Collection]:
        """Gather the specified collections from gathered API roots.

        Args:
            api_roots (List[taxii2client.ApiRoot] | str): List of ApiRoot objects.
            gather_data (List[dict]): List of dictionaries of data to be gathered, containing
                API Root titles and collections IDs inside of them.

        Returns:
           List[taxii2client.Collection]: of gathered Collections
        """
        collections_to_gather = []
        for root in api_roots:
            for entry in gather_data:
                if root.title == entry["title"]:
                    if isinstance(entry["collections"], str) and entry["collections"] == "*":
                        collections_to_gather += root.collections
                        break
                    else:
                        for collection in root.collections:
                            if collection.id in entry["collections"]:
                                collections_to_gather.append(collection)

        return collections_to_gather

    def _parse_stix_objects(self, stix_content: stix2.Bundle) -> List[IOC_V2]:
        """Parser for `stix2.Indicator`.

        Args:
            stix_content (stix2.Bundle): STIX Bundle Object containing the STIX Objects

        Returns:
            List[IOC_V2]: of parsed STIX Objects into IOCs.
        """
        iocs = []
        # Sometimes the Bundle doesn't have `objects`
        if hasattr(stix_content, "objects"):
            for stix_obj in stix_content.objects:
                stix_type = getattr(stix_obj, "type", None)
                if stix_type and stix_type == "indicator":
                    iocs += self._parse_stix_indicator(stix_obj)
        return iocs

    def _parse_stix_indicator(self, indicator: Indicator) -> List[IOC_V2]:
        """Parsing a single STIX Indicator object into `IOC_V2`.

        Note: Sometimes there is more than one key:value in a single Indicator pattern
        this is why we return List here.

        Args:
            indicator (stix2.Indicator): STIX Indicator Object.

        Returns:
            List[IOC_V2]: of parsed STIX Objects into IOCs.
        """
        logger.info(f"Parsing {indicator.id}")
        iocs = []
        try:
            stix_pattern_parser = STIXPatternParser()
            Pattern(indicator.pattern).walk(stix_pattern_parser)
        except InvalidValueError:
            logger.warn(f"Indicator {indicator.id} has invalid pattern.")
            return []
        for ioc in stix_pattern_parser.matched_iocs:
            iocs.append(IOC_V2.create_equality(self.cbcapi, indicator.id, ioc["field"], ioc["value"]))
        return iocs
