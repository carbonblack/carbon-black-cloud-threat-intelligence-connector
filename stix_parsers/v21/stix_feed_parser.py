import logging
import typing

import stix2
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr import IOC_V2
from stix2 import parse as stix2parse
from stix2.exceptions import InvalidValueError
from stix2.v21 import Indicator, File
from stix2patterns.v21.pattern import Pattern
from stix2validator import validate_file

from stix_parsers.v21.stix_pattern_parser import STIXPatternParser


class ParserV21:
    """
    Parser for translating `stix2.v21.Indicator` and `stix2.v21.ObservedData`
    objects to `cbc_sdk.enterprise_edr.IOC_V2`.
    """

    def __init__(self, cbcapi: CBCloudAPI, strict=False) -> None:
        """
        Args:
            strict (bool): If strict is True the script will terminate if it encounters
            a parsing error, otherwise it will log it and continue.
            cbcapi (CBCloudAPI): The Authorized CBC Instance

        """
        self.STIX_VERSION = "2.1"
        self.cbcapi = cbcapi
        self.strict = strict

    def parse_file(self, file: str) -> typing.List[IOC_V2]:
        """
        Parsing a STIX 2.1 Feed as a file

        Args:
            file (str): Path to the STIX2.1 feed file in a JSON Format.

        Returns:
           List of parsed STIX Objects into IOCs.
        """
        validate = validate_file(file)
        if validate.is_valid:
            with open(file) as stix_file:
                stix_content = stix2parse(
                    stix_file, allow_custom=True, version=self.STIX_VERSION
                )
                if stix_content.objects:
                    return self._parse_stix_objects(stix_content)
                else:
                    logging.info("No STIX objects found")
                    return []
        else:
            raise ValueError(f"JSON file is not valid or empty: {validate.as_dict()}")

    def parse_feed(self, *args, **kwargs):
        pass

    def _parse_stix_objects(self, stix_content: stix2.Bundle) -> typing.List[IOC_V2]:
        """
        Parser for `stix2.v21.Indicator`.

        Args:
            stix_content (stix2.Bundle): STIX Bundle Object containing the STIX Objects.

        Returns:
           List of parsed STIX Objects into IOCs.
        """
        iocs = []
        for stix_obj in stix_content.objects:
            if isinstance(stix_obj, Indicator):
                if self.strict:
                    iocs += self._parse_stix_indicator(stix_obj)
                else:
                    try:
                        iocs += self._parse_stix_indicator(stix_obj)
                    except InvalidValueError:
                        logging.error(f"Encountered `InvalidValueError` during the parsing of {stix_obj.id}")
        return iocs

    def _parse_stix_file(self, file: File):
        pass

    def _parse_stix_indicator(self, indicator: Indicator) -> typing.List[IOC_V2]:
        """
        Parsing a single STIX Indicator object into `IOC_V2`.

        Note: Sometimes there is more than one key:value in a single Indicator pattern
        this is why we return List here.

        Args:
            indicator (stix2.v21.Indicator): STIX Indicator Object.

        Returns:
            List of parsed IOCs.
        """
        logging.info(f"Parsing {indicator.id}")
        iocs = []
        stix_pattern_parser = STIXPatternParser()
        Pattern(indicator.pattern).walk(stix_pattern_parser)
        for ioc in stix_pattern_parser.matched_iocs:
            iocs.append(
                IOC_V2.create_equality(
                    self.cbcapi, indicator.id, ioc["field"], ioc["value"]
                )
            )
        return iocs
