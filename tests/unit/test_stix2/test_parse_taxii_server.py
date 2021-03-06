from cbc_importer.stix_parsers.v2.parser import STIX2Parser


def test_parse_feed_get_all_collections(cbcsdk_mock, taxii2_server_mock):
    """Test parse feed get all collections."""
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(taxii2_server_mock.api_roots, "*")
    assert len(collections) == 4


def test_parse_feed_get_specified_collections(cbcsdk_mock, taxii2_server_mock):
    """Test parse feed get specific collection."""
    gather_data = [
        {
            "title": "Malware Research Group",
            "collections": [
                "1",
            ],
        }
    ]
    iocs = STIX2Parser(cbcsdk_mock.api).parse_taxii_server(taxii2_server_mock, gather_data)
    assert len(iocs) == 4


def test_parse_feed_get_one_root_all_collections(cbcsdk_mock, taxii2_server_mock):
    """Test parse feed get one root all collections."""
    gather_data = [{"title": "Malware Research Group", "collections": "*"}]
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(taxii2_server_mock.api_roots, gather_data)
    assert len(collections) == 2


def test_parse_feed_get_one_root_certain_collections(cbcsdk_mock, taxii2_server_mock):
    """Test parse feed get one root specific collection."""
    gather_data = [{"title": "Malware Research Group", "collections": ["1"]}]
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(taxii2_server_mock.api_roots, gather_data)
    assert len(collections) == 1


def test_parse_feed(cbcsdk_mock, taxii2_server_mock):
    """Test parse feed."""
    iocs = STIX2Parser(cbcsdk_mock.api).parse_taxii_server(taxii2_server_mock)
    assert len(iocs) == 16
