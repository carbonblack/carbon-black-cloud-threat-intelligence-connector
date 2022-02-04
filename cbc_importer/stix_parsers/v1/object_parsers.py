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

import re
from typing import Union

import validators
from cybox.objects.address_object import Address
from cybox.objects.domain_name_object import DomainName
from cybox.objects.file_object import File
from cybox.objects.uri_object import URI


class AddressParser:
    """STIX 1.x `Address` Parser

    Parses `cybox.objects.address_object.Address` into an dict,
    that can be used as `initial_data` for `cbc_sdk.enterprise_edr.IOC_V2`
    """

    CB_FIELD_IPV4 = "netconn_ipv4"
    CB_FIELD_IPV6 = "netconn_ipv6"

    def __init__(self, address: Address) -> None:
        """
        Args:
            address (cybox.objects.address_object.Address)
        """
        self.address = address
        self._type = address.category or None

    def parse(self) -> Union[dict, None]:
        """Parsing IPV4/IPV6 into CBC IOC dict

        Returns:
            dict | None
        """
        if self._type and self._type == "ipv4-addr":
            return self._parse_ipv4()
        elif self._type and self._type == "ipv6-addr":
            return self._parse_ipv6()
        else:
            return None

    def _parse_ipv4(self) -> Union[dict, None]:
        """Parsing IPV4 into CBC IOC dict

        Returns:
            dict | None
        """
        value = self.address.to_dict()["address_value"]

        # Sometimes the value key can be a dictionary
        # oftentimes its when it contains multiple values.
        if isinstance(value, dict):
            value = value["value"]

        id_ = self.address._parent.id_
        clean_id = re.sub(r"\W+", "", id_)
        values = []
        if isinstance(value, list):
            for v in value:
                if validators.ipv4(v):
                    values.append(v)
        else:
            if validators.ipv4(value):
                values.append(value)
        if values:
            return {"id": clean_id, "match_type": "equality", "field": self.CB_FIELD_IPV4, "values": values}
        return None

    def _parse_ipv6(self) -> Union[dict, None]:
        """Parsing an IPV6 into CBC IOC dict

        Returns:
            dict | None
        """
        value = self.address.to_dict()["address_value"]

        # Sometimes the value key can be a dictionary
        # oftentimes its when it contains multiple values.
        if isinstance(value, dict):
            value = value["value"]

        id_ = self.address._parent.id_
        clean_id = re.sub(r"\W+", "", id_)
        values = []
        if isinstance(value, list):
            for v in value:
                if validators.ipv6(v):
                    values.append(v)
        else:
            if validators.ipv6(value):
                values.append(value)
        if values:
            return {"id": clean_id, "match_type": "equality", "field": self.CB_FIELD_IPV6, "values": values}
        return None


class DomainNameParser:
    """STIX 1.x `Domain` Parser

    Parses `cybox.objects.domain_name_object.DomainName` into an dict,
    that can be used as `initial_data` for `cbc_sdk.enterprise_edr.IOC_V2`
    """

    CB_FIELD = "netconn_domain"

    def __init__(self, domain_name: DomainName) -> None:
        """
        Args:
            domain_name (cybox.objects.domain_name_object.DomainName)
        """
        self.domain_name = domain_name

    def parse(self) -> Union[dict, None]:
        """Parsing DomainName into CBC IOC dict

        Returns:
            dict | None
        """
        value = self.domain_name.to_dict()["value"]

        # Sometimes the value key can be a dictionary
        # oftentimes its when it contains multiple values.
        if isinstance(value, dict):
            value = value["value"]

        id_ = self.domain_name._parent.id_
        clean_id = re.sub(r"\W+", "", id_)
        values = []
        if isinstance(value, list):
            for v in value:
                if validators.domain(v):
                    values.append(v)
        else:
            if validators.domain(value):
                values.append(value)
        if values:
            return {"id": clean_id, "match_type": "equality", "field": self.CB_FIELD, "values": values}
        return None


class FileParser:
    """STIX 1.x `File` Parser

    Parses `cybox.objects.file_object.File` into an dict,
    that can be used as `initial_data` for `cbc_sdk.enterprise_edr.IOC_V2`
    """

    CB_FIELD_PROCESS_HASH = "process_hash"
    CB_FIELD_FILE_NAME = "process_name"

    def __init__(self, file: File) -> None:
        """
        Args:
            file (cybox.objects.file_object.File)
        """
        self.file = file

    def parse(self) -> Union[dict, None]:
        """Parsing File into CBC IOC dict

        Returns:
            dict | None
        """
        value = self.file
        id_ = self.file._parent.id_
        clean_id = re.sub(r"\W+", "", id_)
        query_string = []
        if hasattr(value, "file_name") and value.file_name is not None:
            query_string.append(f"{self.CB_FIELD_FILE_NAME}:{str(value.file_name)}")
        elif hasattr(value, "hashes"):
            for i in value.hashes:
                if str(i.type_) == "SHA256":
                    if validators.sha256(str(i)):
                        query_string.append(f"{self.CB_FIELD_PROCESS_HASH}:{str(i)}")
                elif str(i.type_) == "MD5":
                    if validators.md5(str(i)):
                        query_string.append(f"{self.CB_FIELD_PROCESS_HASH}:{str(i)}")
        if query_string:
            _query_string = " OR ".join(query_string)
            return {"id": clean_id, "match_type": "query", "values": [_query_string]}
        return None


class URIParser:
    """STIX 1.x `URI` Parser

    Parses `cybox.objects.uri_object.URI` into an dict,
    that can be used as `initial_data` for `cbc_sdk.enterprise_edr.IOC_V2`
    """

    CB_FIELD = "netconn_domain"

    def __init__(self, uri: URI) -> None:
        """
        Args:
            uri (cybox.objects.uri_object.URI)
        """
        self.uri = uri

    def parse(self) -> Union[dict, None]:
        """Parsing URI into CBC IOC dict

        Returns:
            dict | None
        """
        value = self.uri.to_dict()["value"]

        # Sometimes the value key can be a dictionary
        # oftentimes its when it contains multiple values.
        if isinstance(value, dict):
            value = value["value"]

        id_ = self.uri._parent.id_
        clean_id = re.sub(r"\W+", "", id_)
        values = []
        if isinstance(value, list):
            for v in value:
                if validators.url(v):
                    values.append(v)
        else:
            if validators.url(value):
                values.append(value)
        if values:
            return {"id": clean_id, "match_type": "equality", "field": self.CB_FIELD, "values": values}
        return None
