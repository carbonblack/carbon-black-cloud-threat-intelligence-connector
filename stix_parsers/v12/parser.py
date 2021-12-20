import logging
import subprocess

from stix.core import STIXPackage
from stix2elevator import elevate


class STIXParserError(Exception):
    pass


class ParserV12:
    """
    STIX 1.2 Parsing class

    This class entirely uses the function from the STIX Elevator
    `elevate` it works both for files and feeds.

    The validations are provided by a process call to `stix-validator`.
    """

    @staticmethod
    def _validate_file(xml_file):
        """Validating the STIX Feed."""
        validation_code = subprocess.call(["stix-validator", xml_file], stdout=subprocess.PIPE)
        if validation_code != 0:
            raise STIXParserError(f"Error during the validation. Error code {validation_code}.")
        return True

    @staticmethod
    def _parse_stix_objects(stix_package):
        """Parsing STIX.Observables and STIX.Indicators"""
        if not stix_package.indicators and not stix_package.observables:
            logging.info("No Indicators or Observables found in the XML")
            return []

    def _parse_stix_indicator(self, indicator):
        pass

    def _parse_stix_observable(self, observable):
        pass

    def parse_file(self, xml_file):
        """Parsing the STIX File Feed"""
        if self._validate_file(xml_file):
            stix_package = STIXPackage.from_xml(xml_file)
            reports = self._parse_stix_objects(stix_package)


    def parse_feed(self, *args, **kwargs):
        pass