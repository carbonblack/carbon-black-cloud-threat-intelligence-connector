import pytest
from cbc_sdk import CBCloudAPI
from stix2 import Bundle, Indicator

from stix_parsers.v21.stix_feed_parser import STIX2Parser
from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.taxii_mock import TAXIIServerMock


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch):
    cbc_sdk = CBCloudAPI(
        url="https://example.com", org_key="test", token="abcd/1234", ssl_verify=False
    )
    return CBCSDKMock(monkeypatch, cbc_sdk)


@pytest.fixture(scope="function")
def taxii_server_mock():
    return TAXIIServerMock()


class STIXFactory:
    @staticmethod
    def create_stix_indicator(**kwargs):
        return Indicator(name="testIndicator", pattern_type="stix", **kwargs)

    @staticmethod
    def create_stix_bundle(*args, **kwargs):
        return Bundle(*args, **kwargs)


def test_parse_feed_get_all_collections(cbcsdk_mock, taxii_server_mock):
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(
        taxii_server_mock.api_roots, "*"
    )
    assert len(collections) == 3


def test_parse_feed_get_specified_collections(cbcsdk_mock, taxii_server_mock):
    gather_data = {
        "Malware Research Group": {
            "collections": [
                "1",
            ]
        },
        "Test Data": {"collections": "*"},
    }
    iocs = STIX2Parser(cbcsdk_mock.api).parse_feed(taxii_server_mock, gather_data)
    assert len(iocs) == 6316


def test_parse_feed_get_one_root_all_collections(cbcsdk_mock, taxii_server_mock):
    gather_data = {"Malware Research Group": {"collections": "*"}}
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(
        taxii_server_mock.api_roots, gather_data
    )
    assert len(collections) == 2


def test_parse_feed_get_one_root_certain_collections(cbcsdk_mock, taxii_server_mock):
    gather_data = {
        "Malware Research Group": {
            "collections": [
                "1",
            ]
        }
    }
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(
        taxii_server_mock.api_roots, gather_data
    )
    assert len(collections) == 1


def test_parse_feed(cbcsdk_mock, taxii_server_mock):
    iocs = STIX2Parser(cbcsdk_mock.api).parse_feed(taxii_server_mock)
    assert len(iocs) == 9474
