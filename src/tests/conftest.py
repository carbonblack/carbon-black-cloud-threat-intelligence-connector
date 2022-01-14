import pytest
from cbc_sdk import CBCloudAPI

from tests.fixtures.cbc_sdk_mock import CBCSDKMock
from tests.fixtures.taxii_mock import TAXIIServerMock


@pytest.fixture(scope="function")
def cbcsdk_mock(monkeypatch):
    cbc_sdk = CBCloudAPI(
        url="https://example.com", org_key="test", token="abcd/1234", ssl_verify=False
    )
    return CBCSDKMock(monkeypatch, cbc_sdk)


@pytest.fixture(scope="function")
def taxii_server_mock():
    return TAXIIServerMock()
