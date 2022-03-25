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
import logging
import uuid
from typing import List

from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr.threat_intelligence import IOC_V2, Feed, Report
from cbc_sdk.errors import ObjectNotFoundError

from cbc_importer.utils import get_feed

logger = logging.getLogger(__name__)

# Constants for the batch sizes of reports and IOCs
IOCS_BATCH_SIZE = 1000
REPORTS_BATCH_SIZE = 10000


def process_iocs(
    cb: CBCloudAPI,
    iocs: List[IOC_V2],
    severity: int,
    replace: bool,
    feed_id: str,
) -> List[Feed]:
    """Create reports and add the iocs to the reports.

    If the iocs are >= IOCS_BATCH_SIZE, then create multiple reports.
    If the number of reports are >= REPORTS_BATCH_SIZE, then create multiple feeds.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        iocs (list): list of iocs
        severity (int): The severity of the Report
        replace (bool): Replacing the existing Reports in the Feed, if false it will append the results
        feed_id (str): id of an existing feed to be used for the import

    Returns:
        list(Feed): list of feeds created as part of the import
    """
    num_iocs = len(iocs)
    num_reports = num_iocs // IOCS_BATCH_SIZE + 1
    counter_r = 1
    feeds = []

    start, end = 0, IOCS_BATCH_SIZE

    reports = []
    iocs_list = iocs[start:end]

    # edge case when the number of iocs is divisible by IOCS_BATCH_SIZE * REPORTS_BATCH_SIZE
    if replace:
        if iocs_list:
            try:
                # if feed_id is provided, use the existing feed, but only for the first feed
                # if more feeds are needed, they will be created using the default logic
                feed = get_feed(cb, feed_id=feed_id)
            except ObjectNotFoundError:
                logger.error(f"Feed was not found with id: {feed_id}")
                raise SystemExit(1)

            # make the reports with batches of iocs per IOCS_BATCH_SIZE or less
            while counter_r <= min(num_reports, REPORTS_BATCH_SIZE):
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
    else:
        pass

    return feeds
