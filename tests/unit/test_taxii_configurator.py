import arrow
import pytest
from cabby import Client10, Client11
from taxii2client.v20 import Server as Client20
from taxii2client.v21 import Server as Client21

from cbc_importer.taxii_configurator import TAXIIConfigurator

DEFAULT_TAXII_CONFIG_v2 = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "Test",
            "version": 2.1,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "Test",
                "severity": 5,
                "summary": "empty summary",
                "category": "STIX",
                "feed_id": None,
            },
            "connection": {"url": "test.test"},
            "proxies": None,
            "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
            "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
        },
    ],
}

DEFAULT_TAXII_CONFIG_v1 = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "Test",
            "version": 1.1,
            "enabled": False,
            "cbc_feed_options": {
                "feed_base_name": "TestSTIX",
                "severity": 5,
                "summary": "empty summary",
                "category": "STIX",
                "feed_id": None,
            },
            "proxies": None,
            "connection": {
                "host": "test.test.com",
                "discovery_path": "/taxii/discovery",
                "port": None,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "test",
                "password": "test",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": "2022-01-01 00:00:00",
                "end_date": "2022-02-01 00:00:00",
                "collection_management_uri": "/test/",
                "collections": "*",
            },
        },
    ],
}


def test_get_client_10():
    """Test for selecting the client"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 1.0,
                "enabled": False,
                "cbc_feed_options": {
                    "feed_base_name": "TestSTIX",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "proxies": None,
                "connection": {
                    "host": "test.test.com",
                    "discovery_path": "/taxii/discovery",
                    "port": None,
                    "use_https": True,
                    "headers": None,
                    "timeout": None,
                },
                "auth": {
                    "username": "test",
                    "password": "test",
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "key_password": None,
                    "jwt_auth_url": None,
                    "verify_ssl": True,
                },
                "options": {
                    "begin_date": "2022-01-01 00:00:00",
                    "end_date": "2022-02-01 00:00:00",
                    "collection_management_uri": "/test/",
                    "collections": "*",
                },
            },
        ],
    }
    configurator = TAXIIConfigurator(configuration["servers"][0])
    assert isinstance(configurator.client, Client10)


def test_get_client_11():
    """Test for selecting the client"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 1.1,
                "enabled": False,
                "cbc_feed_options": {
                    "feed_base_name": "TestSTIX",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "proxies": None,
                "connection": {
                    "host": "test.test.com",
                    "discovery_path": "/taxii/discovery",
                    "port": None,
                    "use_https": True,
                    "headers": None,
                    "timeout": None,
                },
                "auth": {
                    "username": "test",
                    "password": "test",
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "key_password": None,
                    "jwt_auth_url": None,
                    "verify_ssl": True,
                },
                "options": {
                    "begin_date": "2022-01-01 00:00:00",
                    "end_date": "2022-02-01 00:00:00",
                    "collection_management_uri": "/test/",
                    "collections": "*",
                },
            },
        ],
    }
    configurator = TAXIIConfigurator(configuration["servers"][0])
    assert isinstance(configurator.client, Client11)


def test_get_client_20():
    """Test for selecting the client"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.0,
                "enabled": True,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    configurator = TAXIIConfigurator(configuration["servers"][0])
    assert isinstance(configurator.client, Client20)


def test_get_client_21():
    """Test for selecting the client"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.1,
                "enabled": True,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    configurator = TAXIIConfigurator(configuration["servers"][0])
    assert isinstance(configurator.client, Client21)


def test_get_client_raises_value_error():
    """Test for selecting the client"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.2,
                "enabled": True,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": "2022-01-01 00:00:00", "roots": "*"},
            },
        ],
    }
    with pytest.raises(ValueError):
        TAXIIConfigurator(configuration["servers"][0])


def test_get_search_options_1x():
    """Test for setting the search options"""
    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v1["servers"][0])
    begin_date = arrow.get("2022-01-01 00:00:00", tzinfo="UTC")
    end_date = arrow.get("2022-02-01 00:00:00", tzinfo="UTC")

    assert configurator.search_options["collection_management_uri"] == "/test/"
    assert configurator.search_options["begin_date"] == begin_date
    assert configurator.search_options["end_date"] == end_date
    assert configurator.search_options["collections"] == "*"


def test_get_search_options_2x():
    """Test for setting the search options"""
    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v2["servers"][0])
    added_after = arrow.get("2022-01-01 00:00:00", tzinfo="UTC")

    assert configurator.search_options["gather_data"] == "*"
    assert configurator.search_options["added_after"] == added_after


def test_set_cbc_feed_options_1x():
    """Test for setting the feed options"""
    start_date = arrow.get("2022-01-01 00:00:00", tzinfo="UTC").format("YYYY-MM-DD HH:mm:ss ZZ")
    end_date = arrow.get("2022-02-01 00:00:00", tzinfo="UTC").format("YYYY-MM-DD HH:mm:ss ZZ")

    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v1["servers"][0])

    assert configurator.cbc_feed_options == DEFAULT_TAXII_CONFIG_v1["servers"][0]["cbc_feed_options"]
    assert configurator.cbc_feed_options["start_date"] == start_date
    assert configurator.cbc_feed_options["end_date"] == end_date
    assert configurator.cbc_feed_options["provider_url"] == "test.test.com"


def test_set_cbc_feed_options_2x():
    """Test for setting the feed options"""
    start_date = arrow.get("2022-01-01 00:00:00", tzinfo="UTC").format("YYYY-MM-DD HH:mm:ss ZZ")
    end_date = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss ZZ")

    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v2["servers"][0])

    assert configurator.cbc_feed_options == DEFAULT_TAXII_CONFIG_v2["servers"][0]["cbc_feed_options"]
    assert configurator.cbc_feed_options["start_date"] == start_date
    assert configurator.cbc_feed_options["end_date"] == end_date
    assert configurator.cbc_feed_options["provider_url"] == "test.test"


def test_set_default_time_range_taxii1_custom():
    """Test for getting the default time range"""
    begin_date = arrow.get("2022-01-01 00:00:00", tzinfo="UTC").datetime
    end_date = arrow.get("2022-02-01 00:00:00", tzinfo="UTC").datetime

    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v1["servers"][0])

    assert isinstance(configurator.dates[0], arrow.Arrow)
    assert isinstance(configurator.dates[1], arrow.Arrow)
    assert configurator.dates[0].tzname() == "UTC"
    assert configurator.dates[1].tzname() == "UTC"
    assert configurator.dates[0] == begin_date
    assert configurator.dates[1] == end_date


def test_set_default_time_range_taxii1_defaults():
    """Test for getting the default time range"""
    begin_date = arrow.utcnow().shift(months=-1)
    end_date = arrow.utcnow()
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 1.1,
                "enabled": False,
                "cbc_feed_options": {
                    "feed_base_name": "TestSTIX",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "proxies": None,
                "connection": {
                    "host": "test.test.com",
                    "discovery_path": "/taxii/discovery",
                    "port": None,
                    "use_https": True,
                    "headers": None,
                    "timeout": None,
                },
                "auth": {
                    "username": "test",
                    "password": "test",
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "key_password": None,
                    "jwt_auth_url": None,
                    "verify_ssl": True,
                },
                "options": {
                    "begin_date": None,
                    "end_date": None,
                    "collection_management_uri": "/test/",
                    "collections": "*",
                },
            },
        ],
    }
    configurator = TAXIIConfigurator(configuration["servers"][0])

    assert isinstance(configurator.dates[0], arrow.Arrow)
    assert isinstance(configurator.dates[1], arrow.Arrow)
    assert configurator.dates[0].tzname() == "UTC"
    assert configurator.dates[1].tzname() == "UTC"
    assert configurator.dates[0].replace(microsecond=0) == begin_date.replace(microsecond=0)
    assert configurator.dates[1].replace(microsecond=0) == end_date.replace(microsecond=0)


def test_set_default_time_range_taxii2_custom():
    """Test for getting the default time range"""
    added_after = arrow.get("2022-01-01 00:00:00", tzinfo="UTC").datetime

    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v2["servers"][0])

    assert isinstance(configurator.dates, arrow.Arrow)
    assert configurator.dates.tzname() == "UTC"
    assert configurator.dates == added_after


def test_set_default_time_range_taxii2_default():
    """Tests for getting the default `added_after`"""
    configuration = {
        "cbc_auth_profile": "default",
        "servers": [
            {
                "name": "Test",
                "version": 2.1,
                "enabled": True,
                "cbc_feed_options": {
                    "feed_base_name": "Test",
                    "severity": 5,
                    "summary": "empty summary",
                    "category": "STIX",
                    "feed_id": None,
                },
                "connection": {"url": "test.test"},
                "proxies": None,
                "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
                "options": {"added_after": None, "roots": "*"},
            },
        ],
    }
    added_after = arrow.utcnow().shift(months=-1)
    configurator = TAXIIConfigurator(configuration["servers"][0])

    assert isinstance(configurator.dates, arrow.Arrow)
    assert configurator.dates.tzname() == "UTC"
    assert configurator.dates.replace(microsecond=0) == added_after.replace(microsecond=0)


def test_authenticate_client_taxii1():
    """Tests for authenticating"""
    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v1["servers"][0])

    assert configurator.client.username == "test"
    assert configurator.client.password == "test"
    assert configurator.client.cert_file is None
    assert configurator.client.key_password is None
    assert configurator.client.jwt_url is None
    assert configurator.client.verify_ssl


def test_authenticate_client_taxii2():
    """Tests for authenticating"""
    configurator = TAXIIConfigurator(DEFAULT_TAXII_CONFIG_v2["servers"][0])

    assert configurator.client._user == "guest"
    assert configurator.client._password == "guest"
    assert configurator.client._verify
    assert configurator.client._cert is None
