import copy

from cbc_sdk.enterprise_edr import IOC_V2

from cbc_importer.importer import process_iocs
from tests.fixtures.cbc_sdk_mock_responses import (
    FEED_GET_ALL_RESP_NO_FEED,
    FEED_RESP_POST_STIXS,
    FEEDS_STIX,
    REPORTS_10000_INIT_1000_IOCS,
    REPORTS_GET_10000_WITH_1000_IOCS,
)


def test_process_iocs_couple_of_feeds(cbcsdk_mock):
    """Test process iocs with enough iocs for two feeds"""
    api = cbcsdk_mock.api
    ioc = IOC_V2.create_query(api, "unsigned-chrome", "process_name:chrome.exe")
    ioc_list = [ioc for i in range(2 * 1000 * 10000)]
    counter_f = 0

    def on_get_feed(url, *args, **kwargs):
        return FEED_GET_ALL_RESP_NO_FEED

    def on_post_feed(url, body, **kwargs):
        nonlocal counter_f
        assert body == FEEDS_STIX[counter_f]
        counter_f += 1
        return FEED_RESP_POST_STIXS[counter_f - 1]

    def on_post_report(url, body, **kwargs):
        report_body = copy.deepcopy(body)

        # remove the variable properties
        for i in range(len(report_body["reports"])):
            del report_body["reports"][i]["id"]
            del report_body["reports"][i]["timestamp"]
            title = report_body["reports"][i]["title"]
            assert "Report my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part" in title
            # change the title to match the mock
            report_body["reports"][i]["title"] = "Report my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1-1"
            assert len(report_body["reports"][i]["iocs_v2"]) == 1000

        assert len(report_body["reports"]) == 10000
        assert report_body == REPORTS_10000_INIT_1000_IOCS
        return REPORTS_10000_INIT_1000_IOCS

    def on_get_reports(url, *args, **kwargs):
        return REPORTS_GET_10000_WITH_1000_IOCS

    cbcsdk_mock.mock_request("GET", "/threathunter/feedmgr/v2/orgs/test/feeds", on_get_feed)
    cbcsdk_mock.mock_request("POST", "/threathunter/feedmgr/v2/orgs/test/feeds", on_post_feed)
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports", on_post_report
    )
    cbcsdk_mock.mock_request(
        "POST", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCe/reports", on_post_report
    )
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCg/reports", on_get_reports
    )
    cbcsdk_mock.mock_request(
        "GET", "/threathunter/feedmgr/v2/orgs/test/feeds/90TuDxDYQtiGyg5qhwYCe/reports", on_get_reports
    )
    feeds = process_iocs(
        api,
        ioc_list,
        "my_base_name",
        "2.0",
        "2022-01-27",
        "2022-02-27",
        "limo.domain.com",
        "feed for stix taxii",
        "thiswouldgood",
        5,
    )

    assert len(feeds) == 2
    assert len(feeds[0].reports) == 10000
    assert len(feeds[1].reports) == 10000
    assert len(feeds[0].reports[0]["iocs_v2"]) == 1000
    assert len(feeds[1].reports[0]["iocs_v2"]) == 1000
