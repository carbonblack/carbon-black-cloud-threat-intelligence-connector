import pytest

from stix_parsers.v21.stix_feed_parser import ParserV21
from cbc_sdk import CBCloudAPI

JSON_FEED_TEST_VALID = "./tests/fixtures/stix_v2.1.json"
JSON_FEED_TEST_FAULTY = "./tests/fixtures/stix_v2.1_faulty.json"
JSON_FEED_TEST_EMPTY = "./tests/fixtures/empty_file.json"
COLLECTION_URL = "http://test.test/"

def test_parser_faulty_stix(monkeypatch):
    cbcapi = CBCloudAPI(profile="default")
    parser = ParserV21(cbcapi)
    monkeypatch.setattr("stix2validator.validator.FileValidationResults.is_valid", lambda: False)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY)


def test_parser_empty_file(tmp_path):
    cbcapi = CBCloudAPI(profile="default")
    parser = ParserV21(cbcapi)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_EMPTY)


def test_parser_valid_file():
    cbcapi = CBCloudAPI(profile="default")
    parser = ParserV21(cbcapi)
    parser.parse_file(JSON_FEED_TEST_VALID)