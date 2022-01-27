# -*- coding: utf-8 -*-

# *******************************************************
# Copyright (c) VMware, Inc. 2022. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# *******************************************************
# *
# * DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# * WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# * EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# * WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

"""Helpers to import everything in CBC"""
from typing import List
import uuid
from cbc_sdk import CBCloudAPI
from cbc_sdk.errors import ObjectNotFoundError
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2, Report, Feed
from cbc_importer.utils import get_feed, create_feed, create_watchlist


# Constants for the batch sizes of reports and iocs
IOCS_BATCH_SIZE = 5
REPORTS_BATCH_SIZE = 10000


def process_iocs(
    cb: CBCloudAPI,
    iocs: List[IOC_V2],
    feed_name: str,
    stix_version: str,
    start_date: str,
    end_date: str,
    provider_url: str,
    summary: str,
    category: str,
    severity: int,
) -> List[Feed]:
    """Create reports and add the iocs to the reports.

    If the iocs are >= IOCS_BATCH_SIZE, then create multiple reports.
    If the number of reports are >= REPORTS_BATCH_SIZE, then create multiple feeds.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        iocs (list): list of iocs
        feed_name (str): The base name of the feeds
        stix_version (str): the stix version
        start_date (str): the start date
        end_date (str): the end date
        provider_url (str): Provider URL for the new feed.
        summary (str): Summary for the new feed.
        category (str): Category for the new feed.
        severity (int): (optional) severity for the reports
    Returns:
        list(Feed): list of feeds created as part of the import
    """
    num_iocs = len(iocs)
    num_reports = num_iocs // IOCS_BATCH_SIZE + 1
    num_feeds = num_reports // REPORTS_BATCH_SIZE + 1
    counter_f = counter_r = 1
    feeds = []

    # include http if there is no such - provider_url should be valid url
    if not provider_url.startswith("http"):
        provider_url = f"http://{provider_url}"

    while counter_f <= num_feeds:
        start, end = 0, IOCS_BATCH_SIZE
        reports = []
        feed_name = f"{feed_name} ({stix_version}) {start_date} to {end_date} - Part {counter_f}"

        try:
            feed = get_feed(cb, feed_name=feed_name)
        except ObjectNotFoundError:
            feed = create_feed(cb, name=feed_name, provider_url=provider_url, summary=summary, category=category)

        while counter_r <= num_reports:
            iocs_list = iocs[start:end]
            counter_r += 1

            # check for the edge case where we have iocs divisible by IOCS_BATCH_SIZE
            # in that case there will be one-off error
            if iocs_list:
                builder = Report.create(cb, f"Report {feed.name}-{counter_r - 1}", feed.summary, severity)

                # use the builder so that the data is properly formed
                report = builder.build()
                report.append_iocs(iocs_list)
                start, end = end, end + IOCS_BATCH_SIZE
                report_data = report._info

                # add id for the report, because the builder is not include it
                report_data["id"] = str(uuid.uuid4())

                # finally, add the report to the list to be added in the current feed
                reports.append(Report(cb, initial_data=report_data, feed_id=feed.id))
        
        # add reports to the current feed
        feed.replace_reports(reports)
        # add the created feed
        feeds.append(feed)
        print('here', feed._info)
        # update the counter of the feed
        counter_f += 1

    return feeds


def subscribe_to_feed(
    cb: CBCloudAPI, feed_base_name: str = None, feed_name: str = None, with_alerts: bool = False
) -> None:
    """Add the reports to the existing feed

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        feed_base_name (str): base name of the feed
        feed_name (str): feed name to be create watchlist from
        with_alerts (bool): whether to enable alerts
    """
    if feed_name:
        feed = get_feed(cb, feed_name=feed_name)
        create_watchlist(feed, enable_alerts=with_alerts)
    elif feed_base_name:
        feeds = get_feed(cb, feed_name=feed_name, return_all=True)
        for feed in feeds:
            create_watchlist(feed, enable_alerts=with_alerts)
    else:
        print("Either feed base name or feed name needs to be provided")
