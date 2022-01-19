from datetime import datetime

import pytz
from cabby import create_client
from cabby.entities import Collection

from stix_parsers.stix1_parser import STIX1Parser

COLLECTIONS = [
    Collection("TEST_COLLECTION_1", "TEST_DESC", available=True),
    Collection("TEST_COLLECTION_2", "TEST_DESC", available=True),
]


def test_get_collections(monkeypatch, cbcsdk_mock):
    collections = ["TEST_COLLECTION_1"]

    client = create_client("limo.anomali.com", use_https=True, discovery_path="/api/v1/taxii/taxii-discovery-service/")
    client.set_auth(username="guest", password="guest", verify_ssl=True)

    monkeypatch.setattr("cabby.Client11.get_collections", lambda *args, **kwargs: COLLECTIONS)
    gathered_collections = STIX1Parser(cbcsdk_mock.api)._get_collections(COLLECTIONS, collections)
    assert gathered_collections == ["TEST_COLLECTION_1"]


def test_poll_server(monkeypatch, cbcsdk_mock):
    collections = ["TEST_COLLECTION_1"]

    client = create_client("test.taxiistand.com", use_https=True, discovery_path="/read-write/services/discovery")
    collections = client.get_collections(uri="https://test.taxiistand.com/read-write/services/collection-management")
    # 2016-10-30
    begin_date = datetime(2016, 10, 29, 8, 15, 12, 0, pytz.UTC)
    end_date = datetime(2017, 5, 29, 8, 15, 12, 0, pytz.UTC)

    iocs = STIX1Parser(cbcsdk_mock.api).parse_taxii_server(
        client, [collections[0].name], begin_date=begin_date, end_date=end_date
    )
    breakpoint()
    assert iocs == ["TEST_COLLECTION_1"]
