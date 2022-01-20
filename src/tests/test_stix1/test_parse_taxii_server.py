from datetime import datetime

import pytz
from cabby import create_client
from cabby.entities import Collection

from stix_parsers.v1.parser import STIX1Parser

COLLECTIONS = [
    Collection("TEST_COLLECTION_1", "TEST_DESC", available=True),
    Collection("TEST_COLLECTION_2", "TEST_DESC", available=True),
]


# def test_get_collections(monkeypatch, cbcsdk_mock):
#     collections = ["TEST_COLLECTION_1"]

#     client = create_client("limo.anomali.com", use_https=True, discovery_path="/api/v1/taxii/taxii-discovery-service/")
#     client.set_auth(username="guest", password="guest", verify_ssl=True)

#     monkeypatch.setattr("cabby.Client11.get_collections", lambda *args, **kwargs: COLLECTIONS)
#     gathered_collections = STIX1Parser(cbcsdk_mock.api)._get_collections(COLLECTIONS, collections)
#     assert gathered_collections == ["TEST_COLLECTION_1"]


# def test_poll_server(monkeypatch, cbcsdk_mock):
#     collections = ["TEST_COLLECTION_1"]

#     client = create_client("limo.anomali.com", use_https=True, discovery_path="/api/v1/taxii/taxii-discovery-service/")
#     client.set_auth(username="guest", password="guest")
#     collections = client.get_collections("https://limo.anomali.com/api/v1/taxii/collection_management/")

#     iocs = STIX1Parser(cbcsdk_mock.api).parse_taxii_server(
#         client, "*"
#     )
#     breakpoint()
#     assert iocs == ["TEST_COLLECTION_1"]
