import pytest
from cbc_sdk.enterprise_edr import IOC_V2
from sdv.errors import ValidationError

from cbc_importer.stix_parsers.v1.parser import STIX1Parser

XML_FEED_TEST_VALID = "./tests/fixtures/files/stix_v1.2.xml"
XML_FEED_TEST_FAULTY = "./tests/fixtures/files/stix_v1.2_faulty.xml"
XML_FEED_TEST_EMPTY = "./tests/fixtures/files/empty_file.xml"


def test_parser_empty_file(cbcsdk_mock):
    """Test with empty file."""
    parser = STIX1Parser(cbcsdk_mock.api)
    with pytest.raises(ValidationError):
        parser.parse_file(XML_FEED_TEST_EMPTY)


def test_parser_faulty_stix_12(cbcsdk_mock):
    """Test with faulty stix v1.2."""
    parser = STIX1Parser(cbcsdk_mock.api)
    with pytest.raises(ValidationError):
        parser.parse_file(XML_FEED_TEST_FAULTY)


def test_parser_valid_file_12(cbcsdk_mock):
    """Test with valid file v1.2."""
    parser = STIX1Parser(cbcsdk_mock.api)
    objs = parser.parse_file(XML_FEED_TEST_VALID)
    assert len(objs) == 4
    assert isinstance(objs[0], IOC_V2)


def test_parser_raises_value_error(monkeypatch, cbcsdk_mock):
    """Test raising value error"""
    parser = STIX1Parser(cbcsdk_mock.api)

    def raise_value_error(*args, **kwargs):
        raise ValueError

    monkeypatch.setattr("stix.core.STIXPackage.from_xml", raise_value_error)
    with pytest.raises(ValueError):
        parser.parse_file(XML_FEED_TEST_VALID)
