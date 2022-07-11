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
    feed_id: str,
    replace: bool,
) -> None:
    """Create reports and add the iocs to the reports.

    If replace is True - replace all of the reports in a feed.
    If replace is False, then append - so fill any reports with iocs < IOCS_BATCH_SIZE and create additional reports,
        if needed.
    If the iocs are >= IOCS_BATCH_SIZE, then create multiple reports.
    If the number of reports are >= REPORTS_BATCH_SIZE, then raise an error, this will not create addtional feeds.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        iocs (list): list of iocs
        severity (int): The severity of the Report
        feed_id (str): id of an existing feed to be used for the import
        replace (bool): Replacing the existing Reports in the Feed, if false it will append the results

    Raises:
        ObjectNotFoundError: Whenever a Feed as not Found
        SystemExit: If there is an Error within the function
    """
    reports = []
    counter_r = 1
    start, end = 0, 0

    try:
        feed = get_feed(cb, feed_id=feed_id)
    except ObjectNotFoundError:
        logger.error(f"Feed was not found with id: {feed_id}")
        raise SystemExit(1)

    iocs_list = []

    # if we need to append the iocs instead of replacing, then first fill any existing reports
    # with iocs count less than IOCS_BATCH_SIZE
    if not replace:
        for item in feed.reports:
            if item.iocs_total_count < IOCS_BATCH_SIZE:
                start, end = end, end + (IOCS_BATCH_SIZE - item.iocs_total_count)
                iocs_list = iocs[start:end]

                if not iocs_list:
                    # if there are no more new iocs to be added, but still iocs_total_count < IOCS_BATCH_SIZE
                    # then just add the report
                    reports.append(item)
                else:
                    # create a new report with the existing iocs + new ones up to IOCS_BATCH_SIZE
                    report = create_report(cb, feed, counter_r, severity, iocs_list, item.iocs_v2)
                    reports.append(report)
            else:
                # if the report is full (IOCS_BATCH_SIZE iocs) just added it as is.
                reports.append(item)
            counter_r += 1

    # make the reports with batches of iocs per IOCS_BATCH_SIZE or less
    # do not allow the report count to be > REPORTS_BATCH_SIZE
    # if replace = False and if there are still iocs to be added, create new reports for them
    # if replace = True, then add all the iocs as new reports and replace the existing reports with the new ones
    while counter_r <= REPORTS_BATCH_SIZE:
        if counter_r != 1 and not iocs_list:
            # we have exhausted all the iocs, so break the loop
            break

        # if case we need to replace all the reports or just create more reports as part of the append procedure
        start, end = end, end + IOCS_BATCH_SIZE
        iocs_list = iocs[start:end]

        if iocs_list:
            report = create_report(cb, feed, counter_r, severity, iocs_list)
            reports.append(report)
            counter_r += 1
    else:
        logger.info("The feed is full, it is possible that not all iocs are imported.")

    # add reports to the current feed
    feed.replace_reports(reports)


def create_report(
    cb: CBCloudAPI, feed: Feed, number_of_report: int, severity: int, new_iocs: List[IOC_V2], existing_iocs: int = None
) -> Report:
    """Create reports and add the iocs to the reports.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        feed (Feed): Feed to which the report will be added
        number_of_report (int): The current report number
        severity (int): The severity of the Report
        new_iocs (list): List of the new iocs that needs to be added
        existing_iocs (list): (optional) List of existing iocs

    Returns:
        Report: The created report

    """
    # use the builder so that the data is properly formed
    builder = Report.create(cb, f"Report {feed.name}", feed.summary, severity)
    report_data = builder._report_body

    # add the iocs
    report_data["iocs_v2"] = existing_iocs if existing_iocs else []
    [report_data["iocs_v2"].append(ioc._info) for ioc in new_iocs]

    # add id for the report, because the builder is not include it
    report_data["id"] = str(uuid.uuid4())

    # create a report with all the data
    report = Report(cb, initial_data=report_data, feed_id=feed.id)
    report.save()
    return report
