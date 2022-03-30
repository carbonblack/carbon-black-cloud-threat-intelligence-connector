import arrow
import pytest
from cabby import Client10, Client11
from taxii2client.v20 import Server as Client20
from taxii2client.v21 import Server as Client21

from cbc_importer.taxii_configurator import TAXIIConfigurator


def test_get_client_10(example_configuration):
    """Test for selecting the client"""
    example_configuration["servers"][0]["version"] = 1.0
    configurator = TAXIIConfigurator(example_configuration["servers"][0])
    assert isinstance(configurator.client, Client10)


def test_get_client_11(example_configuration):
    """Test for selecting the client"""
    example_configuration["servers"][0]["version"] = 1.1
    configurator = TAXIIConfigurator(example_configuration["servers"][0])
    assert isinstance(configurator.client, Client11)


def test_get_client_12(example_configuration):
    """Test for selecting the client"""
    example_configuration["servers"][0]["version"] = 1.2
    configurator = TAXIIConfigurator(example_configuration["servers"][0])
    # The client for 1.2 is actually the 1.1
    assert isinstance(configurator.client, Client11)


def test_get_client_20(example_configuration):
    """Test for selecting the client"""
    example_configuration["servers"][1]["version"] = 2.0
    configurator = TAXIIConfigurator(example_configuration["servers"][1])
    assert isinstance(configurator.client, Client20)


def test_get_client_21(example_configuration):
    """Test for selecting the client"""
    example_configuration["servers"][1]["version"] = 2.1
    configurator = TAXIIConfigurator(example_configuration["servers"][1])
    assert isinstance(configurator.client, Client21)


def test_get_client_raises_value_error(example_configuration):
    """Test for selecting the client"""
    example_configuration["servers"][1]["version"] = 2.2
    with pytest.raises(ValueError):
        TAXIIConfigurator(example_configuration["servers"][1])


def test_get_search_options_1x(example_configuration):
    """Test for setting the search options"""
    example_configuration["servers"][0]["options"]["collection_management_uri"] = "/test/"
    example_configuration["servers"][0]["options"]["begin_date"] = "2022-01-01 00:00:00"
    example_configuration["servers"][0]["options"]["end_date"] = "2022-02-01 00:00:00"
    configurator = TAXIIConfigurator(example_configuration["servers"][0])
    begin_date = arrow.get("2022-01-01 00:00:00", tzinfo="UTC")
    end_date = arrow.get("2022-02-01 00:00:00", tzinfo="UTC")

    assert configurator.search_options["collection_management_uri"] == "/test/"
    assert configurator.search_options["begin_date"] == begin_date
    assert configurator.search_options["end_date"] == end_date
    assert configurator.search_options["collections"] == ["collection-a", "collection-b"]


def test_get_search_options_2x(example_configuration):
    """Test for setting the search options"""
    configurator = TAXIIConfigurator(example_configuration["servers"][1])
    added_after = arrow.get("2022-01-01 00:00:00", tzinfo="UTC")

    assert configurator.search_options["gather_data"] == [
        {"collections": ["collection-a", "collection-b"], "title": "Test Root Title"},
        {"collections": ["collection-c", "collection-d"], "title": "Test Root Title 2"},
    ]
    assert configurator.search_options["added_after"] == added_after


def test_set_default_time_range_taxii1_custom(example_configuration):
    """Test for getting the default time range"""
    example_configuration["servers"][0]["options"]["begin_date"] = "2022-01-01 00:00:00"
    example_configuration["servers"][0]["options"]["end_date"] = "2022-02-01 00:00:00"
    begin_date = arrow.get("2022-01-01 00:00:00", tzinfo="UTC").datetime
    end_date = arrow.get("2022-02-01 00:00:00", tzinfo="UTC").datetime

    configurator = TAXIIConfigurator(example_configuration["servers"][0])

    assert isinstance(configurator.dates[0], arrow.Arrow)
    assert isinstance(configurator.dates[1], arrow.Arrow)
    assert configurator.dates[0].tzname() == "UTC"
    assert configurator.dates[1].tzname() == "UTC"
    assert configurator.dates[0] == begin_date
    assert configurator.dates[1] == end_date


def test_set_default_time_range_taxii1_defaults(example_configuration):
    """Test for getting the default time range"""
    begin_date = arrow.utcnow().shift(months=-1)
    end_date = arrow.utcnow()
    example_configuration["servers"][0]["options"]["begin_date"] = None
    example_configuration["servers"][0]["options"]["end_date"] = None
    configurator = TAXIIConfigurator(example_configuration["servers"][0])

    assert isinstance(configurator.dates[0], arrow.Arrow)
    assert isinstance(configurator.dates[1], arrow.Arrow)
    assert configurator.dates[0].tzname() == "UTC"
    assert configurator.dates[1].tzname() == "UTC"
    assert configurator.dates[0].replace(microsecond=0) == begin_date.replace(microsecond=0)
    assert configurator.dates[1].replace(microsecond=0) == end_date.replace(microsecond=0)


def test_set_default_time_range_taxii2_custom(example_configuration):
    """Test for getting the default time range"""
    added_after = arrow.get("2022-01-01 00:00:00", tzinfo="UTC").datetime

    configurator = TAXIIConfigurator(example_configuration["servers"][1])

    assert isinstance(configurator.dates, arrow.Arrow)
    assert configurator.dates.tzname() == "UTC"
    assert configurator.dates == added_after


def test_set_default_time_range_taxii2_default(example_configuration):
    """Tests for getting the default `added_after`"""
    example_configuration["servers"][1]["options"]["added_after"] = None
    added_after = arrow.utcnow().shift(months=-1)
    configurator = TAXIIConfigurator(example_configuration["servers"][1])

    assert isinstance(configurator.dates, arrow.Arrow)
    assert configurator.dates.tzname() == "UTC"
    assert configurator.dates.replace(microsecond=0) == added_after.replace(microsecond=0)


def test_authenticate_client_taxii1(example_configuration):
    """Tests for authenticating"""
    configurator = TAXIIConfigurator(example_configuration["servers"][0])
    assert configurator.client.username == "test"
    assert configurator.client.password == "test"
    assert configurator.client.cert_file is None
    assert configurator.client.key_password is None
    assert configurator.client.jwt_url is None
    assert configurator.client.verify_ssl


def test_authenticate_client_taxii2(example_configuration):
    """Tests for authenticating"""
    configurator = TAXIIConfigurator(example_configuration["servers"][1])
    assert configurator.client._user == "guest"
    assert configurator.client._password == "guest"
    assert configurator.client._verify
    assert configurator.client._cert is None
