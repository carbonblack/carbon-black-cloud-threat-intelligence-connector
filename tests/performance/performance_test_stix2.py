import sys

from cbc_sdk import CBCloudAPI
from stix2 import Bundle, Indicator

from cbc_importer.stix_parsers.v2.parser import STIX2Parser


def create_indicator():
    return Indicator(
        name="TestName",
        pattern="[file:hashes.'SHA-256' = 'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c']",
        pattern_type="stix",
    )


def create_stix_bundle(indicators):
    return Bundle(indicators)


def performance_test_stix_20_parser(number_of_indicators):
    cbc = CBCloudAPI(profile="default")
    indicators = [create_indicator() for i in range(number_of_indicators)]
    bundle = create_stix_bundle(indicators)
    parser = STIX2Parser(cbc, stix_version="2.1")
    process_objects_iocs = parser._parse_stix_objects(bundle)
    assert len(process_objects_iocs) == number_of_indicators


if __name__ == "__main__":
    performance_test_stix_20_parser(int(sys.argv[1]))
