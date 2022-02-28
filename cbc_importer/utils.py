# -*- coding: utf-8 -*-

# *******************************************************
# Copyright (c) VMware, Inc. 2020-2021. All Rights Reserved.
# SPDX-License-Identifier: MIT
# *******************************************************
# *
# * DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# * WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# * EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# * WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

"""CBC Helpers"""
from typing import List, Union

import arrow
import validators
from cbc_sdk import CBCloudAPI
from cbc_sdk.enterprise_edr import Feed, Report, Watchlist
from cbc_sdk.errors import (
    InvalidObjectError,
    MoreThanOneResultError,
    ObjectNotFoundError,
)
from typer import BadParameter

"""Feed Helpers"""


def create_feed(
    cb: CBCloudAPI,
    name: str,
    provider_url: str,
    summary: str,
    category: str,
    reports: List[Report] = None,
) -> Feed:
    """Create new feed.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        name (str): Name for the new feed.
        provider_url (str): Provider URL for the new feed.
        summary (str): Summary for the new feed.
        category (str): Category for the new feed.
        reports ([Report]) (optional): List of Reports to add to this Feed.

    Returns:
        Feed: The new Feed.
    """
    builder = Feed.create(cb, name, provider_url, summary, category)
    if reports:
        builder.add_reports(reports)
    feed = builder.build()
    return feed.save()


def get_feed(
    cb: CBCloudAPI, feed_name: str = None, feed_id: str = None, return_all: bool = False
) -> Union[Feed, List[Feed]]:
    """Return Feed by providing either feed name or feed id.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        feed_name (str): Feed name
        feed_id (str): Feed id
        return_all (bool): (optional, default False) return all feeds that start with specific name

    Returns:
        Feed: The found feed.

    Raises:
        ObjectNotFoundError: if there is no such feed
        MoreThanOneResultError: if more than one feed is found that fulfils the criteria
        ValueError: neither feed_name nor feed_id is provided
    """
    if feed_id:
        return cb.select(Feed, feed_id)
    elif feed_name:
        if return_all:
            # if all feeds with specific base name are needed
            return [feed for feed in cb.select(Feed) if feed.name.startswith(feed_name)]

        # otherwise, check for feed with specific name
        feeds = [feed for feed in cb.select(Feed) if feed.name == feed_name]

        if not feeds:
            raise ObjectNotFoundError("No feeds named '{}'".format(feed_name))
        elif len(feeds) > 1:
            raise MoreThanOneResultError("More than one feed named '{}'".format(feed_name))
        return feeds[0]
    else:
        raise ValueError("expected either feed_id or feed_name")


"""Watchlist Helpers"""


def create_watchlist(
    feed: Feed,
    name: str = None,
    description: str = None,
    enable_alerts: bool = False,
) -> Watchlist:
    """Create watchlist from feed

    Args:
        feed (Feed): feed
        name (str): (optional) name to be used for the watchlist, if not provided the feed name will be used
        description (str): (optional) description to be used for the watchlist, if not provided the feed
                           description will be used
        enable_alerts (bool): whether to generate alert upon hits

    Returns:
        Watchlist: The new watchlist.
    """
    if feed and isinstance(feed, Feed):
        watchlist = Watchlist.create_from_feed(feed, name=name, description=description, enable_alerts=enable_alerts)
        return watchlist.save()
    raise InvalidObjectError("invalid Feed")


def validate_provider_url(value: str) -> str:
    """Validate if a str is valid URL

    Args:
        value (str): url value

    Raises:
        BadParameter: Whenever the value is not a valid URL

    Returns:
        str: Valid URL
    """
    if validators.domain(value) or validators.url(value):
        return value
    raise BadParameter("Provider URL is not a valid URL")


def validate_severity(value: int) -> int:
    """Validating the severity

    Args:
        value (int): Severity integer

    Raises:
        BadParameter: Whenever an integer is not between 1-10

    Returns:
        int: int between 1-10
    """
    if 1 <= value <= 10:
        return value
    raise BadParameter("Severity must be between 1-10")


def transform_date(value: str) -> arrow.Arrow:
    """Transform a str date to Arrow object

    Args:
        value (str): The date as a string

    Raises:
        arrow.ParserError: Whenever the provided date is not valid.

    Returns:
        arrow.Arrow: Arrow object of that date
    """
    date = arrow.get(value).replace(tzinfo="UTC")
    return date.datetime
