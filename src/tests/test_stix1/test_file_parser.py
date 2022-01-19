import pytest
from cbc_sdk.enterprise_edr import IOC_V2
from sdv.errors import ValidationError

from stix_parsers.stix1_parser import STIX1Parser

XML_FEED_TEST_VALID = "./src/tests/fixtures/files/stix_v1.2.xml"
XML_FEED_TEST_FAULTY = "./src/tests/fixtures/files/stix_v1.2_faulty.xml"
XML_FEED_TEST_EMPTY = "./src/tests/fixtures/files/empty_file.xml"


def test_parser_empty_file(cbcsdk_mock):
    parser = STIX1Parser(cbcsdk_mock.api)
    with pytest.raises(ValidationError):
        parser.parse_file(XML_FEED_TEST_EMPTY)


def test_parser_faulty_stix_12(cbcsdk_mock):
    parser = STIX1Parser(cbcsdk_mock.api)
    with pytest.raises(ValidationError):
        parser.parse_file(XML_FEED_TEST_FAULTY)


def test_parser_valid_file_12(cbcsdk_mock):
    parser = STIX1Parser(cbcsdk_mock.api)
    objs = parser.parse_file(XML_FEED_TEST_VALID)
    assert len(objs) == 3158
    assert isinstance(objs[0], IOC_V2)
