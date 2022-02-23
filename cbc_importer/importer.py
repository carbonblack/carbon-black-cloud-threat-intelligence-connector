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
import uuid
from typing import List
import logging

from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2, Feed, Report
from cbc_sdk.errors import ObjectNotFoundError

from cbc_importer.utils import create_feed, create_watchlist, get_feed

logger = logging.getLogger(__name__)

# Constants for the batch sizes of reports and iocs
IOCS_BATCH_SIZE = 1000
REPORTS_BATCH_SIZE = 10000


def process_iocs(
    cb: CBCloudAPI,
    iocs: List[IOC_V2],
    feed_base_name: str,
    stix_version: str,
    start_date: str,
    end_date: str,
    provider_url: str,
    summary: str,
    category: str,
    severity: int,
    feed_id: str = None,
) -> List[Feed]:
    """Create reports and add the iocs to the reports.

    If the iocs are >= IOCS_BATCH_SIZE, then create multiple reports.
    If the number of reports are >= REPORTS_BATCH_SIZE, then create multiple feeds.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        iocs (list): list of iocs
        feed_base_name (str): The base name of the feeds
        stix_version (str): the stix version
        start_date (str): the start date
        end_date (str): the end date
        provider_url (str): Provider URL for the new feed.
        summary (str): Summary for the new feed.
        category (str): Category for the new feed.
        severity (int): severity for the reports
        feed_id (str): (optional) id of an existing feed to be used for the import
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

    start, end = 0, IOCS_BATCH_SIZE

    while counter_f <= num_feeds:
        reports = []
        feed_name = f"{feed_base_name} ({stix_version}) {start_date} to {end_date} - Part {counter_f}"
        iocs_list = iocs[start:end]

        # edge case when the number of iocs is divisible by IOCS_BATCH_SIZE * REPORTS_BATCH_SIZE
        if iocs_list:
            try:
                # if feed_id is provided, use the existing feed, but only for the first feed
                # if more feeds are needed, they will be created using the default logic
                if feed_id is not None and counter_f == 1:
                    feed = get_feed(cb, feed_id=feed_id)
                    logger.info(f"Using existing feed with name: {feed.name}")
                else:
                    feed = create_feed(cb, name=feed_name, provider_url=provider_url, summary=summary, category=category)
                    logger.info(f"Feed was created with name: {feed.name}")
            except ObjectNotFoundError:
                feed = create_feed(cb, name=feed_name, provider_url=provider_url, summary=summary, category=category)
                logger.info(f"Feed was created with name: {feed.name}")

            # make the reports with batches of iocs per IOCS_BATCH_SIZE or less
            while counter_r <= min(num_reports, counter_f * REPORTS_BATCH_SIZE):
                iocs_list = iocs[start:end]
                start, end = end, end + IOCS_BATCH_SIZE
                counter_r += 1

                # check for the edge case where we have iocs divisible by IOCS_BATCH_SIZE
                # in that case there will be one-off error
                if iocs_list:
                    # use the builder so that the data is properly formed
                    builder = Report.create(cb, f"Report {feed.name}-{counter_r - 1}", feed.summary, severity)
                    report_data = builder._report_body
                    # add the iocs
                    report_data["iocs_v2"] = []
                    [report_data["iocs_v2"].append(ioc._info) for ioc in iocs_list]

                    # add id for the report, because the builder is not include it
                    report_data["id"] = str(uuid.uuid4())

                    # create a report with all the data
                    report = Report(cb, initial_data=report_data, feed_id=feed.id)
                    report.save()

                    # finally, add the report to the list to be added in the current feed
                    reports.append(report)

            # add reports to the current feed
            feed.replace_reports(reports)
            # add the created feed
            feeds.append(feed)

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
        feeds = get_feed(cb, feed_name=feed_base_name, return_all=True)
        for feed in feeds:
            create_watchlist(feed, enable_alerts=with_alerts)
    else:
        raise Exception("Either feed base name or feed name needs to be provided")
