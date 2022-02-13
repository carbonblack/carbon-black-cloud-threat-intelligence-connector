import uuid
from unittest import mock

from cbc_importer.stix_parsers.v1.parser import STIX1Parser

STIX_FILE_HASHES = "./tests/fixtures/files/stix_1x_sample_objects/file_hashes.xml"
STIX_HAT_DNS = "./tests/fixtures/files/stix_1x_sample_objects/hat_dns_example.xml"
STIX_SIMPLE_DNS_WATCHLIST = "./tests/fixtures/files/stix_1x_sample_objects/simple_dns_watchlist.xml"
STIX_SIMPLE_IP_WATCHLIST = "./tests/fixtures/files/stix_1x_sample_objects/simple_ip_watchlist.xml"
STIX_SIMPLE_IPV4 = "./tests/fixtures/files/stix_1x_sample_objects/simple_ipv4.xml"
STIX_SIMPLE_IPV6_WATCHLIST = "./tests/fixtures/files/stix_1x_sample_objects/simple_ipv6_watchlist.xml"
STIX_INDICATOR_URI = "./tests/fixtures/files/stix_1x_sample_objects/indicator_for_malicious_url.xml"


def test_parsing_hashes(cbcsdk_mock):
    """Test parsing hashes."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_FILE_HASHES)
    assert len(iocs) == 1
    assert iocs[0].match_type == "query"
    assert iocs[0].values == [
        "process_hash:ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c OR process_hash:0d2a3f99885def98abb093a4768bce0c"
    ]


def test_parsing_observable_single_domain(cbcsdk_mock):
    """Test parsing single domain."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_HAT_DNS)
    assert iocs[0].values[0] == "fctnnbsc38w-47-54-126-15.dhcp-dynamic.fibreop.nb.bellaliant.net"
    assert iocs[0].field == "netconn_domain"
    assert len(iocs) == 1


def test_parsing_observable_raises_key_error(cbcsdk_mock):
    """Test parsing observable to raise KeyError"""
    parser = STIX1Parser(cbcsdk_mock.api)
    parser.CB_MAPPINGS = {}
    iocs = parser.parse_file(STIX_HAT_DNS)
    assert len(iocs) == 0


def test_parsing_observable_raises_attribute_error(monkeypatch, cbcsdk_mock):
    """Test parsing observable to raise AttributeError"""
    parser = STIX1Parser(cbcsdk_mock.api)

    class ObservableMock:

        object_ = "test"

    class STIXPackageMock:

        observables = [ObservableMock()]
        indicators = []

    monkeypatch.setattr("stix.core.STIXPackage.from_xml", lambda *args, **kwargs: STIXPackageMock())

    iocs = parser.parse_file(STIX_HAT_DNS)

    assert len(iocs) == 0


def test_parsing_indicator_multiple_domains(cbcsdk_mock):
    """Test parse multiple domains."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_SIMPLE_DNS_WATCHLIST)
    assert len(iocs) == 2
    assert iocs[0].field == "netconn_domain"
    assert len(iocs[0].values) == 3


def test_parsing_indicator_raises_key_error(cbcsdk_mock):
    """Test parsing indicator to raise KeyError"""
    parser = STIX1Parser(cbcsdk_mock.api)
    parser.CB_MAPPINGS = {}
    iocs = parser.parse_file(STIX_SIMPLE_DNS_WATCHLIST)
    assert len(iocs) == 0


def test_parsing_ips(cbcsdk_mock):
    """Test parse ip."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_SIMPLE_IP_WATCHLIST)
    assert len(iocs) == 1
    assert iocs[0].field == "netconn_ipv4"
    assert len(iocs[0].values) == 3


def test_parsing_ipv4_multiple_values(cbcsdk_mock):
    """Test parse IPV4."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_SIMPLE_IP_WATCHLIST)
    assert len(iocs) == 1
    assert iocs[0].field == "netconn_ipv4"
    assert len(iocs[0].values) == 3


def test_parsing_ipv4(cbcsdk_mock):
    """Test parsing IPv4"""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_SIMPLE_IPV4)
    assert len(iocs) == 1
    assert iocs[0].field == "netconn_ipv4"
    assert iocs[0].values == ["54.153.123.93"]


def test_parsing_ipv6(cbcsdk_mock):
    """Test parsing IPv6."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_SIMPLE_IPV6_WATCHLIST)
    assert len(iocs) == 2
    assert iocs[0].field == "netconn_ipv6"
    assert len(iocs[0].values) == 3
    assert iocs[0].values == [
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7335",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7336",
    ]


def test_parsing_uri(cbcsdk_mock):
    """Test parsing URL."""
    parser = STIX1Parser(cbcsdk_mock.api)
    iocs = parser.parse_file(STIX_INDICATOR_URI)
    assert len(iocs) == 1
    assert iocs[0].field == "netconn_domain"
    assert iocs[0].values == ["http://x4z9arb.cn/4712"]
