import pytest
from lxml.etree import XMLSyntaxError

from cbc_importer.stix_parsers.v1.parser import STIX1Parser


def test_get_collections(cbcsdk_mock, taxii1_server_mock):
    """Test get collections."""
    collections = ["COLLECTION_1"]

    gathered_collections = STIX1Parser(cbcsdk_mock.api)._get_collections(
        taxii1_server_mock.get_collections(), collections
    )
    assert gathered_collections == ["COLLECTION_1"]


def test_poll_server_one_collection(taxii1_server_mock, cbcsdk_mock):
    """Test poll one collection."""
    collections = ["COLLECTION_1"]

    iocs = STIX1Parser(cbcsdk_mock.api).parse_taxii_server(
        taxii1_server_mock,
        collections,
    )

    assert len(iocs) == 3158


def test_parse_server_raises_xml_syntax_error(caplog, monkeypatch, taxii1_server_mock, cbcsdk_mock):
    """Test parsing raising `XMLSyntaxError`"""
    collections = ["COLLECTION_1"]

    def raise_xml_parsing_error(*args, **kwargs):
        raise XMLSyntaxError()

    monkeypatch.setattr("stix.core.STIXPackage.from_xml", raise_xml_parsing_error)
    STIX1Parser(cbcsdk_mock.api).parse_taxii_server(
        taxii1_server_mock,
        collections,
    )
    assert "XMLSyntaxError" in caplog.text


def test_parse_server_general_exception(caplog, monkeypatch, taxii1_server_mock, cbcsdk_mock):
    """Test parsing raising general Exception"""
    collections = ["COLLECTION_1"]

    def raise_exception(*args, **kwargs):
        raise Exception("Test Exception")

    monkeypatch.setattr("stix.core.STIXPackage.from_xml", raise_exception)
    STIX1Parser(cbcsdk_mock.api).parse_taxii_server(
        taxii1_server_mock,
        collections,
    )
    assert "Test Exception" in caplog.text
