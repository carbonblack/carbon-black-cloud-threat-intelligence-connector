import pytest
from cbc_sdk.enterprise_edr import IOC_V2

from stix_parsers.v21.stix_feed_parser import STIX2Parser

JSON_FEED_TEST_VALID_21 = "./src/tests/fixtures/files/stix_v2.1.json"
JSON_FEED_TEST_FAULTY_21 = "./src/tests/fixtures/files/stix_v2.1_faulty.json"
JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_21 = (
    "./src/tests/fixtures/files/stix_v2.1_indicator_pattern_error.json"
)
JSON_FEED_TEST_VALID_20 = "./src/tests/fixtures/files/stix_v2.0.json"
JSON_FEED_TEST_FAULTY_20 = "./src/tests/fixtures/files/stix_v2.0_faulty.json"
JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_20 = (
    "./src/tests/fixtures/files/stix_v2.0_indicator_pattern_error.json"
)
JSON_FEED_TEST_EMPTY = "./src/tests/fixtures/files/empty_file.json"


def test_parser_empty_file(cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_EMPTY)


def test_parser_faulty_stix_21(monkeypatch, cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    monkeypatch.setattr(
        "stix2validator.validator.FileValidationResults.is_valid", lambda: False
    )
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY_21)


def test_parser_valid_file_21(cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    objs = parser.parse_file(JSON_FEED_TEST_VALID_21)
    assert len(objs) == 3158
    assert isinstance(objs[0], IOC_V2)


def test_parser_parse_stix_indicator_with_pattern_error_21(cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_21)


def test_parser_faulty_stix_20(monkeypatch, cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    monkeypatch.setattr(
        "stix2validator.validator.FileValidationResults.is_valid", lambda: False
    )
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY_20)


def test_parser_valid_file_20(cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    objs = parser.parse_file(JSON_FEED_TEST_VALID_20)
    assert len(objs) == 3158
    assert isinstance(objs[0], IOC_V2)


def test_parser_parse_stix_indicator_with_pattern_error_20(cbcsdk_mock):
    parser = STIX2Parser(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR_20)
