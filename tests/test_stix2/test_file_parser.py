import pytest
from cbc_sdk.enterprise_edr import IOC_V2

from cbc_importer.stix_parsers.v2.parser import STIX2Parser

JSON_FEED_TEST_VALID_21 = "./tests/fixtures/files/stix_v2.1.json"
JSON_FEED_TEST_FAULTY_21 = "./tests/fixtures/files/stix_v2.1_faulty.json"
JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_21 = "./tests/fixtures/files/stix_v2.1_indicator_pattern_error.json"
JSON_FEED_TEST_VALID_20 = "./tests/fixtures/files/stix_v2.0.json"
JSON_FEED_TEST_FAULTY_20 = "./tests/fixtures/files/stix_v2.0_faulty.json"
JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_20 = "./tests/fixtures/files/stix_v2.0_indicator_pattern_error.json"
JSON_FEED_TEST_EMPTY = "./tests/fixtures/files/empty_file.json"

XML_FEED_TEST_VALID = "./tests/fixtures/files/stix_v1.2.xml"
XML_FEED_TEST_FAULTY = "./tests/fixtures/files/stix_v1.2_faulty.xml"


"""Tests for STIX 2.1"""


def test_parser_empty_file(cbcsdk_mock):
    """Test parse empty file."""
    parser = STIX2Parser(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_EMPTY)


def test_parser_faulty_stix_21(monkeypatch, cbcsdk_mock):
    """Test parse faulty v2.1."""
    parser = STIX2Parser(cbcsdk_mock.api)
    monkeypatch.setattr("stix2validator.validator.FileValidationResults.is_valid", lambda: False)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY_21)


def test_parser_valid_file_21(cbcsdk_mock):
    """Test parse valid file v2.1."""
    parser = STIX2Parser(cbcsdk_mock.api)
    objs = parser.parse_file(JSON_FEED_TEST_VALID_21)
    assert len(objs) == 3158
    assert isinstance(objs[0], IOC_V2)


def test_parser_parse_stix_indicator_with_pattern_error_21(cbcsdk_mock):
    """Test parse with error"""
    parser = STIX2Parser(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_21)


"""Tests for STIX 2.0"""


def test_parser_faulty_stix_20(monkeypatch, cbcsdk_mock):
    """Test parse faulty v2.0."""
    parser = STIX2Parser(cbcsdk_mock.api, stix_version="2.0")
    monkeypatch.setattr("stix2validator.validator.FileValidationResults.is_valid", lambda: False)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY_20)


def test_parser_valid_file_20(cbcsdk_mock):
    """Test parse valid file v2.0."""
    parser = STIX2Parser(cbcsdk_mock.api, stix_version="2.0")
    objs = parser.parse_file(JSON_FEED_TEST_VALID_20)
    assert len(objs) == 3158
    assert isinstance(objs[0], IOC_V2)


def test_parser_parse_stix_indicator_with_pattern_error_20(cbcsdk_mock):
    """Test parse with error."""
    parser = STIX2Parser(cbcsdk_mock.api, stix_version="2.0")
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_20)


def test_parser_with_wrong_stix_version(cbcsdk_mock):
    """Test parse wrong stix version."""
    parser = STIX2Parser(cbcsdk_mock, stix_version="1.2")
    with pytest.raises(ValueError):
        parser.parse_file(XML_FEED_TEST_FAULTY)
