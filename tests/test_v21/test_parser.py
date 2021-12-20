import pytest

from stix_parsers.v21.parser import ParserV21

JSON_FEED_TEST_VALID = "./tests/fixtures/stix_v2.1.json"
JSON_FEED_TEST_FAULTY = "./tests/fixtures/stix_v2.1_faulty.json"
JSON_FEED_TEST_EMPTY = "./tests/fixtures/empty_file.json"


def test_parser_faulty_stix(monkeypatch):
    parser = ParserV21()
    monkeypatch.setattr("stix2validator.validator.FileValidationResults.is_valid", lambda: False)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY)


def test_parser_empty_file(tmp_path):
    parser = ParserV21()
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_EMPTY)


def test_parser_valid_file():
    parser = ParserV21()
    parser.parse_file(JSON_FEED_TEST_VALID)