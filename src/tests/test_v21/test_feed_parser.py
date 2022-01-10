import pytest
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr import IOC_V2
from stix2 import Bundle, Indicator
from stix2.exceptions import InvalidValueError

from stix_parsers.v21.stix_feed_parser import ParserV21
from tests.fixtures.cbc_sdk_mock import CBCSDKMock

JSON_FEED_TEST_VALID = "./tests/fixtures/files/stix_v2.1.json"
JSON_FEED_TEST_FAULTY = "./tests/fixtures/files/stix_v2.1_faulty.json"
JSON_FEED_TEST_EMPTY = "./tests/fixtures/files/empty_file.json"
JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR = (
    "./tests/fixtures/files/stix_v2.1_indicator_pattern_error.json"
)


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch):
    cbc_sdk = CBCloudAPI(
        url="https://example.com", org_key="test", token="abcd/1234", ssl_verify=False
    )
    return CBCSDKMock(monkeypatch, cbc_sdk)


class STIXFactory:
    @staticmethod
    def create_stix_indicator(**kwargs):
        return Indicator(name="testIndicator", pattern_type="stix", **kwargs)

    @staticmethod
    def create_stix_bundle(*args, **kwargs):
        return Bundle(*args, **kwargs)


def test_parser_faulty_stix(monkeypatch, cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    monkeypatch.setattr(
        "stix2validator.validator.FileValidationResults.is_valid", lambda: False
    )
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_FAULTY)


def test_parser_empty_file(tmp_path, cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_TEST_EMPTY)


def test_parser_valid_file(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    objs = parser.parse_file(JSON_FEED_TEST_VALID)
    assert len(objs) == 3158
    assert isinstance(objs[0], IOC_V2)


def test_parser_parse_stix_indicator_with_pattern_error(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    with pytest.raises(ValueError):
        parser.parse_file(JSON_FEED_OBJECTS_INDICATOR_PATTERN_ERROR)


def test_parser_parse_stix_indicator_InvalidValueError(monkeypatch, cbcsdk_mock):
    def _raise_invalid_value_error(*args, **kwargs):
        raise InvalidValueError

    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[file:hashes.'SHA-256' = 'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    monkeypatch.setattr(
        "stix2patterns.v21.pattern.Pattern.walk",
        lambda *args, **kwargs: _raise_invalid_value_error,
    )
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 0


def test_parser_parse_stix_indicator_returns_empty_list(monkeypatch, cbcsdk_mock):
    def _raise_invalid_value_error(*args, **kwargs):
        raise InvalidValueError

    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[file:hashes.'SHA-256' = 'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    monkeypatch.setattr(
        "stix2patterns.v21.pattern.Pattern.walk",
        lambda *args, **kwargs: _raise_invalid_value_error,
    )
    indicator = parser._parse_stix_indicator(indicator)
    assert indicator == []


def test_parser_parse_stix_indicator_with_file_hash_sha256(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[file:hashes.'SHA-256' = 'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 1
    assert objs[0].field == "process_hash"
    assert objs[0].values == [
        "ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c"
    ]


def test_parser_parse_stix_indicator_with_file_hash_multiple(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = (
        "[file:hashes.'SHA-256' = 'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c' OR "
        "file:hashes.'MD5' = 'd6d9c42d50794f64088f369597b84721']"
    )
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 2
    assert objs[0].field == "process_hash"
    assert objs[1].field == "process_hash"
    assert objs[0].values == [
        "ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c"
    ]
    assert objs[1].values == ["d6d9c42d50794f64088f369597b84721"]


def test_parser_parse_stix_indicator_with_file_hash_multiple_invalid_second(
    cbcsdk_mock,
):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = (
        "[file:hashes.'SHA-256' = 'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c' OR "
        "file:hashes.'TEST' = 'd6d9c42d50794f64088f369597b84721']"
    )
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 1
    assert objs[0].field == "process_hash"
    assert objs[0].values == [
        "ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c"
    ]


def test_parser_parse_stix_indicator_with_url(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[url:value = 'http://test.test/1337/']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 1
    assert objs[0].field == "netconn_domain"
    assert objs[0].values == ["test.test"]


def test_parser_parse_stix_indicator_with_url_multiple(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[url:value = 'http://test.test/1337/' OR url:value = 'http://test1.test/1337/']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 2
    assert objs[0].field == "netconn_domain"
    assert objs[0].values == ["test.test"]
    assert objs[1].field == "netconn_domain"
    assert objs[1].values == ["test1.test"]


def test_parser_parse_stix_indicator_with_ip_cidr(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[ipv4-addr:value = '198.51.100.1/32']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 1
    assert objs[0].field == "netconn_ipv4"
    assert objs[0].values == ["198.51.100.1"]


def test_parser_parse_stix_indicator_with_ip_no_cidr(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = "[ipv4-addr:value = '198.51.100.1']"
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 1
    assert objs[0].field == "netconn_ipv4"
    assert objs[0].values == ["198.51.100.1"]


def test_parser_parse_stix_indicator_with_ip_complex(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = (
        "[ipv4-addr:value = '198.51.100.1/32' OR ipv4-addr:value = '203.0.113.33/32' OR "
        "ipv6-addr:value = '2001:0db8:dead:beef:dead:beef:dead:0001/128']"
    )
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 3
    assert objs[0].field == "netconn_ipv4"
    assert objs[0].values == ["198.51.100.1"]
    assert objs[1].field == "netconn_ipv4"
    assert objs[1].values == ["203.0.113.33"]
    assert objs[2].field == "netconn_ipv6"
    assert objs[2].values == ["2001:0db8:dead:beef:dead:beef:dead:0001"]


def test_parser_parse_stix_indicator_with_ip_domain(cbcsdk_mock):
    parser = ParserV21(cbcsdk_mock.api)
    pattern = (
        "[ipv4-addr:value = '198.51.100.1/32' OR ipv4-addr:value = '203.0.113.33/32' OR "
        "ipv6-addr:value = '2001:0db8:dead:beef:dead:beef:dead:0001/128' OR domain-name:value = "
        "'example.com']"
    )
    indicator = STIXFactory.create_stix_indicator(pattern=pattern)
    bundle = STIXFactory.create_stix_bundle(indicator)
    objs = parser._parse_stix_objects(bundle)
    assert len(objs) == 4
    assert objs[0].field == "netconn_ipv4"
    assert objs[0].values == ["198.51.100.1"]
    assert objs[1].field == "netconn_ipv4"
    assert objs[1].values == ["203.0.113.33"]
    assert objs[2].field == "netconn_ipv6"
    assert objs[2].values == ["2001:0db8:dead:beef:dead:beef:dead:0001"]
    assert objs[3].field == "netconn_domain"
    assert objs[3].values == ["example.com"]
