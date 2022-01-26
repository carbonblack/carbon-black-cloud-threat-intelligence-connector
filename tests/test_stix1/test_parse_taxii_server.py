from cbc_importer.stix_parsers.v1.parser import STIX1Parser


def test_get_collections(cbcsdk_mock, taxii1_server_mock):
    collections = ["COLLECTION_1"]

    gathered_collections = STIX1Parser(cbcsdk_mock.api)._get_collections(
        taxii1_server_mock.get_collections(), collections
    )
    assert gathered_collections == ["COLLECTION_1"]


def test_poll_server_one_collection(taxii1_server_mock, cbcsdk_mock):
    collections = ["COLLECTION_1"]

    iocs = STIX1Parser(cbcsdk_mock.api).parse_taxii_server(
        taxii1_server_mock,
        collections,
    )

    assert len(iocs) == 3158
