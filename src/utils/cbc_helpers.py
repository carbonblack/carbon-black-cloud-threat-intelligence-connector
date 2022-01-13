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
from cbc_sdk.enterprise_edr import Feed, Watchlist
from cbc_sdk.errors import ObjectNotFoundError, MoreThanOneResultError

"""Feed Helpers"""


def create_feed(cb, name, provider_url, summary, category, reports=None):
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


def get_feed(cb, feed_name=None, feed_id=None):
    """Return Feed by providing either feed name or feed id.

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        feed_name (str): Feed name
        feed_id (str): Feed id

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
        feeds = [feed for feed in cb.select(Feed) if feed.name == feed_name]

        if not feeds:
            raise ObjectNotFoundError("No feeds named '{}'".format(feed_name))
        elif len(feeds) > 1:
            raise MoreThanOneResultError(
                "More than one feed named '{}'".format(feed_name)
            )
        return feeds[0]
    else:
        raise ValueError("expected either feed_id or feed_name")


"""Watchlist Helpers"""


def create_watchlist(cb, feed, name=None, description=None, enable_alerts=False):
    """Create watchlist from feed

    Args:
        cb (CBCloudAPI): A reference to the CBCloudAPI object.
        feed (Feed): feed
        name (str): (optional) name to be used for the watchlist, if not provided the feed name will be used
        description (str): (optional) description to be used for the watchlist, if not provided the feed
                           description will be used
        enable_alerts (bool): whether to generate alert upon hits

    Returns:
        Watchlist: The new watchlist.
    """
    watchlist = Watchlist.create_from_feed(
        feed, name=name, description=description, enable_alerts=enable_alerts
    )
    return watchlist.save()
