import pytest

from stix_parsers.v12.parser import ParserV12, STIXParserError

XML_FEED_TEST_VALID = "./tests/fixtures/files/stix_v1.2.xml"
XML_FEED_TEST_FAULTY = "./tests/fixtures/files/stix_v1.2_faulty.xml"


def test_validate_faulty_file():
    with pytest.raises(STIXParserError):
        parser = ParserV12()
        parser._validate_file(XML_FEED_TEST_FAULTY)


def test_validate_valid_file():
    parser = ParserV12()
    assert parser._validate_file(XML_FEED_TEST_VALID) == True


def test_parsing_file_valid():
    parser = ParserV12()
    parser.parse_file(XML_FEED_TEST_VALID)
