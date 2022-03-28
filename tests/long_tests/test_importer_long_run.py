import copy

from cbc_sdk.enterprise_edr import IOC_V2, Feed

from cbc_importer.importer import process_iocs
from tests.fixtures.cbc_sdk_mock_responses import (
    REPORTS_10000_INIT_1000_IOCS,
    FEED_GET_RESP,
)


def test_creating_of_more_feeds(cbcsdk_mock):
    """Test process iocs with enough iocs for more than one feed - should not create second one."""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")
    ioc_list = [ioc for i in range(1000 * 10000 + 1)]

    cbcsdk_mock.mock_request(
        "GET",
        "/threathunter/feedmgr/v2/orgs/test/feeds/feedid",
        FEED_GET_RESP,
    )

    def on_post_report(url, body, **kwargs):
        report_body = copy.deepcopy(body)

        # remove the variable properties
        for i in range(len(report_body["reports"])):
            del report_body["reports"][i]["id"]
            del report_body["reports"][i]["timestamp"]
            if report_body["reports"][i].get("iocs_total_count"):
                del report_body["reports"][i]["iocs_total_count"]
            title = report_body["reports"][i]["title"]
            assert "Report My STIX Feed" in title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report My STIX Feed-1"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000

        assert len(report_body["reports"]) == 10000
        assert report_body == REPORTS_10000_INIT_1000_IOCS
        return REPORTS_10000_INIT_1000_IOCS

    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/feedid/reports", on_post_report
    )
    feed = process_iocs(api, ioc_list, 5, "feedid", True)
    assert isinstance(feed, Feed)
