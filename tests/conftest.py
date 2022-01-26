import pytest
from cbc_sdk import CBCloudAPI

from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.taxii1_mock import TAXII1ServerMock
from tests.fixtures.taxii2_mock import TAXII2ServerMock


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch):
    cbc_sdk = CBCloudAPI(url="https://example.com", org_key="test", token="abcd/1234", ssl_verify=False)
    return CBCSDKMock(monkeypatch, cbc_sdk)


@pytest.fixture(scope="function")
def taxii2_server_mock():
    return TAXII2ServerMock()


@pytest.fixture(scope="function")
def taxii1_server_mock():
    return TAXII1ServerMock()
