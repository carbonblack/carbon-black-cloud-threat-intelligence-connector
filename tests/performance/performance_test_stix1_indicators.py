import sys

from cbc_sdk import CBCloudAPI
from cybox.core import Observable
from cybox.objects.address_object import Address
from stix.core import Indicator

from cbc_importer.stix_parsers.v1.parser import STIX1Parser


def create_indicator():
    indicator = Indicator(title="RandomIpv4")
    observable = Observable(title="ipv4", item=Address("127.0.0.1", category="ipv4-addr"))
    indicator.add_observable(observable)
    return indicator


def performance_test_stix_1_indicators_parser(number_of_indicators):
    cbc = CBCloudAPI(profile="default")
    parser = STIX1Parser(cbc)
    indicators = [create_indicator() for _ in range(number_of_indicators)]
    parser._parse_stix_indicators(indicators)
    assert len(parser.iocs) == number_of_indicators


if __name__ == "__main__":
    performance_test_stix_1_indicators_parser(int(sys.argv[1]))
