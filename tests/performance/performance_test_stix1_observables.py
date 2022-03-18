import sys

from cbc_sdk import CBCloudAPI
from cybox.core import Observable, Observables
from cybox.objects.address_object import Address

from cbc_importer.stix_parsers.v1.parser import STIX1Parser


def create_observable():
    return Observable(title="ipv4", item=Address("127.0.0.1", category="ipv4-addr"))


def performance_test_stix_1_observables_parser(number_of_observables):
    cbc = CBCloudAPI(profile="default")
    parser = STIX1Parser(cbc)
    observables = Observables()
    for _ in range(number_of_observables):
        observables.add(create_observable())
    parser._parse_stix_observable(observables)
    assert len(parser.iocs) == number_of_observables


if __name__ == "__main__":
    performance_test_stix_1_observables_parser(int(sys.argv[1]))
