from stix_parsers.stix2_parser import STIX2Parser


def test_parse_feed_get_all_collections(cbcsdk_mock, taxii_server_mock):
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(taxii_server_mock.api_roots, "*")
    assert len(collections) == 4


def test_parse_feed_get_specified_collections(cbcsdk_mock, taxii_server_mock):
    gather_data = {
        "Malware Research Group": {
            "collections": [
                "1",
            ]
        },
        "Test Data": {"collections": "*"},
    }
    iocs = STIX2Parser(cbcsdk_mock.api).parse_taxii_server(taxii_server_mock, gather_data)
    assert len(iocs) == 6316


def test_parse_feed_get_one_root_all_collections(cbcsdk_mock, taxii_server_mock):
    gather_data = {"Malware Research Group": {"collections": "*"}}
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(taxii_server_mock.api_roots, gather_data)
    assert len(collections) == 2


def test_parse_feed_get_one_root_certain_collections(cbcsdk_mock, taxii_server_mock):
    gather_data = {
        "Malware Research Group": {
            "collections": [
                "1",
            ]
        }
    }
    collections = STIX2Parser(cbcsdk_mock.api)._gather_collections(taxii_server_mock.api_roots, gather_data)
    assert len(collections) == 1


def test_parse_feed(cbcsdk_mock, taxii_server_mock):
    iocs = STIX2Parser(cbcsdk_mock.api).parse_taxii_server(taxii_server_mock)
    assert len(iocs) == 12632
